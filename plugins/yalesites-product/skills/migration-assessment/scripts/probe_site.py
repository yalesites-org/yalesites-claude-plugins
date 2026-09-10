#!/usr/bin/env python3
"""Collect a read-only migration-assessment inventory for a public Drupal site.

This script does the mechanical gathering for a YaleSites migration assessment:
it fingerprints the source CMS, enumerates URLs (from the sitemap, or by a
bounded link crawl when there is none), reads the main navigation, samples a
spread of pages, and reports the signals that decide how cleanly a site can move
onto YaleSites. It emits one JSON document on stdout.

It carries exactly one piece of interpretation -- `SOURCE_TYPE_MAP`, the source
content type vocabulary, used to bucket a sampled page. Every classification
reports the `basis` it was decided on, and `summary.buckets_by_basis` keeps
defaulted pages distinguishable from pages typed off real markup, so a guess can
never be quoted as a measurement. Everything else -- the field-level mapping,
the effort rating, the mechanism options -- lives in SKILL.md and the reference
docs, which are authoritative for the target model.

Read-only and public by construction: GET only, no cookies, no auth, no form
submission. `robots.txt` Disallow rules -- including wildcard rules -- are
honoured, and account/admin/SSO routes are never fetched whether robots
mentions them or not. Requests are sequential with a delay between them.

    python3 probe_site.py https://example.edu --sample 12 > probe.json

Standard library only, so it runs anywhere python3 does.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser

USER_AGENT = "YaleSites-migration-assessment (read-only; +https://yalesites.yale.edu)"
HTTP_OK = 200

# A form fingerprint appearing on at least this share of sampled pages is site
# chrome (search, newsletter, donate), not content the site owner authored.
CHROME_FORM_SHARE = 0.8

# Fingerprint probes: path -> what a 200 tells us. Deliberately excludes
# `/user/login`: it matches NEVER_CRAWL, so probing it broke the tool's own
# "never touch an account route" rule on every single run. The remaining paths
# plus the response headers identify Drupal perfectly well, and each is still
# checked against robots.txt before being fetched.
FINGERPRINT_PATHS = ("/jsonapi", "/CHANGELOG.txt", "/core/CHANGELOG.txt")

# Front-end carousel/slider libraries, matched on asset paths and initialiser
# names. YaleSites has no carousel component, so this is one of the highest-value
# findings -- which is exactly why it is kept separate from the weaker markup
# hints below. Patterns are matched against lowercased markup, so keep them lower.
CAROUSEL_LIBRARIES = {
    "slick": r"\bslick\b",
    "swiper": r"\bswiper\b",
    "splide": r"\bsplide\b",
    "owl-carousel": r"owl[-_.]?carousel",
    "flexslider": r"\bflexslider\b",
    "bxslider": r"\bbxslider\b",
    "tiny-slider": r"tiny[-_.]?slider|\btns\b",
    "glide": r"\bglidejs\b|glide\.min",
}

# Weaker evidence: a bare `carousel`/`slider` class or word. Reported separately
# because it also matches prose ("we removed the carousel") and the class names
# a named library already accounts for.
CAROUSEL_MARKUP_HINTS = {
    "carousel-class": r"class=[\"'][^\"']*\bcarousel\b",
    "slider-class": r"class=[\"'][^\"']*\bslider\b",
    "slideshow-class": r"class=[\"'][^\"']*\bslideshow\b",
}

# Externally hosted form vendors. These migrate as-is (a link or an embed), so
# finding one is good news -- it is a native Drupal form that is not.
EXTERNAL_FORM_VENDORS = {
    "maxient": r"maxient",
    "servicenow": r"service-now|servicenow",
    "qualtrics": r"qualtrics",
    "google-forms": r"docs\.google\.com/forms",
    "formstack": r"formstack",
    "jotform": r"jotform",
    "smartsheet": r"smartsheet",
    "wufoo": r"wufoo",
    "microsoft-forms": r"forms\.(office|microsoft)\.com",
}

EMBEDDED_MEDIA = {
    "youtube": r"youtube|youtu\.be",
    "vimeo": r"vimeo",
    "panopto": r"panopto",
    "soundcloud": r"soundcloud",
    "spotify": r"spotify",
    "arcgis": r"arcgis",
    "tableau": r"tableau",
    "kaltura": r"kaltura",
}

# Patterns implying JavaScript behaviour. Deliberately excludes tables -- a
# `<table>` is markup, not an interactive feature, and `basic_html` permits
# tables anyway; table signals are reported separately.
INTERACTIVE_PATTERNS = {
    "accordion": r"class=[\"'][^\"']*\baccordion\b|data-accordion",
    "tabs": r"role=[\"']tablist|class=[\"'][^\"']*\btabs?\b",
    "modal": r"role=[\"']dialog|class=[\"'][^\"']*\b(modal|dialog)\b",
    "map": r"google\.com/maps|mapbox|leaflet",
    "faceted_search": r"class=[\"'][^\"']*\b(facet|facets|views-exposed-form)\b",
    "gated_content": r"login-required|paywall|class=[\"'][^\"']*\bprotected\b",
}

# Source content-type machine names seen on Yale Drupal sites, mapped to the
# bucket the assessment reasons about. Anything absent is reported as
# "unmapped" rather than guessed -- an unrecognised type is a finding, and each
# one needs an explicit product decision.
#
# THIS IS THE ONLY HOME for this vocabulary. `references/yalesites-target-model.md`
# points here rather than restating it, so there is one place to extend. Add a
# regression test alongside any addition.
SOURCE_TYPE_MAP = {
    "page": "page",
    "basic_page": "page",
    "landing_page": "page",
    "faq": "page",
    "article": "post",
    "post": "post",
    "news": "post",
    "news_item": "post",
    "blog": "post",
    "blog_post": "post",
    "story": "post",
    "announcement": "post",
    "press_release": "post",
    "event": "event",
    "events": "event",
    "person": "profile",
    "profile": "profile",
    "people": "profile",
    "staff": "profile",
    "staff_profile": "profile",
    "bio": "profile",
    "faculty": "profile",
    "resource": "resource",
    "publication": "resource",
    "document": "resource",
    "report": "resource",
    "view": "listing",
    "views": "listing",
}

# File extensions that are documents or assets rather than pages. This is a
# cheap PRE-fetch hint that avoids spending a request on a 200 MB video -- it is
# NOT the arbiter of "is this a page." That decision is made after the fetch,
# from the response Content-Type (see `is_html_response`).
NON_PAGE_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".csv",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
    ".mp3", ".mp4", ".mov", ".ics", ".xml", ".rss", ".json", ".txt",
    ".css", ".js",
)

# Never fetch these, whether or not robots.txt mentions them: they are account,
# admin, SSO, or system routes. This is a safety invariant of the tool, so it
# must not depend on the source site cooperating.
NEVER_CRAWL = re.compile(
    r"^/(user|users|admin|node/add|comment|login|logout|cron|update|install|filter/tips"
    r"|cas|caslogin|saml|saml_login|sso|shibboleth|Shibboleth\.sso)(/|$)",
    re.I,
)

# Reject only genuinely invalid paths -- control characters, or characters that
# must have been percent-encoded and were not (a malformed `href` yields `/&`).
# Deliberately NOT an allow-list: a charset allow-list silently deletes real
# pages such as `/cafe-menu` with an accent, `/about-us-(history)`, or a
# non-Latin slug, and a silent undercount corrupts the effort estimate with no
# trace in the output.
INVALID_PATH = re.compile(r"[\x00-\x20\x7f<>\"{}|\\^`]|&(?![A-Za-z]+;|#\d+;)")


# --------------------------------------------------------------------------
# Pure parsing helpers (unit-tested in test_probe_site.py -- no network here)
# --------------------------------------------------------------------------


def _lower_headers(headers: dict) -> dict:
    return {str(k).lower(): v for k, v in (headers or {}).items()}


def _normalised_path(parsed) -> str:
    """Collapse duplicate slashes so `//user/login` cannot slip past `^/` rules."""
    return re.sub(r"/{2,}", "/", parsed.path or "/")


def is_fetchable(url: str, base_host: str) -> bool:
    """Whether a URL may be requested at all.

    Applies to the two inputs that reach the fetcher without going through
    `url_verdict`: `Sitemap:` lines in the probed site's robots.txt, and
    `Location:` headers. Both are fully source-controlled, and without this the
    source site chooses the scheme and host -- which allowed a `file://` read
    and requests to internal hosts.
    """
    try:
        parsed = urllib.parse.urlparse(url or "")
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and parsed.netloc == base_host


def redirect_allowed(from_url: str, to_url: str, base_host: str) -> bool:
    """Whether a redirect may be followed.

    urllib follows 3xx to any host by default, and nothing re-checked the
    target -- so a filter-approved page could redirect to an internal service
    (or to `/user/login`) and have its content parsed into the report.
    """
    target = urllib.parse.urljoin(from_url, to_url or "")
    if not is_fetchable(target, base_host):
        return False
    return not NEVER_CRAWL.match(_normalised_path(urllib.parse.urlparse(target)))


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect automatically; the caller validates each hop."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_safe_opener():
    """An opener that can only speak HTTP(S) and never auto-redirects.

    Built explicitly rather than via `build_opener`, so `FileHandler`,
    `FTPHandler`, and `DataHandler` are simply absent: a non-HTTP scheme has no
    handler and fails, instead of relying on a scheme check alone.
    """
    opener = urllib.request.OpenerDirector()
    for handler in (
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(),
        urllib.request.HTTPDefaultErrorHandler(),
        urllib.request.HTTPErrorProcessor(),
        _RefuseRedirects(),
    ):
        opener.add_handler(handler)
    return opener


def base_url_problem(base_url: str):
    """Why this base URL cannot be probed safely, or None.

    Every safety and robots pattern is anchored at `^/`, so a base URL carrying
    a path prefix would silently disable all of them.
    """
    parsed = urllib.parse.urlparse(base_url or "")
    if parsed.scheme not in ("http", "https"):
        return "url must start with http:// or https://"
    if not parsed.netloc:
        return "url has no host"
    if (parsed.path or "/").rstrip("/"):
        return (
            "url must be a bare site root (no path). Safety and robots.txt rules "
            "are anchored at the site root, so a path prefix would disable them."
        )
    if parsed.query or parsed.fragment:
        return "url must not carry a query string or fragment"
    return None


def is_html_response(headers: dict) -> bool:
    """Whether a response body should be parsed as a page.

    The root cause of the worst false positive this tool has had -- an
    aggregated CSS file inventoried as a page, whose selectors then reported a
    phantom content type and phantom carousel libraries -- was running an HTML
    parser over a non-HTML body. The server states the type; ask it, rather than
    inferring from the URL, which misses every extensionless asset and feed route.
    """
    content_type = _lower_headers(headers).get("content-type", "")
    return "text/html" in content_type or "application/xhtml" in content_type


def fingerprint(headers: dict, html: str, probes: dict) -> dict:
    """Identify the source CMS and, where possible, its major version."""
    hdrs = _lower_headers(headers)
    probes = probes or {}
    evidence: list[str] = []
    major = None
    is_drupal = False

    generator = hdrs.get("x-generator", "")
    meta = re.search(
        r'<meta[^>]+name=["\']Generator["\'][^>]+content=["\']([^"\']+)', html or "", re.I
    )
    sources = (("X-Generator header", generator), ("meta Generator", meta.group(1) if meta else ""))
    for source, value in sources:
        version = re.search(r"Drupal\s*(\d+)", value or "", re.I)
        if version:
            is_drupal = True
            major = version.group(1)
            evidence.append(f"{source}: {value.strip()}")

    for header in ("x-drupal-cache", "x-drupal-dynamic-cache"):
        if header in hdrs:
            is_drupal = True
            evidence.append(f"{header} header present: {hdrs[header]}")

    if re.search(r"/core/misc/drupal\.js", html or ""):
        is_drupal = True
        major = major or "8+"
        evidence.append("/core/misc/drupal.js in markup (Drupal 8 or newer layout)")
    elif re.search(r"(?<!/core)/misc/drupal\.js", html or ""):
        is_drupal = True
        major = major or "7"
        evidence.append("/misc/drupal.js in markup (Drupal 7 layout)")

    if re.search(r"/sites/default/files/(css|js)/(css|js)_", html or ""):
        is_drupal = True
        evidence.append("aggregated /sites/default/files asset paths")

    jsonapi_open = probes.get("/jsonapi") == HTTP_OK
    for path, status in sorted(probes.items()):
        if status == HTTP_OK:
            evidence.append(f"{path} returned 200")
            if path in ("/jsonapi", "/core/CHANGELOG.txt"):
                is_drupal = True
                major = major or "8+"
            elif path == "/CHANGELOG.txt":
                is_drupal = True
        elif status:
            evidence.append(f"{path} returned {status}")

    return {
        "cms": "Drupal" if is_drupal else "unknown",
        "major": major,
        "jsonapi_open": jsonapi_open,
        "evidence": evidence,
    }


def _localname(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def parse_sitemap(xml_text: str) -> dict:
    """Parse a sitemap or sitemap index. Never raises on bad input.

    The source site is untrusted, and the stdlib XML parser will happily expand
    internally-defined entities (the "billion laughs" amplification). defusedxml
    is not in the standard library and this script takes no dependencies, so
    documents carrying a DOCTYPE or ENTITY declaration are refused outright --
    a real sitemap has neither.
    """
    text = (xml_text or "").strip()
    if re.search(r"<!\s*(DOCTYPE|ENTITY)", text, re.I):
        return {"kind": "rejected-doctype", "urls": [], "sitemaps": []}
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return {"kind": "unparseable", "urls": [], "sitemaps": []}

    kind = _localname(root.tag)
    urls, sitemaps = [], []
    for element in root.iter():
        if _localname(element.tag) != "loc":
            continue
        loc = (element.text or "").strip()
        if not loc:
            continue
        (sitemaps if kind == "sitemapindex" else urls).append(loc)
    return {"kind": kind, "urls": urls, "sitemaps": sitemaps}


def sitemaps_from_robots(robots_text: str) -> list:
    """Sitemap: lines from robots.txt, in file order."""
    found = []
    for line in (robots_text or "").splitlines():
        match = re.match(r"\s*sitemap\s*:\s*(\S+)", line, re.I)
        if match and match.group(1) not in found:
            found.append(match.group(1))
    return found


def disallowed_prefixes(robots_text: str) -> list:
    """Disallow paths from the wildcard user-agent group, in file order."""
    # Consecutive User-agent lines form ONE group, so the `*` flag must stay
    # sticky until a rule line ends the agent list. Resetting it per line
    # discarded rules from a `User-agent: *` + `User-agent: Googlebot` group.
    prefixes: list = []
    in_star = False
    collecting_agents = False
    for line in (robots_text or "").splitlines():
        agent = re.match(r"\s*user-agent\s*:\s*(\S+)", line, re.I)
        if agent:
            if not collecting_agents:
                in_star = False
                collecting_agents = True
            in_star = in_star or agent.group(1) == "*"
            continue
        rule = re.match(r"\s*disallow\s*:\s*(\S*)", line, re.I)
        if rule:
            collecting_agents = False
            if in_star and rule.group(1) and rule.group(1) not in prefixes:
                prefixes.append(rule.group(1))
    return prefixes


def robots_matchers(patterns) -> list:
    """Compile robots.txt Disallow patterns, honouring `*` and `$`.

    Wildcards are the common Drupal idiom (`Disallow: /*/print`, `Disallow: /*?`).
    Skipping those rules rather than translating them would make the module's
    "robots.txt Disallow rules are honoured" claim false exactly where site
    owners rely on it.
    """
    compiled = []
    for pattern in patterns or []:
        if not pattern:
            continue
        anchored_end = pattern.endswith("$")
        body = pattern[:-1] if anchored_end else pattern
        regex = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
        compiled.append(re.compile("^" + regex + ("$" if anchored_end else "")))
    return compiled


def url_verdict(url: str, base_host: str, matchers: list) -> tuple:
    """Whether a URL belongs in the inventory, and if not, which rule dropped it.

    Applied at the inventory boundary so BOTH inventory sources -- the sitemap
    and the link crawl -- get the same rules. Keeping these checks inside the
    link scraper meant a sitemap that listed `/user/login` or an aggregated CSS
    file bypassed every one of them, including the safety rule.

    Returns `(normalised_url_or_None, reason)`; reason is "keep" when kept.
    """
    if not url or url.startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
        return None, "not_a_page_link"
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None, "off_scheme"
    if parsed.netloc != base_host:
        return None, "off_host"
    path = _normalised_path(parsed)
    if INVALID_PATH.search(path):
        return None, "malformed_path"
    if path.lower().endswith(NON_PAGE_EXTENSIONS):
        return None, "non_page_extension"
    if NEVER_CRAWL.match(path):
        return None, "never_crawl"
    if any(matcher.match(path) for matcher in matchers):
        return None, "robots_disallow"
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", "")), "keep"


def filter_inventory(urls, base_url: str, blocked) -> dict:
    """Apply `url_verdict` to a URL list, counting what each rule dropped.

    Silent filtering is the failure mode this exists to prevent: a rule that
    over-fires would otherwise shrink the page count -- the number an effort
    estimate rests on -- leaving no trace in the output.
    """
    base_host = urllib.parse.urlparse(base_url).netloc
    matchers = robots_matchers(blocked)
    kept, excluded = [], Counter()
    for url in urls:
        normalised, reason = url_verdict(url, base_host, matchers)
        if normalised is None:
            excluded[reason] += 1
        elif normalised not in kept:
            kept.append(normalised)
    return {"urls": kept, "excluded": dict(excluded)}


def scan_links(html: str, base_url: str, blocked: list) -> dict:
    """Filter a page's links for the inventory, keeping the exclusion counts."""
    hrefs = [urllib.parse.urljoin(base_url, h) for h in _attr_values(html, "href")]
    return filter_inventory(hrefs, base_url, blocked)


