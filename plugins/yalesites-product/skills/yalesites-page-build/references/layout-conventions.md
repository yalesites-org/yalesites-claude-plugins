# Layout conventions for yalesites.yale.edu

How the team assembles pages, beyond what any one block's docs say. These come from builds the product team reviewed and corrected. Add to this file when a review corrects something new.

## End the page on a non-text block

A page should not trail off into a paragraph. End it with a block that works as the period at the end of the sentence:

- a **reusable Callout** or **Quick Links** block (support, next steps, related training)
- a **View** block used as "related content" (related posts, resources, or pages by tag)

Open the block picker (`/layout_builder/choose/block/overrides/node.<nid>/<section>/<region>`) and scroll past the inline block types to the reusable blocks. Prefer one that already exists over writing a new one. Ones seen in use:

| Reusable block | Type | Seen at the end of |
|---|---|---|
| Need help getting started QuickLinks | Quick Links | Community Spotlight (node 559) |
| Building with Blocks Callout | Callout | Text Block (node 212) |

Also in the picker, not yet checked on a real page: Support Callouts, Request a site to get started, Tips and Tricks end callout, We're Here to Help quicklinks (all reusable). Add a row when one is confirmed in use.

If the draft ends with a Text block of links (a support list, for example), keep it, and still add the non-text block after it. On node 559 the "Start or grow your own site" Text block is followed by the reusable Quick Links block.

## Padding between blocks

The **Text** block defaults to **No padding**. That is fine for one Text block alone, but two Text blocks in a row then sit jammed together, with the second heading right against the paragraph above it.

- When a Text block follows another Text block, set the second one to **No bottom padding** (that is, keep the top padding). On node 559, the "Find a site like yours" Text block after the intro needed exactly this.
- Most other blocks (Quote Callout, View, Callout, Divider) default to **Padding on both top and bottom**. Leave them on the default unless the page's own pattern says otherwise.
- The section-level "Connected Sections" trick (No bottom padding on one section, No top padding on the next) is for joining sections. Do not use it to fix spacing inside one section.

## Match the page you are editing

On an existing page, read the blocks around the insertion point before adding anything, and copy their pattern:

- **Dividers between topics.** The block reference pages (Text Block, node 212) alternate Text, Divider, Text. Those Text blocks keep **No padding**, because the Divider (100% width, default padding) supplies the space. A new topic goes in as Text plus Divider, not Text alone.
- **Headings.** Use the heading level the neighbors use for the same kind of topic (usually H2 in a Text block, with H3 for sub-items).
- **Table labels.** When a new option joins a comparison table, relabel the existing column headings rather than adding a column, unless the new option behaves differently.

## Placement order

A new block lands at the end of its region. Move it into place in the same pass, before saving the layout, so the saved draft never has a block stranded under the page's closing block.
