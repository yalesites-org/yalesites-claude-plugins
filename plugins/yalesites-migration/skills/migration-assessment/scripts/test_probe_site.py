#!/usr/bin/env python3
"""Unit tests for probe_site.py's pure parsing helpers.

Network-free by design: every test feeds fixture strings to a helper.

    python3 test_probe_site.py

CI runs this via `scripts/run-skill-tests.sh`, which also asserts the tests were
actually collected. See SKILL.md for why `unittest discover` is not used.
"""

import os
import sys
import unittest

# The script under test is a sibling file, not an installed package -- skill
# directories deliberately ship no `__init__.py` (see SKILL.md). Static analysers
# cannot follow a runtime path insert, hence the import suppression.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import probe_site as p  # noqa: E402  # pyright: ignore[reportMissingImports]


class FingerprintTest(unittest.TestCase):
    def test_detects_modern_drupal_from_headers(self):
        result = p.fingerprint(
            headers={"X-Generator": "Drupal 10 (https://www.drupal.org)"},
            html="<html></html>",
            probes={},
        )
        self.assertEqual(result["cms"], "Drupal")
        self.assertEqual(result["major"], "10")
        self.assertTrue(any("X-Generator" in e for e in result["evidence"]))

    def test_detects_drupal_7_from_legacy_asset_paths(self):
        html = '<script src="/misc/drupal.js?v=7.98"></script>'
        result = p.fingerprint(headers={}, html=html, probes={})
        self.assertEqual(result["cms"], "Drupal")
        self.assertEqual(result["major"], "7")

    def test_core_misc_path_means_drupal_8_plus(self):
        html = '<script src="/core/misc/drupal.js?v=10.3.1"></script>'
        result = p.fingerprint(headers={}, html=html, probes={})
        self.assertEqual(result["cms"], "Drupal")
        self.assertEqual(result["major"], "8+")

    def test_jsonapi_probe_is_recorded_as_evidence(self):
        result = p.fingerprint(
            headers={"X-Drupal-Dynamic-Cache": "MISS"},
            html="<html></html>",
            probes={"/jsonapi": 200},
        )
        self.assertEqual(result["cms"], "Drupal")
        self.assertIn("/jsonapi", " ".join(result["evidence"]))
        self.assertTrue(result["jsonapi_open"])

    def test_unknown_cms_when_nothing_matches(self):
        result = p.fingerprint(headers={}, html="<html><body>hi</body></html>", probes={})
        self.assertEqual(result["cms"], "unknown")
        self.assertIsNone(result["major"])


class SitemapTest(unittest.TestCase):
    URLSET = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://example.edu/</loc></url>
      <url><loc>https://example.edu/news/first-post</loc></url>
      <url><loc>https://example.edu/news/second-post</loc></url>
    </urlset>"""

    INDEX = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <sitemap><loc>https://example.edu/sitemap.xml?page=1</loc></sitemap>
      <sitemap><loc>https://example.edu/sitemap.xml?page=2</loc></sitemap>
    </sitemapindex>"""

    def test_parses_urlset(self):
        parsed = p.parse_sitemap(self.URLSET)
        self.assertEqual(parsed["kind"], "urlset")
        self.assertEqual(len(parsed["urls"]), 3)
        self.assertIn("https://example.edu/news/first-post", parsed["urls"])
        self.assertEqual(parsed["sitemaps"], [])

    def test_parses_sitemap_index(self):
        parsed = p.parse_sitemap(self.INDEX)
        self.assertEqual(parsed["kind"], "sitemapindex")
        self.assertEqual(len(parsed["sitemaps"]), 2)
        self.assertEqual(parsed["urls"], [])

    def test_malformed_xml_returns_empty_rather_than_raising(self):
        parsed = p.parse_sitemap("<urlset><url><loc>oops")
        self.assertEqual(parsed["kind"], "unparseable")
        self.assertEqual(parsed["urls"], [])

    def test_entity_declarations_are_refused_not_expanded(self):
        billion_laughs = (
            '<?xml version="1.0"?>'
            '<!DOCTYPE urlset [<!ENTITY a "aaaaaaaaaa">]>'
            "<urlset><url><loc>&a;</loc></url></urlset>"
        )
        parsed = p.parse_sitemap(billion_laughs)
        self.assertEqual(parsed["kind"], "rejected-doctype")
        self.assertEqual(parsed["urls"], [])

    def test_sitemaps_from_robots(self):
        robots = (
            "User-agent: *\n"
            "Disallow: /admin\n"
            "Sitemap: https://example.edu/sitemap.xml\n"
            "sitemap: https://example.edu/sitemap_index.xml\n"
        )
        found = p.sitemaps_from_robots(robots)
        self.assertEqual(
            found,
            [
                "https://example.edu/sitemap.xml",
                "https://example.edu/sitemap_index.xml",
            ],
        )


