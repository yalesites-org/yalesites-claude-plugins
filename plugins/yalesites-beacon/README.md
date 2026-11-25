# yalesites-beacon

Testing tools for Beacon, the YaleSites AI chatbot.

## Who it's for

Anyone testing Beacon's answers for a site or comparing Beacon against another setup.

## Installation

```
/plugin install yalesites-beacon@yalesites-claude-plugins
```

Add `yalesites` too if you want platform context while writing questions.

## Skills

| Skill | Use it for |
|---|---|
| `beacon-question-set` | A quick content-accuracy question set for testing Beacon against one site |
| `beacon-test-bank` | A full tiered test bank with guardrails, safety, and edge-case coverage |
| `beacon-comparison-review` | Analyzing a Beacon AI Tester A/B comparison JSON export |

`beacon-comparison-review` can post its summary to GitHub. It follows the shared writing standard
bundled under `skills/beacon-comparison-review/references/`, generated from `standards/` at the
repo root by `bash scripts/sync-standards.sh`.

## Maintainer

Yale ITS Digital Experiences,
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)