def crawlable_links(html: str, base_url: str, blocked: list) -> list:
    """Same-host page links worth adding to a crawl inventory, in document order."""
    return scan_links(html, base_url, blocked)["urls"]


def _segments(url: str) -> list:
    path = urllib.parse.urlparse(url).path
    return [s for s in path.split("/") if s]


def _prefix(url: str) -> str:
    """The first path segment, which is the axis both reporting and sampling use."""
    segments = _segments(url)
    return f"/{segments[0]}" if segments else "/(root)"


def group_by_prefix(urls) -> dict:
    """Group URLs by first path segment. Shared so reporting and sampling agree."""
    grouped: dict[str, list] = {}
    for url in urls:
        grouped.setdefault(_prefix(url), []).append(url)
    return grouped


def bucket_paths(urls: list) -> list:
    """Group URLs by first path segment, most populous first."""
    buckets = [
        {"prefix": prefix, "count": len(members), "examples": sorted(members)[:3]}
        for prefix, members in group_by_prefix(urls).items()
    ]
    buckets.sort(key=lambda b: (-b["count"], b["prefix"]))
    return buckets


def depth_histogram(urls: list) -> dict:
    """How deep the URL tree goes -- a proxy for sub-navigation depth."""
    return dict(Counter(len(_segments(url)) for url in urls))