class BucketTest(unittest.TestCase):
    def test_buckets_by_first_path_segment_and_sorts_by_count(self):
        urls = [
            "https://example.edu/",
            "https://example.edu/news/a",
            "https://example.edu/news/b",
            "https://example.edu/news/c",
            "https://example.edu/events/x",
            "https://example.edu/about",
        ]
        buckets = p.bucket_paths(urls)
        self.assertEqual(buckets[0]["prefix"], "/news")
        self.assertEqual(buckets[0]["count"], 3)
        prefixes = [b["prefix"] for b in buckets]
        self.assertIn("/events", prefixes)
        self.assertIn("/(root)", prefixes)
        self.assertLessEqual(len(buckets[0]["examples"]), 3)

    def test_depth_histogram_counts_path_segments(self):
        urls = [
            "https://example.edu/a",
            "https://example.edu/a/b",
            "https://example.edu/a/b/c",
            "https://example.edu/a/b/d",
        ]
        self.assertEqual(p.depth_histogram(urls), {1: 1, 2: 1, 3: 2})


class CrawlableLinksTest(unittest.TestCase):
    """Sites with no sitemap.xml still have to be inventoried (Drupal 7 rarely
    ships one), so the crawl fallback's link filter is load-bearing."""

    HTML = """
    <a href="/about">About</a>
    <a href="/about#staff">About anchor</a>
    <a href="/news?page=2">Paged</a>
    <a href="https://accessibility.yale.edu/contacts">Absolute same host</a>
    <a href="https://www.yale.edu/">Other host</a>
    <a href="/files/policy.pdf">PDF</a>
    <a href="mailto:someone@yale.edu">Mail</a>
    <a href="tel:+12035551212">Phone</a>
    <a href="/admin/content">Admin</a>
    <a href="/user/login">Login</a>
    """

    def test_keeps_same_host_html_links_only(self):
        links = p.crawlable_links(self.HTML, "https://accessibility.yale.edu/", ["/admin/"])
        self.assertIn("https://accessibility.yale.edu/about", links)
        self.assertIn("https://accessibility.yale.edu/contacts", links)
        for rejected in (
            "https://www.yale.edu/",
            "https://accessibility.yale.edu/files/policy.pdf",
            "mailto:someone@yale.edu",
            "tel:+12035551212",
            "https://accessibility.yale.edu/admin/content",
        ):
            self.assertNotIn(rejected, links)

    def test_drops_fragments_and_query_strings_and_dedupes(self):
        links = p.crawlable_links(self.HTML, "https://accessibility.yale.edu/", [])
        self.assertEqual(links.count("https://accessibility.yale.edu/about"), 1)
        self.assertNotIn("https://accessibility.yale.edu/news?page=2", links)
        self.assertIn("https://accessibility.yale.edu/news", links)

    def test_skips_authentication_paths_even_when_robots_allows_them(self):
        links = p.crawlable_links(self.HTML, "https://accessibility.yale.edu/", [])
        self.assertNotIn("https://accessibility.yale.edu/user/login", links)

    def test_skips_cas_and_saml_entry_points(self):
        # Yale sites expose /cas; fetching it renders a sign-in page, which is
        # an authentication surface an assessment has no business touching.
        html = '<a href="/cas">Sign in</a><a href="/saml/login">SSO</a><a href="/ok">ok</a>'
        links = p.crawlable_links(html, "https://accessibility.yale.edu/", [])
        self.assertEqual(links, ["https://accessibility.yale.edu/ok"])

    def test_rejects_aggregated_css_and_js_assets(self):
        # Drupal 7 puts aggregated assets under /sites/default/files, which is
        # not robots-disallowed. Crawling one and then sampling it produced a
        # phantom "book" content type from CSS selectors in the file.
        html = (
            '<link rel="stylesheet" href="/sites/default/files/css/css_059Bx.css">'
            '<script src="/sites/default/files/js/js_2Arx.js"></script>'
            '<a href="/sites/default/files/css/css_4p66.css">stray link</a>'
        )
        self.assertEqual(p.crawlable_links(html, "https://accessibility.yale.edu/", []), [])

    def test_rejects_paths_that_are_not_plausible_urls(self):
        html = '<a href="/&amp;">broken</a><a href="/real-page">fine</a>'
        links = p.crawlable_links(html, "https://accessibility.yale.edu/", [])
        self.assertEqual(links, ["https://accessibility.yale.edu/real-page"])


