# YaleSites Claude Plugins

A Claude Code plugin marketplace for the Yale ITS Digital Experiences team.

> **Important:** Review a plugin before installing. The YaleSites core team
> reviews all plugins in `/plugins/`. Plugins can include MCP servers, skills,
> and other executable components — only install plugins you trust.

## Available Plugins

| Plugin | Description | Install command |
|---|---|---|
| [yalesites](plugins/yalesites/) | Deep expertise on the YaleSites Drupal 10 platform | `/plugin install yalesites@yalesites-claude-plugins` |
| [yalesites-product](plugins/yalesites-product/) | Release prep, ticket grooming, and UX research workflows for the product team | `/plugin install yalesites-product@yalesites-claude-plugins` |

## Installation

### 1. Register this marketplace (once per machine)

Open Claude Code and run:

```
/plugin marketplace add yalesites-org/yalesites-claude-plugins
```

### 2. Browse available plugins

```
/plugin discover
```

### 3. Install a plugin

```
/plugin install yalesites@yalesites-claude-plugins
```

## Structure

- **`/plugins`** — Core team-maintained plugins, reviewed by
  `@yalesites-org/claude-core-team` before merge
- **`/external_plugins`** — Community plugins (not yet open for submissions)

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the plugin contract,
versioning convention, and submission process.

## License

See individual plugin directories for license information.
