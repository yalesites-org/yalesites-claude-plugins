# Raising a decision or a follow-up

Load this when the user wants to raise or resolve a `needs-decision` or `follow-up` on an issue or PR ("flag this for April to follow up", "this needs a decision from Michael"), when grooming turns up an unresolved debate, or when a new embed provider needs approval. The exact block formats live in `references/routing.md` ("Waiting on a person"). Read that section too.

---

When work can't go on until a person does something, mark it so it can't get lost. Two labels cover it, and both are defined in `references/routing.md`:

- **`needs-decision`:** someone has to make a choice. Replaces `question`. Don't apply `question` to anything new.
- **`follow-up`:** someone owes an action, such as a reply, a test, a review, or a check-in with a requester.

Each label goes with a block, in the issue body or a new comment, that names one handle, what they owe, and a date. Use the block formats in `references/routing.md` exactly, since other tools parse them (the router routine and the work dashboard, if your team runs them). Then add the label. Ask the user for the handle and the date if they didn't give them. Offer 5 working days out as the default date.

To close one out, post the resolution comment from `references/routing.md` and remove the label. The label is the switch: a block with no label counts as closed.

Comments can only be added, never edited in place. If a block needs correcting, post a new comment rather than trying to revise the old one.

This works on PRs in the code repos too. Use `gh pr comment` and `gh pr edit --add-label`. The GitHub connector is read-only on `yalesites-project`, so it can't post there. If `gh` isn't available, draft the comment text and hand it to the user to paste in rather than retrying the write.

An open `needs-decision` also blocks the `claude` label (see "Claude pickup" in `references/fields.md`) and holds the ticket where it is: routing does not promote a phase child with an open `needs-decision`.

**New embed providers.** An `Embed:` or `Embed Request:` ticket, or a child of the Embed Requests epic (yalesites-org/YaleSites-Internal#1373), needs a `needs-decision` for `miketullo95` asking whether to add the provider, unless it is a Bug on an embed that already ships or already carries his `## Decision: approved` comment. See "New embed providers" in `references/routing.md` and "Title" in `references/issue-format.md`.