class CrawlInventoryTest(unittest.TestCase):
    class _StubFetcher:
        """Serves fixture pages as text/html, matching what the crawl requires.

        The Content-Type matters: `crawl_inventory` refuses to parse a response
        that is not HTML, so a stub with no headers silently exercises the
        skip path instead of the crawl.
        """

        def __init__(self, pages, content_type="text/html; charset=utf-8"):
            self.pages = pages
            self.asked = []
            self.content_type = content_type

        def get(self, url, cache=True, status_only=False):
            self.asked.append(url)
            body = self.pages.get(url, "")
            headers = {"Content-Type": self.content_type}
            return (200 if body else 404), headers, body

    def test_homepage_is_not_double_counted(self):
        home_html = '<a href="/">Home</a><a href="/about">About</a>'
        fetcher = self._StubFetcher({"https://example.edu/about": "<a href='/'>Home</a>"})
        result = p.crawl_inventory(fetcher, "https://example.edu", home_html, [], 5, 100)
        self.assertEqual(result["urls"].count("https://example.edu/"), 1)
        self.assertEqual(
            sorted(result["urls"]), ["https://example.edu/", "https://example.edu/about"]
        )

    def test_reports_what_the_filters_excluded(self):
        # Exclusion accounting was only wired to the sitemap path, so it read as
        # empty on exactly the sites that use the crawl (Drupal 7, no sitemap).
        home_html = (
            '<a href="/about">About</a>'
            '<a href="/user/login">Login</a>'
            '<a href="/css/app.css">CSS</a>'
            '<a href="https://elsewhere.edu/x">Off host</a>'
        )
        fetcher = self._StubFetcher({"https://example.edu/about": '<a href="/admin/x">Admin</a>'})
        result = p.crawl_inventory(fetcher, "https://example.edu", home_html, [], 5, 100)
        self.assertEqual(result["urls"], ["https://example.edu/", "https://example.edu/about"])
        self.assertEqual(result["excluded"]["never_crawl"], 2)
        self.assertEqual(result["excluded"]["non_page_extension"], 1)
        self.assertEqual(result["excluded"]["off_host"], 1)

    def test_a_non_html_response_is_counted_and_never_parsed(self):
        home_html = '<a href="/aggregate">Asset route</a>'
        fetcher = self._StubFetcher(
            {"https://example.edu/aggregate": ".node-type-book{color:red}"},
            content_type="text/css",
        )
        result = p.crawl_inventory(fetcher, "https://example.edu", home_html, [], 5, 100)
        self.assertEqual(result["non_html_skipped"], 1)
        self.assertEqual(result["urls"], ["https://example.edu/", "https://example.edu/aggregate"])

    def test_respects_the_fetch_budget(self):
        home_html = "".join(f'<a href="/p{i}">{i}</a>' for i in range(10))
        fetcher = self._StubFetcher({f"https://example.edu/p{i}": "<p>x</p>" for i in range(10)})
        result = p.crawl_inventory(fetcher, "https://example.edu", home_html, [], 3, 100)
        self.assertEqual(result["pages_crawled"], 3)
        self.assertEqual(len(fetcher.asked), 3)
        self.assertEqual(result["frontier_remaining"], 7)


class NavTest(unittest.TestCase):
    HTML = """
    <html><body>
      <nav class="menu--main" role="navigation">
        <ul>
          <li><a href="/campus-access">Campus Access</a>
            <ul>
              <li><a href="/campus-access/parking">Parking</a></li>
              <li><a href="/campus-access/shuttles">Shuttles</a></li>
            </ul>
          </li>
          <li><a href="/accommodations">Accommodations</a></li>
        </ul>
      </nav>
      <nav class="menu--footer"><ul><li><a href="/privacy">Privacy</a></li></ul></nav>
    </body></html>
    """

    def test_prefers_the_main_menu_nav(self):
        nav = p.extract_nav(self.HTML)
        self.assertIn("menu--main", nav["container"])
        labels = [i["label"] for i in nav["items"]]
        self.assertEqual(labels[0], "Campus Access")
        self.assertIn("Accommodations", labels)
        self.assertNotIn("Privacy", labels)

    def test_records_depth_so_subnavigation_is_visible(self):
        nav = p.extract_nav(self.HTML)
        by_label = {i["label"]: i for i in nav["items"]}
        self.assertEqual(by_label["Campus Access"]["depth"], 0)
        self.assertEqual(by_label["Parking"]["depth"], 1)
        self.assertEqual(nav["max_depth"], 1)
        self.assertEqual(nav["top_level_count"], 2)

    def test_no_nav_element_yields_empty_result(self):
        nav = p.extract_nav("<html><body><p>no nav here</p></body></html>")
        self.assertEqual(nav["items"], [])
        self.assertIsNone(nav["container"])