class _NavParser(HTMLParser):
    """Collect anchors inside every <nav>, tagged with their list nesting depth."""

    MAIN_HINT = re.compile(r"menu--main|main-menu|main_menu|primary|main-nav|nav-main", re.I)

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.navs: list[dict] = []
        self._stack: list[dict] = []
        self._anchor = None

    def _identity(self, attrs: dict) -> str:
        parts = ["nav"]
        if attrs.get("class"):
            parts.append("." + ".".join(attrs["class"].split()))
        if attrs.get("id"):
            parts.append(f"#{attrs['id']}")
        if attrs.get("role"):
            parts.append(f"[role={attrs['role']}]")
        return "".join(parts)

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v or "") for k, v in attrs}
        if tag == "nav":
            self._stack.append({"container": self._identity(attrs), "items": [], "list_depth": 0})
            return
        if not self._stack:
            return
        current = self._stack[-1]
        if tag in ("ul", "ol"):
            current["list_depth"] += 1
        elif tag == "a":
            self._anchor = {
                "label": "",
                "href": attrs.get("href", ""),
                "depth": max(current["list_depth"] - 1, 0),
            }

    def handle_endtag(self, tag):
        if not self._stack:
            return
        current = self._stack[-1]
        if tag == "a" and self._anchor is not None:
            label = " ".join(self._anchor["label"].split())
            if label:
                self._anchor["label"] = label
                current["items"].append(self._anchor)
            self._anchor = None
        elif tag in ("ul", "ol"):
            current["list_depth"] = max(current["list_depth"] - 1, 0)
        elif tag == "nav":
            self.navs.append(self._stack.pop())

    def handle_data(self, data):
        if self._anchor is not None:
            self._anchor["label"] += data

    def best(self) -> dict:
        candidates = [n for n in self.navs if n["items"]]
        if not candidates:
            return {"container": None, "items": []}
        hinted = [n for n in candidates if self.MAIN_HINT.search(n["container"])]
        return max(hinted or candidates, key=lambda n: len(n["items"]))


