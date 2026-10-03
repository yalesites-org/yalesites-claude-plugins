---
name: github-screenshots
description: "Put a screenshot into a YaleSites GitHub issue or comment without anyone dragging it in by hand. `gh` and API tokens cannot upload images, so this commits the image to the `screenshots` branch of yalesites-org/YaleSites-Internal and returns an <img> tag to paste into the body. Use whenever a screenshot belongs on a YaleSites-Internal ticket or comment: a bug repro, a punch list, proof that PR work behaves as described, a before/after, a review-run result, or an image the user pasted into chat. Invoked by the ticket, ticket-sync and pr-feedback skills, and directly on requests like 'add this screenshot to the ticket', 'post these screenshots on 1785', or 'attach proof to the issue'. Refuses public repos, where the image would show as broken."
---

# Posting screenshots to GitHub

`gh` and API tokens cannot upload images to GitHub. The drag-and-drop upload in a comment box
only works from a logged-in browser. `scripts/post-screenshot.py` is the workaround: it commits
the image to the `screenshots` branch of `yalesites-org/YaleSites-Internal` and prints an `<img>`
tag to paste into the issue body or comment. The images live in the same repo as the tickets
that show them, so they stay together.

```bash
python3 scripts/post-screenshot.py <image> \
  --ticket yalesites-org/YaleSites-Internal#1785 \
  --alt "Results & filters tab renders blank on an existing People block" \
  --slug item5-results-filters-blank
```

From another skill in this plugin, the path is `../github-screenshots/scripts/post-screenshot.py`.

It prints one line, for example:

```html
<img width="600" alt="Results &amp; filters tab renders blank on an existing People block" src="https://github.com/yalesites-org/YaleSites-Internal/raw/<sha>/YaleSites-Internal/1785/2026-10-02-item5-results-filters-blank.webp" />
```

## Where it works

| Target | Works? | Why |
|---|---|---|
| `yalesites-org/YaleSites-Internal` issues and comments | Yes | Same repo, same audience (every org member) |
| Public repos: `yalesites-project`, `component-library-twig`, `atomic`, `tokens`, `yalesites-claude-plugins` | **No** | Outside readers get a broken image. The script refuses with exit code 3 |
| Notification emails | No | Emails don't carry a GitHub login. Write the comment so it still reads without the image |

Proof for a PR in a public repo goes on its linked YaleSites-Internal issue. When the script
refuses a public repo, there are two options:

1. The user drags the image in by hand.
2. If the PR has a linked YaleSites-Internal issue, post the screenshot there and link that
   comment from the PR.

Ask the user which one they want. Don't pick for them.

## Rules

- **Always pass a real `--alt`.** Say what the screenshot shows, not "screenshot". The script
  rejects an empty one.
- **Images pasted into chat work.** The app saves them to a local temp folder, so pass that file
  path. PNG, JPG, WebP and GIF all render, up to 5MB.
- **Posting is still a GitHub write.** The upload only adds a commit to the `screenshots` branch.
  The comment that shows the image needs the same confirmation as any other comment.
- **Look before you post.** Open the image and check it shows what the alt text says. A wrong
  screenshot misleads more than a missing one.
- **Never delete the `screenshots` branch, or move or delete files on it.** Old tickets link to
  them, and a deleted branch lets GitHub drop the commits behind every link. The script never
  overwrites a file either: on a name clash it adds `-2`, `-3`, and so on.
- **Never commit screenshots to `main`.** The script always targets the `screenshots` branch.
- **No secrets in frame.** No passwords, tokens, `drush uli` links or personal data visible in the
  image. The repo is private, but it's readable by the whole org and kept forever.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Uploaded. The `<img>` tag is on stdout |
| 2 | Bad input: ticket reference, file type, size over 5MB, empty alt text |
| 3 | Target repo is public, so nothing was uploaded |
| 4 | A `gh` call failed (not logged in, no access, network, `screenshots` branch missing) |

`--dry-run` runs every check, including the public-repo check and the name-clash lookup, and
prints the path it would use without uploading anything.

## Background

Tested 2026-10-02 (yalesites-org/YaleSites-Internal#1865). `github.com/.../raw/...` links aren't
routed through GitHub's image proxy, so the viewer's browser sends its own GitHub login and the
private image loads. `raw.githubusercontent.com` links don't send it, so they render broken. The
script pins each link to the commit that added the file, so it survives a later move.