class PageSignalsTest(unittest.TestCase):
    def test_reads_drupal_node_type_from_body_classes(self):
        html = '<body class="page-node-type-post node--full">x</body>'
        sig = p.page_signals(html, "https://example.edu/news/a")
        self.assertEqual(sig["node_type"], "post")

    def test_reads_drupal_7_node_type_from_body_classes(self):
        # Drupal 7 emits `node-type-page`; only Drupal 8+ emits
        # `page-node-type-page` / `node--type-page`. Missing the D7 form means
        # every page on a D7 source site classifies as an unknown type.
        html = '<body class="html front page-node node-type-page one-sidebar">x</body>'
        sig = p.page_signals(html, "https://example.edu/")
        self.assertEqual(sig["node_type"], "page")

    def test_reads_the_canonical_url_so_alias_duplicates_can_be_collapsed(self):
        html = '<link rel="canonical" href="https://example.edu/welcome" />'
        sig = p.page_signals(html, "https://example.edu/node/1")
        self.assertEqual(sig["canonical"], "https://example.edu/welcome")

    def test_canonical_is_none_when_absent(self):
        self.assertIsNone(p.page_signals("<p>x</p>", "https://example.edu/x")["canonical"])

    def test_detects_carousel_library_from_asset_name(self):
        html = '<link rel="stylesheet" href="/libraries/slick/slick.css">'
        sig = p.page_signals(html, "https://example.edu/")
        self.assertIn("slick", sig["carousel_libraries"])

    def test_collects_iframe_hosts_and_flags_external_form_vendors(self):
        html = (
            '<iframe src="https://cm.maxient.com/reportingform.php?Yale"></iframe>'
            '<iframe src="https://www.youtube.com/embed/abc"></iframe>'
        )
        sig = p.page_signals(html, "https://example.edu/report")
        self.assertIn("cm.maxient.com", sig["iframe_hosts"])
        self.assertIn("maxient", sig["external_form_vendors"])
        self.assertIn("youtube", sig["embedded_media"])

    def test_detects_native_drupal_form_with_form_id(self):
        html = (
            '<form action="/form/contact" method="post">'
            '<input type="hidden" name="form_id" value="webform_submission_contact_form">'
            "</form>"
        )
        sig = p.page_signals(html, "https://example.edu/contact")
        self.assertEqual(len(sig["forms"]), 1)
        self.assertEqual(sig["forms"][0]["form_id"], "webform_submission_contact_form")
        self.assertTrue(sig["has_webform"])

    def test_search_form_is_reported_and_left_for_the_rollup_to_classify(self):
        html = (
            '<form action="/search" method="get" class="search-block-form">'
            '<input type="hidden" name="form_id" value="search_block_form">'
            "</form>"
        )
        sig = p.page_signals(html, "https://example.edu/")
        self.assertEqual(len(sig["forms"]), 1)
        self.assertEqual(sig["forms"][0]["fingerprint"], "search_block_form")

    def test_a_webform_whose_name_contains_search_is_not_suppressed(self):
        # Name-matching `search` dropped a real course-search webform from
        # has_webform -- the single most consequential field in the report.
        html = (
            '<form action="/form/course-search" method="post">'
            '<input type="hidden" name="form_id" value="webform_submission_course_search_form">'
            "</form>"
        )
        sig = p.page_signals(html, "https://example.edu/courses")
        self.assertTrue(sig["has_webform"])
        self.assertEqual(len(sig["forms"]), 1)

    def test_has_webform_is_true_even_when_the_form_is_filtered_out(self):
        # The login safety filter must not be able to hide a webform finding.
        html = (
            '<form class="user-login-form" method="post">'
            '<input type="hidden" name="form_id" value="webform_submission_login">'
            "</form>"
        )
        sig = p.page_signals(html, "https://example.edu/x")
        self.assertEqual(sig["forms"], [])
        self.assertTrue(sig["has_webform"])

    def test_sign_in_form_is_not_counted_as_a_content_form(self):
        html = (
            '<form action="login" method="post" class="sign-in-form">'
            '<input type="password" name="password">'
            "</form>"
        )
        self.assertEqual(p.page_signals(html, "https://example.edu/cas")["forms"], [])

    def test_counts_inline_styles_and_pdf_links(self):
        html = (
            "<style>.a{color:red}</style>"
            '<p style="color: blue">hi</p>'
            '<a href="/files/policy.pdf">Policy</a>'
            '<a href="/files/guide.PDF">Guide</a>'
        )
        sig = p.page_signals(html, "https://example.edu/")
        self.assertEqual(sig["inline_style_blocks"], 1)
        self.assertEqual(sig["inline_style_attrs"], 1)
        self.assertEqual(sig["pdf_link_count"], 2)

    def test_third_party_scripts_exclude_the_site_host(self):
        html = (
            '<script src="/core/misc/drupal.js"></script>'
            '<script src="https://example.edu/local.js"></script>'
            '<script src="https://www.googletagmanager.com/gtm.js"></script>'
        )
        sig = p.page_signals(html, "https://example.edu/")
        self.assertEqual(sig["third_party_script_hosts"], ["www.googletagmanager.com"])

    def test_detects_hero_and_interactive_patterns(self):
        html = (
            '<div class="hero-banner"><img src="/h.jpg" alt=""></div>'
            '<div class="accordion"><button aria-expanded="false">More</button></div>'
            '<div role="tablist"></div>'
        )
        sig = p.page_signals(html, "https://example.edu/")
        self.assertTrue(sig["has_hero"])
        self.assertIn("accordion", sig["interactive_patterns"])
        self.assertIn("tabs", sig["interactive_patterns"])

    def test_a_layout_table_is_not_reported_as_an_interactive_feature(self):
        sig = p.page_signals('<table role="presentation"><tr><td>x</td></tr></table>', "https://e.edu/")
        self.assertEqual(sig["table_count"], 1)
        self.assertFalse(sig["has_data_table"])
        self.assertNotIn("data_table", sig["interactive_patterns"])

    def test_a_real_data_table_is_flagged(self):
        sig = p.page_signals("<table><tr><th>Year</th></tr></table>", "https://e.edu/")
        self.assertTrue(sig["has_data_table"])

    def test_prose_about_a_carousel_is_a_hint_not_a_detected_library(self):
        # `\bcarousel\b` on prose reported a library on the platform's most
        # contested gap. Asset-path evidence and markup hints are now separate.
        sig = p.page_signals("<p>We removed the carousel last year.</p>", "https://e.edu/")
        self.assertEqual(sig["carousel_libraries"], [])
        self.assertEqual(sig["carousel_markup_hints"], [])

    def test_a_carousel_class_is_a_markup_hint(self):
        sig = p.page_signals('<div class="carousel slide">x</div>', "https://e.edu/")
        self.assertEqual(sig["carousel_libraries"], [])
        self.assertIn("carousel-class", sig["carousel_markup_hints"])

    def test_owl_carousel_reports_once_not_three_times(self):
        html = '<script src="/libraries/owl-carousel/owl.carousel.min.js"></script>'
        self.assertEqual(p.page_signals(html, "https://e.edu/")["carousel_libraries"], ["owl-carousel"])


