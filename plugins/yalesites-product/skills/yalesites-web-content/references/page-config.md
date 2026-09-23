# Page config for yalesites.yale.edu

The user builds these pages themselves in the Drupal WYSIWYG. The config block in your draft is what turns body copy into a page that actually appears where it should. Getting the parent item or Content Collections wrong means the page is live but unreachable from the nav, which is a silent failure.

## The config fields

**Content type:** Page, for nearly all user guide and resource content.

**Parent item:** sets the breadcrumb and the left nav position. Name the specific section landing page, not the top-level User Guide. This is the field most likely to be wrong, so check it against the real nav in `site-map.md` rather than guessing from the URL.

**Content Collections:** the mechanism behind the User Guide's left-hand navigation. A page needs this enabled to appear in the section nav. See `/secondary-navigation-with-content-collections` for how it works.

**URL alias:** User Guide pages are inconsistent here. Some sit at the root (`/editorial-workflow`, `/media-library-0`, `/using-taxonomy-and-vocabulary`), others use a full path (`/explore-resources/user-guide/building-your-site/content-types`). Match the closest sibling rather than imposing a scheme. Note that `/media-library-0` carries a Drupal dedupe suffix, so an alias you want may already be taken.

**Nav order:** say where it lands relative to its siblings.

**Hub card:** section landing pages show cards for their children. A new page usually needs one adding, with the teaser text and an illustration. The existing cards use undraw illustrations stored in `/sites/default/files`.

**Teaser image:** also serves as the og:image for social and chat previews.

**Cross-links:** related pages that should link to the new one. Worth doing in the same pass, since it's easy to add a page nothing points at.

## The teaser

About 150 characters, 160 hard ceiling. One sentence, and it has three jobs: the hub card blurb, the meta description, and the search result snippet. Count it and state the count in the draft, since "about 150" invites drift.

Lead with the benefit, not the mechanism. Compare the live examples:

> Learn how to build a basic or mega menu on the new YaleSites Platform and wayfinding tactics to ensure users can easily navigate your site.

> The Media Library lets you upload, organize, and reuse images and files across your YaleSite, making media management quick and easy.

Note that these live teasers predate the STE convention and don't follow it. Match their warmth and their length, not their sentence construction.

## User Guide structure

The current User Guide sections and their children are listed in `site-map.md`, under "Inside Resource Library: the User Guide." Check the parent item against that list.

Verify it before relying on it. Fetch `/managing-site-content` or any published User Guide page; the full left nav renders in the markup on every one of them, so a single fetch gives you the current tree.

## Naming a new page

Sibling titles are mostly noun phrases naming the feature (Media Library, Google Tag Manager, Editorial Workflow), with a couple of gerund forms (Building Your Menu, Using Taxonomy and Vocabulary). Either fits.

Two things worth weighing when the name isn't obvious:

- **Match the label in the admin UI** where you can. Someone who sees "Dashboard" in their toolbar will search that word, and a title that differs breaks the match.
- **Check what the code calls it.** If the routing file, form docblocks, and view descriptions all say "editorial dashboard," that name is already the team's, and publishing it beats inventing a third one.

When those two conflict, say so and let the user choose rather than picking silently.

## Publishing

Drafts are built unpublished and published when the release ships. Unpublished pages need a CAS login with editor permissions or above, so `WebFetch` on one returns an empty body. That is expected, not an error. Verify from the local draft file instead.
