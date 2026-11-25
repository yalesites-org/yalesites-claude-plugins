# yalesites-migration

A read-only probe of a public source site (Drupal 7 included), mapped against the YaleSites content
model. It produces a migration-path assessment: content type and component mapping, what will not
carry over cleanly, an effort rating, and mechanism options.

## Who it's for

People working on the migration project. It is a finite project, so this plugin lives on its own
rather than in everyone's daily set.

## Installation

```
/plugin install yalesites@yalesites-claude-plugins
/plugin install yalesites-migration@yalesites-claude-plugins
```

`yalesites` is optional but recommended. The assessment uses its platform knowledge.

## Skills

| Skill | Use it for |
|---|---|
| `migration-assessment` | Assessing a source site for migration onto YaleSites |

## Maintainer

Yale ITS Digital Experiences,
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)