class ClassifyTest(unittest.TestCase):
    def test_explicit_node_type_wins(self):
        self.assertEqual(p.classify_page({"node_type": "post"})["bucket"], "post")
        self.assertEqual(p.classify_page({"node_type": "profile"})["bucket"], "profile")

    def test_unknown_source_node_type_is_reported_not_guessed(self):
        result = p.classify_page({"node_type": "spotlight"})
        self.assertEqual(result["bucket"], "unmapped")
        self.assertEqual(result["source_type"], "spotlight")

    def test_falls_back_to_heuristics_when_no_node_type(self):
        listing = p.classify_page({"node_type": None, "views_rows": 12})
        self.assertEqual(listing["bucket"], "listing")
        dated = p.classify_page({"node_type": None, "time_elements": 1, "has_byline": True})
        self.assertEqual(dated["bucket"], "post")
        plain = p.classify_page({"node_type": None})
        self.assertEqual(plain["bucket"], "page")

    def test_every_mapped_source_type_lands_in_a_known_bucket(self):
        known = {"page", "post", "event", "profile", "resource", "listing"}
        self.assertEqual(set(p.SOURCE_TYPE_MAP.values()) - known, set())

    def test_classification_always_reports_its_basis(self):
        for signals in ({"node_type": "post"}, {"node_type": "spotlight"},
                        {"views_rows": 12}, {"time_elements": 1, "has_byline": True}, {}):
            self.assertTrue(p.classify_page(signals)["basis"])