def extract_nav(html: str) -> dict:
    """Best-guess main navigation: labels, hrefs, and nesting depth."""
    parser = _NavParser()
    try:
        parser.feed(html or "")
    except Exception:  # malformed markup should degrade, not abort the probe
        pass
    best = parser.best()
    items = best["items"]
    return {
        "container": best["container"],
        "items": items,
        "top_level_count": sum(1 for i in items if i["depth"] == 0),
        "max_depth": max((i["depth"] for i in items), default=0),
        "other_navs": [n["container"] for n in parser.navs if n is not best and n["items"]],
    }


def _strip_tags(fragment: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", fragment or "").split())


def _attr_values(html: str, attr: str) -> list:
    """Every value of an attribute, in document order."""
    return re.findall(rf"\b{attr}=[\"']([^\"']+)", html or "", re.I)


def _tag_srcs(html: str, tag: str) -> list:
    return re.findall(rf"<{tag}\b[^>]*\bsrc=[\"']([^\"']+)", html or "", re.I)


def _hosts(srcs, base_url: str) -> list:
    hosts = set()
    for src in srcs:
        host = urllib.parse.urlparse(urllib.parse.urljoin(base_url, src)).netloc
        if host:
            hosts.add(host)
    return sorted(hosts)


def _matched_keys(patterns: dict, lowered_haystack: str) -> list:
    """Which pattern keys match. Haystack must already be lowercased.

    Lowercasing once and dropping `re.IGNORECASE` is a ~2.5x speedup on
    `page_signals`: the flag forces per-character case folding on every one of
    these scans, and there are four tables' worth.
    """
    return [key for key, pattern in patterns.items() if re.search(pattern, lowered_haystack)]


def _forms(html: str) -> tuple:
    """Every form on the page with a stable fingerprint, plus a webform flag.

    Deliberately does NOT filter out search or newsletter forms. Deciding
    chrome-vs-content by matching names dropped `webform_submission_course_search_form`
    -- a real content form -- from the single most consequential field in the
    report. Frequency across sampled pages is the honest test, and only
    `summarise()` can see that. Login forms are dropped here, as a safety rule
    rather than a classification rule.
    """
    forms, webform_seen = [], False
    for block in re.findall(r"<form\b(.*?)</form>", html or "", re.I | re.S):
        opening = block.split(">", 1)[0]
        form_id_match = re.search(
            r"name=[\"']form_id[\"'][^>]*value=[\"']([^\"']+)", block, re.I
        )
        form_id = form_id_match.group(1) if form_id_match else ""
        class_match = re.search(r"class=[\"']([^\"']*)", opening, re.I)
        classes = class_match.group(1) if class_match else ""
        action_match = re.search(r"action=[\"']([^\"']*)", opening, re.I)
        method_match = re.search(r"method=[\"']([^\"']*)", opening, re.I)
        action = action_match.group(1) if action_match else ""

        if form_id.startswith("webform"):
            webform_seen = True

        if re.search(r"sign[-_]?in|log[-_]?in|user_login|user-login", form_id + " " + classes, re.I):
            continue

        forms.append(
            {
                "form_id": form_id,
                "action": action,
                "method": (method_match.group(1) if method_match else "get").lower(),
                "classes": classes,
                # What makes "the same form" the same across pages.
                "fingerprint": form_id or f"{action}|{classes}",
            }
        )
    return forms, webform_seen


def page_signals(html: str, url: str) -> dict:
    """Everything one sampled page can tell us, with no interpretation applied."""
    html = html or ""
    low = html.lower()
    site_host = urllib.parse.urlparse(url).netloc

    body_class_match = re.search(r"<body\b[^>]*\bclass=[\"']([^\"']*)", low)
    body_classes = body_class_match.group(1).split() if body_class_match else []

    node_type = None
    # Drupal 8+ emits `page-node-type-x` on <body> and `node--type-x` on the
    # node wrapper; Drupal 7 emits `node-type-x`. Three genuinely distinct
    # upstream conventions, all resolving to the same capture, so any match is
    # authoritative and the order is safe.
    for pattern in (
        r"page-node-type-([a-z0-9_-]+)",
        r"node--type-([a-z0-9_-]+)",
        r"node-type-([a-z0-9_-]+)",
    ):
        match = re.search(pattern, low)
        if match:
            node_type = match.group(1).replace("-", "_")
            break

    title_match = re.search(r"<title\b[^>]*>(.*?)</title>", html, re.I | re.S)
    h1_match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    canonical_match = re.search(
        r"<link\b[^>]*\brel=[\"']canonical[\"'][^>]*\bhref=[\"']([^\"']+)", html, re.I
    )

    hrefs = _attr_values(html, "href")
    iframe_srcs = _tag_srcs(html, "iframe")
    link_haystack = " ".join(hrefs + iframe_srcs).lower()

    forms, has_webform = _forms(html)
    table_count = low.count("<table")

    return {
        "url": url,
        "title": _strip_tags(title_match.group(1)) if title_match else "",
        "h1": _strip_tags(h1_match.group(1)) if h1_match else "",
        "canonical": canonical_match.group(1) if canonical_match else None,
        "body_classes": body_classes,
        "node_type": node_type,
        "image_count": low.count("<img"),
        "has_hero": bool(re.search(r"class=[\"'][^\"']*(hero|banner|masthead)", low)),
        "carousel_libraries": _matched_keys(CAROUSEL_LIBRARIES, low),
        "carousel_markup_hints": _matched_keys(CAROUSEL_MARKUP_HINTS, low),
        "iframe_hosts": _hosts(iframe_srcs, url),
        "external_form_vendors": _matched_keys(EXTERNAL_FORM_VENDORS, link_haystack),
        "embedded_media": _matched_keys(EMBEDDED_MEDIA, link_haystack),
        "forms": forms,
        "has_webform": has_webform,
        "exposed_filter_forms": len(re.findall(r"views[_-]exposed[_-]form", low)),
        "interactive_patterns": _matched_keys(INTERACTIVE_PATTERNS, low),
        "table_count": table_count,
        "has_data_table": bool(table_count and re.search(r"<th\b|role=[\"']grid", low)),
        "inline_style_blocks": low.count("<style"),
        "inline_style_attrs": len(re.findall(r"\sstyle=[\"']", low)),
        "pdf_link_count": sum(1 for h in hrefs if re.search(r"\.pdf(\?|#|$)", h, re.I)),
        "third_party_script_hosts": [
            host for host in _hosts(_tag_srcs(html, "script"), url) if host != site_host
        ],
        "time_elements": low.count("<time"),
        "has_byline": bool(re.search(r"class=[\"'][^\"']*(byline|submitted|author)", low)),
        "views_rows": low.count("views-row"),
        "approx_word_count": len(
            _strip_tags(re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)).split()
        ),
    }


