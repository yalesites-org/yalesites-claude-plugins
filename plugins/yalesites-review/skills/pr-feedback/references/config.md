# Reviewer config

Per-person settings for `pr-feedback`, kept out of the skill so the same skill works for anyone.
The file is optional. It sits next to the reviewer profile:

```
~/.claude/yalesites/pr-feedback/config.json
```

Read it once at the start of a run:

```bash
cat ~/.claude/yalesites/pr-feedback/config.json 2>/dev/null
```

- **No file:** use every default below. This is a normal state, not an error. Say nothing.
- **A key is missing:** use that key's default.
- **The file is not valid JSON:** say so in one line, then use every default.
- **An unknown key:** ignore it.

Batch and prep runs read it once, in the parent session, and pass the values down, the same way
they resolve the reviewer once.

## Keys

| Key | Default | What it does |
|---|---|---|
| `reviewer_login` | `gh api user -q .login` | The GitHub login this review runs as. Used to match the role map, to pick the other approver in the UICL two-approval check, and as the assignee for follow-up tickets. Set it only to the account `gh` posts as. It helps when `gh` is not logged in |
| `brief_skill` | none | A skill that writes the pre-review brief instead of `pr-brief`. Called as `/<brief_skill> <repo>#<number> --dry-run`. See `brief-format.md` |
| `brief_dir` | `~/.claude/yalesites/pr-feedback/briefs` | Where briefs are read from and where `pr-brief` writes. The legacy folder `~/.claude/yalesites/pr-prereview/briefs` is always read too |
| `voice_skill` | none | A personal writing-voice skill to apply to posted text, if it is installed. With none set, use a personal voice skill if one exists, else a plain, direct tone. The "I, not we" rule for PR feedback wins over any voice skill |
| `calibration` | `true` | Whether the review board seals guesses and copies answers for calibration (`review-board.md`, "Calibration"). `false` starts the board server with `--no-calibration` |

## Example

```json
{
  "brief_skill": "pr-prereview",
  "voice_skill": "michael-voice",
  "calibration": true
}
```

Everything not listed takes its default. A teammate with no file at all gets the full review:
`pr-brief` writes the brief, the login comes from `gh`, and the tone is plain.

## What does not belong here

Team data stays in the plugin, where everyone gets the same answer:

- The login to review dimensions map, and the UICL required approvers: `reviewer-roles.md`.
- What one person reviews and how they like it phrased: the reviewer profile
  (`reviewer-profile.md` in the same folder, written by the `reviewer-profile` skill).