class InventoryBoundaryTest(unittest.TestCase):
    """The filters used to live only inside the link scraper, so a sitemap that
    listed an admin route or an asset bypassed every one of them -- including the
    safety rule. They now sit at the inventory boundary, shared by both sources."""

    def test_sitemap_urls_get_the_same_rules_as_crawled_ones(self):
        result = p.filter_inventory(
            [
                "https://ex.edu/about",
                "https://ex.edu/user/login",
                "https://ex.edu/css/style.css",
                "https://ex.edu/files/report.pdf",
                "https://other.edu/x",
            ],
            "https://ex.edu",
            [],
        )
        self.assertEqual(result["urls"], ["https://ex.edu/about"])
        self.assertEqual(result["excluded"]["never_crawl"], 1)
        self.assertEqual(result["excluded"]["non_page_extension"], 2)
        self.assertEqual(result["excluded"]["off_host"], 1)

    def test_every_drop_is_counted_so_an_overfiring_rule_is_visible(self):
        result = p.filter_inventory(
            ["https://ex.edu/ok", "https://ex.edu/admin/x"], "https://ex.edu", []
        )
        self.assertEqual(sum(result["excluded"].values()), 1)
        self.assertIn("never_crawl", result["excluded"])

    def test_real_pages_with_unusual_characters_are_kept(self):
        # An allow-list regex silently deleted these, undercounting the site
        # with no trace in the output.
        urls = [
            "https://ex.edu/café-menu",
            "https://ex.edu/about-us-(history)",
            "https://ex.edu/news/2024@yale",
            "https://ex.edu/中文",
        ]
        result = p.filter_inventory(urls, "https://ex.edu", [])
        self.assertEqual(len(result["urls"]), 4)
        self.assertEqual(result["excluded"], {})

    def test_a_genuinely_malformed_path_is_still_dropped(self):
        result = p.filter_inventory(["https://ex.edu/&"], "https://ex.edu", [])
        self.assertEqual(result["urls"], [])
        self.assertEqual(result["excluded"]["malformed_path"], 1)


class RobotsMatcherTest(unittest.TestCase):
    """Wildcard Disallow rules are the common Drupal idiom. They used to be
    filtered out of enforcement, making the module's compliance claim false."""

    def test_wildcard_rules_are_honoured(self):
        matchers = p.robots_matchers(["/*/print", "/*?", "/private"])
        result = p.filter_inventory(
            ["https://ex.edu/news/print", "https://ex.edu/private/x", "https://ex.edu/news"],
            "https://ex.edu",
            ["/*/print", "/*?", "/private"],
        )
        self.assertEqual(result["urls"], ["https://ex.edu/news"])
        self.assertEqual(result["excluded"]["robots_disallow"], 2)
        self.assertEqual(len(matchers), 3)

    def test_dollar_anchors_the_end(self):
        result = p.filter_inventory(
            ["https://ex.edu/report", "https://ex.edu/report/sub"], "https://ex.edu", ["/report$"]
        )
        self.assertEqual(result["urls"], ["https://ex.edu/report/sub"])

    def test_plain_prefix_rules_still_work(self):
        result = p.filter_inventory(
            ["https://ex.edu/blocked/x", "https://ex.edu/ok"], "https://ex.edu", ["/blocked"]
        )
        self.assertEqual(result["urls"], ["https://ex.edu/ok"])


class HtmlResponseGateTest(unittest.TestCase):
    """Running the HTML parser over a non-HTML body is the root cause of the
    phantom content type; the server states the type, so ask it."""

    def test_html_content_types_pass(self):
        self.assertTrue(p.is_html_response({"Content-Type": "text/html; charset=utf-8"}))
        self.assertTrue(p.is_html_response({"content-type": "application/xhtml+xml"}))

    def test_non_html_content_types_are_refused(self):
        for value in ("text/css", "application/javascript", "application/json", "text/plain"):
            self.assertFalse(p.is_html_response({"Content-Type": value}), value)

    def test_a_missing_content_type_is_refused(self):
        self.assertFalse(p.is_html_response({}))