def classify_page(signals: dict) -> dict:
    """Put a sampled page in a content bucket, always saying how it was decided."""
    signals = signals or {}
    node_type = signals.get("node_type")
    if node_type:
        bucket = SOURCE_TYPE_MAP.get(node_type)
        if bucket:
            return {"bucket": bucket, "source_type": node_type, "basis": "source node type"}
        return {"bucket": "unmapped", "source_type": node_type, "basis": "source node type"}

    if signals.get("views_rows", 0) >= 3:
        return {"bucket": "listing", "source_type": None, "basis": "views rows in markup"}
    if signals.get("time_elements", 0) >= 1 and signals.get("has_byline"):
        return {"bucket": "post", "source_type": None, "basis": "date + byline heuristic"}
    return {"bucket": "page", "source_type": None, "basis": "default"}


def classify_forms(pages: list) -> dict:
    """Split forms into site chrome and content, by how many pages carry them.

    A chrome form (search, newsletter, donate) appears on every sampled page; a
    form the site owner authored appears on one. That is evidence the tool
    already collects, and it generalises to every chrome form without naming any
    of them -- unlike a name-matching deny-list, which has to grow forever and
    silently dropped a real course-search webform.
    """
    if not pages:
        return {"content": [], "chrome": []}
    counts = Counter(f["fingerprint"] for page in pages for f in page["signals"]["forms"])
    # ceil, not round: round() truncated the 80% requirement to 67% at three
    # pages, labelling a real two-of-three content form as chrome.
    threshold = max(2, math.ceil(CHROME_FORM_SHARE * len(pages)))
    seen, content, chrome = set(), [], []
    for page in pages:
        for form in page["signals"]["forms"]:
            if form["fingerprint"] in seen:
                continue
            seen.add(form["fingerprint"])
            entry = dict(form, pages_seen_on=counts[form["fingerprint"]])
            (chrome if counts[form["fingerprint"]] >= threshold else content).append(entry)
    return {"content": content, "chrome": chrome}


