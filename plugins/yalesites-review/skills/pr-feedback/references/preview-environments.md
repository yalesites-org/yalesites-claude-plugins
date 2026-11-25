# Where to test a YaleSites PR

Read this when resolving a PR's environment: in `SKILL.md` Step 3, in `test-plan.md`, in
`batch-mode.md` Step B2, and when `pr-brief` writes a brief's **Where to test** section.

Every PR in scope gets one of four answers, and which one depends on the repo. Getting this
wrong wastes the most expensive part of review, so **resolve the environment by probing, never
by assuming the pattern holds.**

## Resolution order

1. **Read the PR's own comments for a bot-posted preview link.** Netlify and Pantheon both
   comment their URL on the PR. A link in the thread beats any pattern in this file, because
   it reflects what actually deployed.
   ```
   gh pr view NUMBER --repo yalesites-org/REPO --json comments \
     -q '.comments[].body' | grep -oiE 'https?://[a-z0-9.-]*(pantheonsite|netlify)[^ )">]*' | sort -u
   ```
2. **Fall back to the repo's pattern below**, and verify it answers before writing it into a
   brief. A pattern URL that 404s is worse than saying there is no environment.
3. **If nothing resolves, say so plainly.** "No preview environment for this PR, needs local
   Lando" is a useful line in a brief. A dead link is not.

## By repo

| Repo | Environment | Pattern |
|---|---|---|
| `yalesites-project` | Pantheon multidev, the full CMS | `https://pr-{NUMBER}-yalesites-platform.pantheonsite.io/` |
| `component-library-twig` | Netlify deploy preview, Storybook only | `https://deploy-preview-{NUMBER}--dev-component-library-twig.netlify.app` |
| `atomic` | None of its own | Test through the sibling `yalesites-project` PR's multidev |
| `tokens` | None of its own | Test through the sibling `component-library-twig` PR's Netlify preview |
| `yale-ui-cl` | None per PR yet. The published UICL Storybook builds from `main` only | Check for a deployed preview first (a bot preview link in the PR comments, a non-Pages deployment, or `https://deploy-preview-{N}--yale-ui-cl.netlify.app` answering); if none, `pr-feedback` builds Storybook locally from the PR head and drives it, per `drive-it.md`, "The `yale-ui-cl` path". The brief names "local Storybook from the PR head" as the environment, never the Pages site. Name the CLT story to compare against: `https://yalesites-org.github.io/component-library-twig/?path=/story/{id}` |

**`atomic` and `tokens` are consumed downstream**, atomic as a Drupal theme and tokens as an npm
package, so neither builds a reviewable environment on its own PR. When there is no sibling PR
for the same ticket number, there is no deployed way to see the change and the brief should say
that outright rather than inventing a URL.

**Storybook is not the CMS.** A `component-library-twig` preview shows the component in
isolation with Storybook controls. It cannot show Layout Builder placement, editor-facing field
labels, role gating, or anything that depends on Drupal passing real values in. When a ticket's
acceptance criteria are about what an editor can do, the Netlify preview is the wrong place to
check it and the multidev is the right one.

## Multidev content: go straight to the page

Multidevs are seeded from the `dev-yalesites-platform` database, which runs the **visreg**
content set. Test content for most blocks and content types already exists, so testing rarely
means building a page from scratch. Swap in the PR number and go direct instead of navigating
the menu.

**Blocks** live at `/blocks-for-visreg/{slug}`:

`accordion`, `action-banner`, `button`, `calendar-list`, `callout`, `custom-cards`,
`directory`, `divider`, `embed`, `events-calendar`, `facts-and-figures`, `gallery`,
`grand-hero`, `image`, `image-banner`, `in-line-message`, `link-grid`, `media-grid`,
`post-feed`, `pre-built-form`, `quick-links`, `quote`, `quote-callout`, `reference-card`,
`spotlight-landscape`, `spotlight-portrait`, `tabs`, `text`, `tiles`, `video`, `video-banner`,
`view`, `wrapped-image`, `wrapped-text-callout`

**Content types** live at `/content-types/{slug}`: `events`, `posts`, `profile`, `resource`

Example: a PR touching the Accordion block on `yalesites-project#1374` is at
`https://pr-1374-yalesites-platform.pantheonsite.io/blocks-for-visreg/accordion`.

This list reflects the menu as of 2026-07-20. **A 404 here is a finding, not a dead end:** it
means the block is new or renamed, and the visreg content set has a coverage gap worth a
follow-up ticket. Fall back to browsing `/blocks-for-visreg` or `/content-types` on the
multidev and note the discrepancy.