class FormClassificationTest(unittest.TestCase):
    """Chrome vs content is decided by how many sampled pages carry a form --
    evidence the tool already collects -- not by matching form names."""

    @staticmethod
    def _page(url, html):
        signals = p.page_signals(html, url)
        return {"url": url, "signals": signals, "classification": p.classify_page(signals)}

    SEARCH = (
        '<form action="/search" class="search-block-form">'
        '<input type="hidden" name="form_id" value="search_block_form"></form>'
    )
    CONTACT = (
        '<form action="/form/contact" method="post">'
        '<input type="hidden" name="form_id" value="webform_submission_contact"></form>'
    )

    def test_a_form_on_every_page_is_chrome(self):
        pages = [self._page(f"https://e.edu/p{i}", self.SEARCH) for i in range(5)]
        result = p.classify_forms(pages)
        self.assertEqual([f["form_id"] for f in result["chrome"]], ["search_block_form"])
        self.assertEqual(result["content"], [])

    def test_a_form_on_one_page_is_content(self):
        pages = [self._page(f"https://e.edu/p{i}", self.SEARCH) for i in range(5)]
        pages.append(self._page("https://e.edu/contact", self.SEARCH + self.CONTACT))
        result = p.classify_forms(pages)
        self.assertEqual([f["form_id"] for f in result["content"]], ["webform_submission_contact"])
        self.assertEqual([f["form_id"] for f in result["chrome"]], ["search_block_form"])

    def test_summary_keeps_the_classification_basis(self):
        pages = [self._page("https://e.edu/", '<body class="node-type-page">x</body>')]
        summary = p.summarise(pages)
        self.assertEqual(summary["buckets"], {"page": 1})
        self.assertEqual(summary["buckets_by_basis"], {"page": {"source node type": 1}})

    def test_a_defaulted_bucket_is_distinguishable_from_a_typed_one(self):
        pages = [
            self._page("https://e.edu/a", '<body class="node-type-page">x</body>'),
            self._page("https://e.edu/b", "<body>no type here</body>"),
        ]
        summary = p.summarise(pages)
        self.assertEqual(summary["buckets"], {"page": 2})
        self.assertEqual(
            summary["buckets_by_basis"], {"page": {"source node type": 1, "default": 1}}
        )


class ChooseSampleTest(unittest.TestCase):
    def test_spreads_across_prefixes_before_going_deep(self):
        urls = [f"https://e.edu/news/{i}" for i in range(5)] + ["https://e.edu/about"]
        sample = p.choose_sample(urls, 2)
        self.assertEqual(len(sample), 2)
        self.assertEqual({p._prefix(u) for u in sample}, {"/news", "/about"})

    def test_respects_the_limit_and_uses_the_shared_prefix_rule(self):
        urls = [f"https://e.edu/s{i}/page" for i in range(10)]
        self.assertEqual(len(p.choose_sample(urls, 4)), 4)
        self.assertEqual(p._prefix("https://e.edu/"), "/(root)")


class SafeFetchTargetTest(unittest.TestCase):
    """The source site controls `Sitemap:` lines and `Location:` headers. Those
    are the two inputs that reach the fetcher without passing the URL filter,
    and both were confirmed to allow scheme and host control -- including a
    local `file://` read."""

    def test_only_http_and_https_targets_are_fetchable(self):
        for url in (
            "file:///etc/passwd",
            "ftp://internal.example/x",
            "gopher://internal.example/1",
            "data:text/html,<b>x</b>",
        ):
            self.assertFalse(p.is_fetchable(url, "ex.edu"), url)

    def test_off_host_targets_are_refused(self):
        self.assertFalse(p.is_fetchable("http://169.254.169.254/latest/meta-data/", "ex.edu"))
        self.assertFalse(p.is_fetchable("http://127.0.0.1:9921/internal", "ex.edu"))
        self.assertTrue(p.is_fetchable("https://ex.edu/sitemap.xml", "ex.edu"))

    def test_declared_sitemaps_are_filtered_before_any_fetch(self):
        robots = (
            "User-agent: *\n"
            "Sitemap: file:///Users/someone/.ssh/id_rsa\n"
            "Sitemap: http://169.254.169.254/latest/meta-data/\n"
            "Sitemap: https://ex.edu/sitemap.xml\n"
        )
        declared = p.sitemaps_from_robots(robots)
        self.assertEqual(len(declared), 3)
        safe = [u for u in declared if p.is_fetchable(u, "ex.edu")]
        self.assertEqual(safe, ["https://ex.edu/sitemap.xml"])

    def test_the_default_opener_is_not_used_so_file_and_ftp_have_no_handler(self):
        handlers = {type(h).__name__ for h in p.build_safe_opener().handlers}
        self.assertNotIn("FileHandler", handlers)
        self.assertNotIn("FTPHandler", handlers)
        self.assertNotIn("DataHandler", handlers)
        self.assertIn("_RefuseRedirects", handlers)


class RedirectPolicyTest(unittest.TestCase):
    def test_an_on_host_redirect_is_allowed(self):
        self.assertTrue(p.redirect_allowed("https://ex.edu/a", "https://ex.edu/b", "ex.edu"))

    def test_an_off_host_redirect_is_refused(self):
        self.assertFalse(
            p.redirect_allowed("https://ex.edu/a", "http://169.254.169.254/", "ex.edu")
        )

    def test_a_redirect_to_an_account_route_is_refused(self):
        # An access-controlled Drupal page 302s to /user/login?destination=...
        self.assertFalse(
            p.redirect_allowed("https://ex.edu/private", "https://ex.edu/user/login", "ex.edu")
        )

    def test_a_redirect_to_a_non_http_scheme_is_refused(self):
        self.assertFalse(p.redirect_allowed("https://ex.edu/a", "file:///etc/passwd", "ex.edu"))