def summarise(pages: list) -> dict:
    """Roll sampled-page signals up into site-level counts."""

    def flat(key):
        return [value for page in pages for value in page["signals"].get(key, [])]

    # Bucket counts alone read as measurements. On a Drupal 7 source most pages
    # fall through to the "default" basis, so keeping the basis is what stops a
    # guessed count being quoted as a counted one.
    by_basis: dict[str, Counter] = {}
    for page in pages:
        classification = page["classification"]
        by_basis.setdefault(classification["bucket"], Counter())[classification["basis"]] += 1

    forms = classify_forms(pages)
    return {
        "sampled": len(pages),
        # A crawl finds both /node/1 and its alias /welcome. Counting canonicals
        # is the only way to know how many distinct pages were actually sampled.
        "distinct_canonicals": len({p["signals"]["canonical"] or p["url"] for p in pages}),
        "buckets": {bucket: sum(bases.values()) for bucket, bases in by_basis.items()},
        "buckets_by_basis": {bucket: dict(bases) for bucket, bases in by_basis.items()},
        "unmapped_source_types": sorted(
            {
                p["classification"]["source_type"]
                for p in pages
                if p["classification"]["bucket"] == "unmapped" and p["classification"]["source_type"]
            }
        ),
        "source_node_types_seen": sorted(
            {p["signals"]["node_type"] for p in pages if p["signals"]["node_type"]}
        ),
        "carousel_libraries": dict(Counter(flat("carousel_libraries"))),
        "carousel_markup_hints": dict(Counter(flat("carousel_markup_hints"))),
        "external_form_vendors": dict(Counter(flat("external_form_vendors"))),
        "embedded_media": dict(Counter(flat("embedded_media"))),
        "interactive_patterns": dict(Counter(flat("interactive_patterns"))),
        "iframe_hosts": dict(Counter(flat("iframe_hosts"))),
        "third_party_script_hosts": dict(Counter(flat("third_party_script_hosts"))),
        "content_forms": forms["content"],
        "chrome_forms": forms["chrome"],
        "pages_with_webform": sum(1 for p in pages if p["signals"]["has_webform"]),
        "pages_with_hero": sum(1 for p in pages if p["signals"]["has_hero"]),
        "pages_with_data_table": sum(1 for p in pages if p["signals"]["has_data_table"]),
        "pages_with_inline_style": sum(
            1
            for p in pages
            if p["signals"]["inline_style_blocks"] or p["signals"]["inline_style_attrs"]
        ),
        "total_images_on_sample": sum(p["signals"]["image_count"] for p in pages),
        "total_pdf_links_on_sample": sum(p["signals"]["pdf_link_count"] for p in pages),
    }


def choose_sample(urls: list, limit: int) -> list:
    """Spread the sample across path prefixes, deepest-first inside each."""
    grouped = group_by_prefix(urls)
    ranked = [
        sorted(members, key=lambda u: (-len(_segments(u)), u))
        for _, members in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]
    sample = []
    for round_index in range(max((len(r) for r in ranked), default=0)):
        for bucket in ranked:
            if round_index < len(bucket) and len(sample) < limit:
                sample.append(bucket[round_index])
        if len(sample) >= limit:
            break
    return sample


# --------------------------------------------------------------------------
# Network layer
# --------------------------------------------------------------------------


