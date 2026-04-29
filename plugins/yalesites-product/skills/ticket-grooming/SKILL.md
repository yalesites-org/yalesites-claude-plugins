---
name: yalesites-ticket-grooming
description: "Create and groom GitHub issues for the YaleSites backlog. Use when creating a new issue, filling out an existing stub ticket, reviewing a ticket for completeness, or preparing issues for an upcoming sprint or grooming session. Applies the correct description format, acceptance criteria, priority, size, type, and labels. Cross-references the YaleSites platform knowledge base to catch overlap with existing features before new work is scoped."
---

# YaleSites Ticket Grooming Skill

## Overview

This skill helps create well-formed GitHub issues for the YaleSites backlog and groom existing stub tickets into complete, actionable ones. Every issue should be readable by anyone on the team — content editors, site owners, project managers — regardless of technical background.

**Repositories available for developer context, relevant code, and existing patterns:**
- `yalesites-org/yalesites-project`
- `yalesites-org/component-library-twig`
- `yalesites-org/atomic`

Search these when you need implementation context, but always write the issue description in plain English first. Technical details belong in the acceptance criteria, not the description.

---

## Platform Fit Check (Do This First)

Before drafting or grooming any ticket, cross-reference the request against the YaleSites platform knowledge base. This catches overlap, suggests extensions over net-new work, and surfaces documentation implications early.

### Step 1: Check what already exists

Load the relevant yalesites skill references and ask:

- **Does a similar block, component, or content type already exist?**
  Check `blocks-reference.md` and `paragraphs-reference.md`.

- **Does an existing content type already support this use case?**
  Check `content-types-reference.md`.

- **Does an existing setting or configuration option already cover this?**
  Check `settings-reference.md`.

- **Are there existing Views or display modes that could be repurposed?**
  Check `views-reference.md`.

### Step 2: Determine the scope recommendation

| Classification | What it means | Action |
|---------------|---------------|--------|
| **Extend existing** | A current block/component/type handles the core need; this adds an option, field, or variant | Note the existing feature in the description; scope as an enhancement |
| **New, distinct feature** | Nothing on the platform does this; genuinely additive | Proceed as a new feature ticket |
| **Already exists** | The request is already supported | Flag it; consider closing as "works as intended" or converting to a docs/training ticket |
| **Conflicts with platform direction** | Would add complexity cutting against platform constraints or brand consistency | Flag the concern for PM discussion before scoping |

### Step 3: Surface the findings in the ticket

- **If extending existing:** Name the existing feature in the description. Note which existing docs need updating in acceptance criteria.
- **If already exists:** Add a note at the top: "Note: this functionality may already exist via [X]. Recommend confirming before scoping."
- **If conflicts:** Add a note flagging the concern for PM review before development is assigned.

---

## Issue Format

Every issue needs these six fields, in this order:

---

### 1. Description

Briefly describe the feature, bug, or improvement in plain language. Avoid developer jargon. Focus on **what it is** and **why it matters**. Anyone on the team should be able to read this and understand the work.

---

### 2. Acceptance Criteria

A single bulleted list of everything required to close the issue:

- Developer tasks and technical requirements
- UX considerations (field labels, design option names, UI behavior)
- Accessibility: flag anything that needs WCAG 2.1 AA validation
- Documentation: note if existing docs need updating or new docs need creating

---

### 3. Priority

| Priority | When to use |
|----------|-------------|
| **Hotfix** | Critical issue breaking core functionality or accessibility. Immediate deployment required. |
| **High** | Significantly impacts user experience or blocks key workflows. |
| **Medium** | Improves platform usability or addresses moderate user pain points. |
| **Low** | Nice-to-have enhancement with minimal user impact. |

---

### 4. Size

| Size | Definition |
|------|------------|
| **XS** | Single file change or quick setting adjustment. < 1 hour |
| **S** | Minor feature update or simple block modification. 1–4 hours |
| **M** | New block component or moderate platform enhancement. 1–2 days |
| **L** | Complex feature with multiple components or significant UX changes. 3–5 days |
| **XL** | Major platform addition requiring design system updates and extensive testing. 1–2 weeks |

---

### 5. Type

| Type | When to use |
|------|-------------|
| **AI** | Work related to the Beacon AI chatbot |
| **Bug** | An unexpected problem or behavior |
| **Communications** | Work under the Communications workstream |
| **Feature** | A request, idea, or new functionality |
| **Task** | A specific piece of work |
| **Vendor/Supported Builds** | Websites built by vendors or supported by the YaleSites team |

---

### 6. Labels

Apply all relevant labels: `ai-engine` `feedback` `vendor-build` `accessibility-bug` `opac`

---

## Grooming Existing Stub Tickets

1. Read the existing issue body — preserve anything already written
2. Identify what's missing
3. Search the relevant repos for context if the work is technical
4. Fill in missing fields following the format above
5. Use `mcp__github__update_issue` on `yalesites-org/YaleSites-Internal` — **append or replace only missing sections**, never overwrite existing content

---

## Quality Bar

- [ ] Description is jargon-free and makes sense to a non-developer
- [ ] Acceptance criteria covers dev, UX, accessibility, and docs
- [ ] Priority reflects actual user/platform impact (don't default to Medium)
- [ ] Size is realistic — if unsure, err toward larger
- [ ] Type is set
- [ ] Relevant labels are applied
