# Platform fit check

Load this before drafting or grooming a feature request, an enhancement, a UX change, or any ticket inside an epic or feature parent. It cross-references the request against the YaleSites platform knowledge base. It catches overlap, suggests extensions over net-new work, and surfaces documentation implications early.

An intake stub runs only Step 1. A plain bug report can use the quick check in `SKILL.md` instead.

The knowledge base lives in the `yalesites` skill, in the separate core `yalesites` plugin. If it isn't installed, say so, do what you can from the repos, and don't guess at what the platform already does.

---

## Step 1: Check what already exists

Load the relevant `yalesites` skill references and ask:

- **Does a similar block, component, or content type already exist?**
  Check `blocks-reference.md` and `paragraphs-reference.md`. If the request is for something like "a new way to display a list of items," check whether an existing block (e.g., Collection, Custom Card Collection) already does this or could be extended.

- **Does an existing content type already support this use case?**
  Check `content-types-reference.md`. If the request adds a field or behavior to Pages, Posts, Events, etc., confirm whether the field already exists or if this is genuinely additive.

- **Does an existing setting or configuration option already cover this?**
  Check `settings-reference.md`. Some "feature requests" are already available but undiscovered by the requester.

- **Are there existing Views or display modes that could be repurposed?**
  Check `views-reference.md`.

## Step 1b: Check who the change affects

**Do this for any ticket that changes what users see or do:** features, UX changes, editorial workflow changes, and bugs that affect an editor-facing behavior. Skip it for purely internal work (dependency bumps, CI, refactors with no user-visible surface) and say you're skipping it rather than silently omitting it.

Load the `yalesites-ux-research` skill (it ships in this plugin) and answer three questions in the ticket:

1. **Which archetype(s) does this affect?** Name them explicitly. The six are Multi-Site Manager, Part-Time Owner, The Maintainer, Transitioning Team, New Recruit, and Solo Starter.
2. **Does it map to a known pain point?** Check the pain point table. A request matching a high-count pain point (confusing terminology at 67%, misleading search results at 61%, poor UI discoverability at 56%) carries real evidence behind it, and the ticket should say so.
3. **Does it put a current delight at risk?** Check the delights table before scoping anything that changes learning resources, the Views GUI, release communications, or brand-compliant output.

Two traps worth naming, both from the 2026 research:

- **Don't "simplify" for the Part-Time Owner.** They are time-poor, not skill-poor. Reducing steps helps them; removing capability doesn't.
- **New-user cost is the usual hidden cost.** The five most-cited pain points all land hardest on Solo Starter and New Recruit. If a change adds a new term, setting, or interface surface, say what it costs those two archetypes even when it's aimed at someone else.

Where this lands in the ticket: name the affected archetypes and the reasoning in the collapsed **Background and analysis** block (see "How this reads on GitHub" in `references/issue-format.md`), and turn archetype-specific expectations into **acceptance criteria** (for example, "labels should be understandable to a New Recruit with no YaleSites training"), which stay visible. Don't paste archetype summaries in wholesale.

## Step 1c: Check how much it's actually used

**Do this when the ticket names a specific block, section layout, or sitewide setting.** Skip it (silently) for everything else: usage data on a ticket that isn't about a measurable feature is noise.

Use the `yalesites-portfolio` skill if it is available (it ships in the separate `yalesites` plugin; if it is not installed, skip this step silently and don't estimate usage numbers). Pull two things:

1. **One line of adoption data** for the collapsed Background and analysis block, with the crawl vintage: e.g. "Facts and Figures: used on 12.8% of crawled sites (38 of 296 sites, 226 instances) as of the 2026-10 portfolio crawl." This grounds the priority conversation: a change to a 70%-adoption block and one to a 5% block are different risks and different wins.
2. **For breaking or behavior-changing work** (template changes, update hooks, config migrations): name 2-3 of the heaviest-usage sites from the block's `Top sites` line in its `references/block-usage.md`. In the acceptance criteria they are reference sites, not QA targets: a yalesites-project multidev carries one site's content, so write "recreate the Facts and Figures band onha uses on the multidev and verify X there", not "verify on onha". The live sites show current behavior and the content shape to copy; the change is tested on the multidev.

Keep it to those two. Never paste usage tables into a ticket.

## Step 2: Determine the scope recommendation

Based on the platform check, classify the ticket as one of:

| Classification | What it means | Action |
|---------------|---------------|--------|
| **Extend existing** | A current block/component/type already handles the core need; this request adds an option, field, or variant | Note the existing feature in the ticket description; scope the work as an enhancement to that feature |
| **New, distinct feature** | Nothing on the platform does this; the request is genuinely additive | Proceed as a new feature ticket |
| **Already exists** | The request is already supported on the platform | Flag this in the ticket; note where the feature lives and consider closing as "works as intended" or converting to a docs/training ticket |
| **Conflicts with platform direction** | The request would add complexity that cuts against platform constraints or brand consistency goals | Flag the concern in the ticket; surface it for PM discussion before scoping |

## Step 3: Surface the findings in the ticket

Incorporate the platform check findings into the ticket. The full write-up goes in the collapsed **Background and analysis** block, but these three cases also get a short visible note right under the TL;DR, because they change whether or how the ticket should be scoped:

- **If extending existing:** The description should name the existing feature ("This adds a new layout option to the existing Action Banner block..."). The acceptance criteria should note which existing docs need updating rather than pointing to new docs.
- **If already exists:** Short note under the TL;DR ("Note: this functionality may already exist via [X]. Recommend confirming before scoping.").
- **If conflicts:** Short note under the TL;DR flagging the concern for the PM to review before development is assigned. This also keeps the ticket out of the `claude` pool (see `references/fields.md`).