class Fetcher:
    """Sequential, polite, GET-only HTTP client.

    Uses an opener that can only speak HTTP(S) and never auto-redirects, and
    validates every redirect hop against the base host before following it.
    """

    MAX_REDIRECTS = 5

    def __init__(self, base_host: str, delay: float = 0.6, timeout: int = 20):
        self.base_host = base_host
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.count = 0
        self.errors: list[str] = []
        self.refused_redirects: list[str] = []
        self._cache: dict[tuple, tuple] = {}
        self._opener = build_safe_opener()

    def get(self, url: str, cache: bool = True, status_only: bool = False) -> tuple:
        """Return (status, headers dict, body text). Never raises.

        `cache=False` for URLs fetched exactly once (robots, sitemaps, probes):
        memoising them retains bodies that can never be hit again.
        `status_only=True` skips reading the body -- the fingerprint probes only
        want the status code, and `/jsonapi` can be hundreds of KB. It is part
        of the cache key, so a body-less result can never be handed to a caller
        that needs the body.
        """
        key = (url, status_only)
        if cache and key in self._cache:
            return self._cache[key]
        result = self._follow(url, status_only)
        if cache:
            self._cache[key] = result
        return result

    def _follow(self, url: str, status_only: bool) -> tuple:
        """Fetch, validating each redirect hop rather than trusting urllib."""
        current = url
        for _ in range(self.MAX_REDIRECTS + 1):
            if not is_fetchable(current, self.base_host):
                self.errors.append(f"{current}: refused (not an on-host http(s) URL)")
                return 0, {}, ""
            status, headers, body = self._fetch_once(current, status_only)
            if status not in (301, 302, 303, 307, 308):
                return status, headers, body
            location = _lower_headers(headers).get("location", "")
            if not redirect_allowed(current, location, self.base_host):
                self.refused_redirects.append(f"{current} -> {location}")
                return status, headers, ""
            current = urllib.parse.urljoin(current, location)
        self.errors.append(f"{url}: too many redirects")
        return 0, {}, ""

    def _fetch_once(self, url: str, status_only: bool) -> tuple:
        if self.count:
            time.sleep(self.delay)
        self.count += 1
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                if status_only:
                    return response.status, dict(response.headers), ""
                body = response.read(3_000_000).decode(
                    response.headers.get_content_charset() or "utf-8", "replace"
                )
                return response.status, dict(response.headers), body
        except urllib.error.HTTPError as exc:
            # A refused redirect surfaces here; the 3xx status and Location
            # header are what the caller needs to decide what to do.
            return exc.code, dict(exc.headers or {}), ""
        except Exception as exc:  # DNS, TLS, timeout, unsupported scheme
            self.errors.append(f"{url}: {type(exc).__name__}: {exc}")
            return 0, {}, ""


def sitemap_inventory(fetcher, base_url: str, declared, blocked, max_urls: int, max_sitemaps: int) -> dict:
    """Collect URLs from the site's sitemap(s), if it publishes any.

    The document budget matters: a `sitemapindex` contributes zero URLs while
    adding children to the queue, so the URL cap alone does not bound the
    request count. A site declaring 200 dead child sitemaps would otherwise cost
    200 requests of pure politeness delay.
    """
    base_host = urllib.parse.urlparse(base_url).netloc
    candidates = list(declared) or [base_url + "/sitemap.xml", base_url + "/sitemap_index.xml"]
    seen, queue, raw, reports = set(), list(candidates), [], []
    refused = 0
    while queue and len(raw) < max_urls and len(reports) < max_sitemaps:
        sitemap_url = queue.pop(0)
        if sitemap_url in seen:
            continue
        seen.add(sitemap_url)
        # `Sitemap:` lines and nested <loc> values are source-controlled, so the
        # scheme and host are the site's choice unless checked here.
        if not is_fetchable(sitemap_url, base_host):
            refused += 1
            reports.append({"url": sitemap_url, "status": None, "kind": "refused-target", "urls": 0})
            continue
        status, _, body = fetcher.get(sitemap_url, cache=False)
        parsed = (
            parse_sitemap(body)
            if status == HTTP_OK
            else {"kind": f"http-{status}", "urls": [], "sitemaps": []}
        )
        reports.append(
            {
                "url": sitemap_url,
                "status": status,
                "kind": parsed["kind"],
                "urls": len(parsed["urls"]),
            }
        )
        raw.extend(parsed["urls"])
        queue.extend(parsed["sitemaps"])

    filtered = filter_inventory(raw[:max_urls], base_url, blocked)
    return {
        "urls": filtered["urls"],
        "excluded": filtered["excluded"],
        "reports": reports,
        "refused_targets": refused,
        "budget_exhausted": len(reports) >= max_sitemaps and bool(queue),
    }


def crawl_inventory(fetcher, base_url: str, home_html: str, blocked: list, max_fetches: int, max_urls: int) -> dict:
    """Discover URLs by following links when the site publishes no sitemap.

    Drupal 7 sites usually have no `sitemap.xml`, so without this the whole
    inventory would be a single page. Breadth-limited on purpose: it fetches at
    most `max_fetches` pages, so the result is a **lower bound** on site size,
    not a census. Callers must say so.
    """
    home = base_url + "/"
    discovered, seen = [home], {home}
    excluded: Counter = Counter()
    frontier: list = []

    def absorb(page_url: str, html: str) -> None:
        # Resolve against the page the markup came from, not the homepage:
        # `href="staff"` on /dept/about means /dept/staff, and resolving it
        # against the root invented a URL that 404s while missing the real child.
        scan = scan_links(html, page_url, blocked)
        excluded.update(scan["excluded"])
        for link in scan["urls"]:
            if link not in seen:
                seen.add(link)
                discovered.append(link)
                frontier.append(link)

    absorb(home, home_html)
    fetched, skipped_non_html = 0, 0
    while frontier and fetched < max_fetches and len(discovered) < max_urls:
        url = frontier.pop(0)
        status, headers, body = fetcher.get(url)
        fetched += 1
        if status != HTTP_OK or not body:
            continue
        if not is_html_response(headers):
            skipped_non_html += 1
            continue
        absorb(url, body)
    return {
        "urls": discovered[:max_urls],
        "excluded": dict(excluded),
        "pages_crawled": fetched,
        "non_html_skipped": skipped_non_html,
        "frontier_remaining": len(frontier),
    }


