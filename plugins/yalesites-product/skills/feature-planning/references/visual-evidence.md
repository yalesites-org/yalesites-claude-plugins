# Visual evidence

How Step 3b captures the screenshots the planning board shows. The goal is that every question
about how something looks or where it lives can be answered by looking, not imagining.

## What to capture

| Set | Where from | How many | Label |
|---|---|---|---|
| **Inspiration** | Strong external findings, tiers 0 to 3: the live example, and the public editor doc if there is one | Two to five per question that needs them; the best example from each tier that had one | `Tier 1: Stanford Sites, events list, checked 2026-11-01` |
| **Closest current option** | The YaleSites block or pattern editors use today to work around the gap, on a heavy-use site from the portfolio | One or two | `Today: Custom Card Collection on onha, 1440px` |
| **Starting point** | The Storybook story for an existing component the feature could build on (published component-library-twig Storybook) | One per component | `Component: Callout, default story` |
| **Affected area** | The existing block or setting on its heaviest-use sites, for changes to something that exists | Two or three sites, at each width that matters | `Facts and Figures on onha, 360px` |

Capture at **1440px** by default, and also at **360px** when the question is about layout. Crop to
the part that matters (an element screenshot of the block, not the whole page) unless the
question is about where it sits on the page.

Skip a capture rather than force it: a finding with no public page to show stays as a `text`
context block with its link.

## How to capture

Use the Playwright CLI headless, in its own session, logged out:

```bash
npx -y @playwright/cli@0.1.22 -s=feature-planning open about:blank
npx -y @playwright/cli@0.1.22 -s=feature-planning resize 1440 900
npx -y @playwright/cli@0.1.22 -s=feature-planning goto '<url>'
npx -y @playwright/cli@0.1.22 -s=feature-planning find '<heading text near the element>'
npx -y @playwright/cli@0.1.22 -s=feature-planning screenshot <ref> --filename=<packet-dir>/<file>.png
npx -y @playwright/cli@0.1.22 -s=feature-planning close
```

For anything taller than the viewport (a 50-image gallery is 8,000px), scroll the element to the
top and take a viewport screenshot instead of an element or clipped one:

```bash
npx -y @playwright/cli@0.1.22 -s=feature-planning run-code "async page => { await page.evaluate(() => { const el = document.querySelector('<css>'); window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 20); }); await page.waitForTimeout(1500); await page.screenshot({ path: '<packet-dir>/<file>.png' }); }"
```

Don't build a `clip` from `boundingBox()`: it is relative to the viewport, a full-page clip is
relative to the page, and the mismatch captures the wrong part of the page. The wait lets lazy
images load. To show an interaction (a viewer opening), click it inside the same `run-code` and
screenshot after a short wait.

Run these from the session's working folder: the CLI writes a `.playwright-cli/` snapshot folder
into the current directory, which must not land in a repo. Leave off `<ref>` for a full viewport.
Close the session when done. If the CLI can't launch a
browser, follow "Browsers" in `../../pr-feedback/references/drive-it.md`; if no browser is
available at all, say so in the Step 1 source list and fall back to links.

In the Claude desktop app, the Claude in Chrome tools work too, but they use the user's own
browser profile, so open a new tab and never interact with anything signed in.

## Rules

- **Public pages only.** Never sign in, never submit a form, decline non-essential cookie banners
  and close other popups before capturing. If a page is behind a login or a paywall, skip it.
- **Name files for what they show:** `stanford-events-list-1440.png`, `today-card-collection-onha-1440.png`.
  Keep the URL with each one; it goes in the context block's `url`.
- **Look before using.** Open each screenshot before it goes on the board. A cookie banner, a
  loading spinner, or the wrong part of the page is worse than no picture.
- **Local only.** Screenshots of other institutions' sites stay in the scratchpad packet for the
  user's decision. They never go into a ticket, a PR, a docs page, or the `github-screenshots`
  branch; the ticket links to the source page instead.

## On the board

- **One option, one picture:** a question whose options are visual directions gets a `compare`
  block with one image per option, labeled by the option (`Stacked:` / `Horizontal:` /
  `Carousel:`), in the same order as the option cards. Put "today" first when there is one.
- **Inspiration without options:** when the pictures inform a question rather than map to its
  options ("what should this block do?"), show them as a `compare` block labeled by source.
- **Marks:** pin the specific thing that makes an example worth seeing ("filters sit above the
  list, not in a sidebar"). One or two per image.
- Everything else about context blocks, labels, and marks: `../../pr-feedback/references/review-board.md`.
