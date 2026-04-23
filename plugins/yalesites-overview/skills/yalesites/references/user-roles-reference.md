# YaleSites User Roles & Editorial Workflow Reference

Source: https://yalesites.yale.edu/editorial-workflow

---

## The Three User Roles

YaleSites has three user roles. Users who were already on the platform before these roles were introduced remain **Site Administrators**.

### Site Administrator
Full control over the site — content, layout, configuration, and users.

### Editor
Can create, edit, and publish content. Cannot assign roles or change site-wide settings.

### Contributor
Can create and edit content but **cannot publish**. When a Contributor edits already-published content, an unpublished draft is created that must be approved and published by an Editor or Site Administrator.

---

## Permissions by Role

| Task | Site Administrator | Editor | Contributor |
|---|---|---|---|
| Assign roles | ✓ | | |
| Publish pages | ✓ | ✓ | |
| Edit pages | ✓ | ✓ | ✓ |
| Create new draft | ✓ | ✓ | ✓ |
| View any unpublished content | ✓ | ✓ | ✓ |
| View latest version | ✓ | ✓ | ✓ |
| Restore pages | ✓ | ✓ | |
| Restore to draft | ✓ | ✓ | |
| Delete pages | ✓ | ✓ | |

**To change a user's role:** Top toolbar → People → Edit (for the user) → update their role.

---

## Content Moderation States

| State | Visible to public? | Notes |
|---|---|---|
| **Draft** | No | Default state for all new content and new revisions |
| **Published** | Yes | Content is live on the site |
| **Archived** | No | Content is hidden but preserved — recommended over deleting |

---

## Moderation Controls Sidebar

On unpublished content, a sidebar appears (access via the "Tasks: Draft" button in the second toolbar). Available options depend on role:

- **View Live Content** — if the page has a published version, view it
- **Edit the Draft** — go to Manage Settings to edit
- **Delete the Draft** — remove the draft
- **Publish this Draft** — make the draft live (Editors and Admins only)
- **Add a Log Message** — annotate the revision history
- **Show Revisions** — view the full revision history
- **Layout Builder** — edit the draft's layout and content
- **Clone this Draft** — create a copy of the draft

---

## Practical Implications for Common Scenarios

**"Why can't I see the Publish button?"**
The user is likely a Contributor. They can save drafts but cannot publish. An Editor or Administrator must publish on their behalf.

**"I edited a published page and now it looks unpublished."**
When a Contributor edits a published page, a new draft is created — the published version is still live. An Editor or Admin needs to review and publish it.

**"How do I add someone to my site?"**
Top toolbar → People → Add user (or invite via CAS NetID). Then set their role. Only Site Administrators can assign roles.

**"My page is archived — can I get it back?"**
Yes. Go to the content list (Content in the top toolbar), find the archived item, and change its moderation state back to Draft or Published.