def probe(base_url: str, sample_limit: int, delay: float, max_urls: int, crawl_pages: int, max_sitemaps: int) -> dict:
    problem = base_url_problem(base_url)
    if problem:
        return {"source_url": base_url, "error": problem, "fetch_errors": []}

    base_url = base_url.rstrip("/")
    base_host = urllib.parse.urlparse(base_url).netloc
    fetcher = Fetcher(base_host, delay=delay)

    status, headers, home_html = fetcher.get(base_url + "/")
    if not home_html:
        return {
            "source_url": base_url,
            "error": f"could not fetch homepage (status {status})",
            "fetch_errors": fetcher.errors,
        }
    if not is_html_response(headers):
        # The homepage seeds the crawl, the nav, and the fingerprint. Parsing a
        # non-HTML root is the same mistake the per-page gate exists to prevent.
        return {
            "source_url": base_url,
            "error": (
                "homepage did not return HTML "
                f"(content-type {_lower_headers(headers).get('content-type', 'unset')!r})"
            ),
            "fetch_errors": fetcher.errors,
        }

    robots_status, _, robots = fetcher.get(base_url + "/robots.txt", cache=False)
    blocked = disallowed_prefixes(robots) if robots_status == HTTP_OK else []
    declared_sitemaps = sitemaps_from_robots(robots) if robots_status == HTTP_OK else []
    robots_matcher_list = robots_matchers(blocked)

    probes = {}
    for path in FINGERPRINT_PATHS:
        # Honour robots for the probes too. Stock Drupal robots.txt disallows
        # /CHANGELOG.txt, and fetching it anyway made the compliance claim false.
        if any(matcher.match(path) for matcher in robots_matcher_list):
            probes[path] = "disallowed-by-robots"
            continue
        probe_status, _, _ = fetcher.get(base_url + path, cache=False, status_only=True)
        probes[path] = probe_status

    sitemap_result = sitemap_inventory(
        fetcher, base_url, declared_sitemaps, blocked, max_urls, max_sitemaps
    )
    inventory = sitemap_result
    inventory_source = "sitemap"
    if not inventory["urls"]:
        # Keep the sitemap diagnostics: an empty result after fetching a 404, an
        # unparseable sitemap, or a refused target must not look identical to
        # "this site publishes no sitemap".
        inventory = crawl_inventory(fetcher, base_url, home_html, blocked, crawl_pages, max_urls)
        inventory_source = "link-crawl"

    all_urls = inventory["urls"]
    buckets = bucket_paths(all_urls)
    home_url = base_url + "/"
    # The homepage is always sampled and counts against the budget.
    sample_urls = choose_sample(all_urls, max(sample_limit - 1, 0)) if all_urls else []
    sample_urls = [home_url] + [u for u in sample_urls if u != home_url]

    pages = []
    for url in sample_urls:
        page_status, page_headers, page_html = fetcher.get(url)
        if page_status != HTTP_OK or not page_html:
            pages.append({"url": url, "status": page_status, "skipped": "not-fetchable"})
            continue
        if not is_html_response(page_headers):
            # Parsing a non-HTML body as a page is how this tool once reported a
            # content type that did not exist. Record it; never parse it.
            pages.append({"url": url, "status": page_status, "skipped": "non-html-response"})
            continue
        signals = page_signals(page_html, url)
        pages.append(
            {
                "url": url,
                "status": page_status,
                "signals": signals,
                "classification": classify_page(signals),
            }
        )

    good_pages = [p for p in pages if not p.get("skipped")]
    return {
        "source_url": base_url,
        "probed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "requests_made": fetcher.count,
        "fetch_errors": fetcher.errors,
        "robots": {
            "status": robots_status,
            "disallow": blocked,
            "sitemaps_declared": declared_sitemaps,
        },
        "refused_redirects": fetcher.refused_redirects,
        "fingerprint": fingerprint(headers, home_html, probes),
        "sitemaps": sitemap_result.get("reports", []),
        "sitemap_refused_targets": sitemap_result.get("refused_targets", 0),
        "url_inventory": {
            "source": inventory_source,
            "is_lower_bound": inventory_source == "link-crawl",
            "total": len(all_urls),
            "truncated_at_max": len(all_urls) >= max_urls,
            "sitemap_budget_exhausted": sitemap_result.get("budget_exhausted", False),
            "sitemap_excluded": sitemap_result.get("excluded", {}),
            "pages_crawled": inventory.get("pages_crawled"),
            "frontier_remaining": inventory.get("frontier_remaining"),
            # What the filters removed, and why. A silently over-firing rule
            # would otherwise undercount the site with no trace here.
            "excluded": inventory.get("excluded", {}),
            "non_html_skipped": inventory.get("non_html_skipped", 0),
            "path_buckets": buckets[:25],
            "depth_histogram": depth_histogram(all_urls),
        },
        "navigation": extract_nav(home_html),
        "sampled_pages": pages,
        "summary": summarise(good_pages),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("url", help="Base URL of the public source site")
    parser.add_argument("--sample", type=int, default=12, help="Pages to sample (default 12)")
    parser.add_argument("--delay", type=float, default=0.6, help="Seconds between requests (default 0.6)")
    parser.add_argument("--max-urls", type=int, default=5000, help="Stop collecting URLs past this many (default 5000)")
    parser.add_argument("--crawl-pages", type=int, default=12, help="Fetch budget for the no-sitemap link crawl (default 12)")
    parser.add_argument("--max-sitemaps", type=int, default=20, help="Sitemap documents to fetch (default 20)")
    args = parser.parse_args(argv)

    problem = base_url_problem(args.url)
    if problem:
        parser.error(problem)

    result = probe(
        args.url, args.sample, args.delay, args.max_urls, args.crawl_pages, args.max_sitemaps
    )
    json.dump(result, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")
    return 1 if result.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