class FingerprintProbeTargetTest(unittest.TestCase):
    def test_no_probe_path_is_an_account_route(self):
        # /user/login was probed on every run, breaking the tool's own
        # "never touch an admin or account route" rule.
        for path in p.FINGERPRINT_PATHS:
            self.assertIsNone(p.NEVER_CRAWL.match(path), path)

    def test_probe_paths_disallowed_by_robots_are_reported_not_fetched(self):
        # Stock Drupal robots.txt disallows /CHANGELOG.txt.
        matchers = p.robots_matchers(["/CHANGELOG.txt"])
        self.assertTrue(any(m.match("/CHANGELOG.txt") for m in matchers))
        self.assertFalse(any(m.match("/jsonapi") for m in matchers))


class BaseUrlTest(unittest.TestCase):
    def test_a_base_url_with_a_path_is_rejected(self):
        # Every safety pattern is anchored at ^/, so a base path prefix would
        # silently disable NEVER_CRAWL and every robots rule.
        self.assertIsNotNone(p.base_url_problem("https://ex.edu/dept"))
        self.assertIsNone(p.base_url_problem("https://ex.edu"))
        self.assertIsNone(p.base_url_problem("https://ex.edu/"))

    def test_duplicate_slashes_cannot_smuggle_past_never_crawl(self):
        result = p.filter_inventory(["https://ex.edu//user/login"], "https://ex.edu", [])
        self.assertEqual(result["urls"], [])
        self.assertEqual(result["excluded"]["never_crawl"], 1)


class RobotsGroupingTest(unittest.TestCase):
    def test_a_star_group_listing_several_agents_still_applies(self):
        robots = (
            "User-agent: *\n"
            "User-agent: Googlebot\n"
            "Disallow: /private/\n"
        )
        self.assertIn("/private/", p.disallowed_prefixes(robots))

    def test_a_group_without_the_star_is_ignored(self):
        robots = "User-agent: Googlebot\nDisallow: /only-google/\n"
        self.assertEqual(p.disallowed_prefixes(robots), [])

    def test_a_new_group_after_rules_resets_the_star(self):
        robots = (
            "User-agent: *\n"
            "Disallow: /shared/\n"
            "User-agent: Bingbot\n"
            "Disallow: /bing-only/\n"
        )
        self.assertEqual(p.disallowed_prefixes(robots), ["/shared/"])


class ChromeFormThresholdTest(unittest.TestCase):
    @staticmethod
    def _page(url, html):
        signals = p.page_signals(html, url)
        return {"url": url, "signals": signals, "classification": p.classify_page(signals)}

    FORM = (
        '<form action="/form/apply" method="post">'
        '<input type="hidden" name="form_id" value="webform_submission_apply"></form>'
    )

    def test_two_of_three_pages_is_content_not_chrome(self):
        # round() truncated the 80% requirement to 67% at three pages, which is
        # the misclassification that hid a real webform.
        pages = [self._page("https://e.edu/a", self.FORM), self._page("https://e.edu/b", self.FORM),
                 self._page("https://e.edu/c", "<p>none</p>")]
        result = p.classify_forms(pages)
        self.assertEqual([f["form_id"] for f in result["content"]], ["webform_submission_apply"])
        self.assertEqual(result["chrome"], [])

    def test_three_of_three_pages_is_chrome(self):
        pages = [self._page(f"https://e.edu/{i}", self.FORM) for i in range(3)]
        result = p.classify_forms(pages)
        self.assertEqual([f["form_id"] for f in result["chrome"]], ["webform_submission_apply"])


class RelativeLinkBaseTest(unittest.TestCase):
    class _StubFetcher:
        def __init__(self, pages):
            self.pages = pages
            self.asked = []

        def get(self, url, cache=True, status_only=False):
            self.asked.append(url)
            body = self.pages.get(url, "")
            return (200 if body else 404), {"Content-Type": "text/html"}, body

    def test_relative_hrefs_resolve_against_the_page_they_came_from(self):
        # Resolving against the homepage invented URLs that 404 and never found
        # the real children -- on exactly the no-sitemap sites the crawl is for.
        fetcher = self._StubFetcher(
            {
                "https://ex.edu/dept/about": '<a href="staff">Staff</a>',
                "https://ex.edu/dept/staff": "<p>ok</p>",
            }
        )
        result = p.crawl_inventory(
            fetcher, "https://ex.edu", '<a href="/dept/about">About</a>', [], 5, 100
        )
        self.assertIn("https://ex.edu/dept/staff", result["urls"])
        self.assertNotIn("https://ex.edu/staff", result["urls"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
