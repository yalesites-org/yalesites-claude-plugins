---
name: drupal-conventions
description: Drupal 10 conventions for YaleSites custom code — hook naming and registration, services and dependency injection, config schema, and update hooks with their drush deploy ordering. Use this whenever writing or reviewing PHP under web/{modules,themes,profiles}/custom: a hook implementation, a .services.yml entry, config/schema YAML, or a hook_update_N / hook_post_update_NAME / hook_deploy_NAME. Reach for it just as readily when something config- or hook-related is misbehaving rather than being written — a config change that reverts after every deploy or drush cim, an update hook whose edits do not stick, a newly added hook that never fires, an API key or Key entity that resolves empty after a release, a contrib bump that shipped its own update hook, or a question about whether updatedb runs before or after config import. Use it even if the user never says "convention", "hook", or "deploy order".
---

# Drupal conventions (YaleSites)

Platform facts these rules are pinned to (verified, not assumed):

| Fact | Value | Where confirmed |
|---|---|---|
| Drupal core | 10.6.13 | `web/core/lib/Drupal.php:78` |
| Drush | 13.7.4 | `composer.lock` (`drush/drush`) |
| OOP `#[Hook]` attribute | **not present in this core** | `web/core/lib/Drupal/Core/Hook/Attribute/` does not exist |
| `autowire:` in services.yml | supported | `web/core/lib/Drupal/Core/DependencyInjection/YamlFileLoader.php:42,259` |
| Custom module root | `web/profiles/custom/yalesites_profile/modules/custom/ys_*` | project CLAUDE.md |
| `npm run confim` | `lando drush deploy` | `scripts/local/confim.sh` |

Re-check the core version before applying anything version-sensitive; these were
read on 2026-07-27 in `yalesites-claude`.

---

## 1. Hooks

Hooks here are **procedural**. The `#[Hook]` attribute does not exist in this
core, so do not reach for it — put implementations in `MODULE.module`,
`MODULE.install`, or `MODULE.theme`.

**Naming** is mechanical: replace `hook` with the module machine name.

| Hook | Implementation in `ys_core` |
|---|---|
| `hook_form_alter` | `ys_core_form_alter(&$form, FormStateInterface $form_state, $form_id)` |
| `hook_form_FORM_ID_alter` | `ys_core_form_node_page_form_alter(...)` |
| `hook_ENTITY_TYPE_presave` | `ys_core_node_presave(EntityInterface $entity)` |
| `hook_preprocess_HOOK` | `ys_core_preprocess_block(&$variables)` |
| `hook_theme_suggestions_HOOK_alter` | `ys_core_theme_suggestions_block_alter(array &$suggestions, array $variables)` |

**Docblock wording is enforced.** DrupalPractice requires the exact phrasing,
naming the *generic* hook, not your function:

```php
/**
 * Implements hook_form_FORM_ID_alter().
 */
function ys_core_form_node_page_form_alter(array &$form, FormStateInterface $form_state, $form_id) {
```

Getting this line wrong is a `composer code-sniff` failure, and code-sniff fails
on warnings too.

### The gotcha that costs a round trip

**A brand-new hook implementation does not run until caches are rebuilt.** Drupal
caches the registry of which module implements which hook. Add a `hook_*`
function that did not previously exist in that module and the site behaves as if
it is not there — while the code reads correctly and unit tests pass.

```bash
lando drush cr
```

Run that *before* concluding the logic is wrong or asking anyone to re-test.
Editing the body of an *existing* hook does not need it; adding a new function
does.

---

## 2. Services and dependency injection

Declare in `MODULE.services.yml`; service IDs are namespaced by module:

```yaml
services:
  ys_core.breadcrumb_builder:
    class: Drupal\ys_core\YsCoreBreadcrumbBuilder
    arguments: ['@entity_type.manager', '@config.factory']
    tags:
      - { name: breadcrumb_builder, priority: 100 }
```

Injection point depends on what you are building:

- **Controllers, forms, blocks** — `ContainerInjectionInterface` with
  `public static function create(ContainerInterface $container): static`.
- **Plugins** (blocks, field formatters, Integration plugins) —
  `ContainerFactoryPluginInterface` with
  `create(ContainerInterface $container, array $configuration, $plugin_id, $plugin_definition)`.
  Remember to pass `$configuration, $plugin_id, $plugin_definition` through to
  the constructor.
- **Event subscribers** — tag `{ name: event_subscriber }` and implement
  `EventSubscriberInterface::getSubscribedEvents()`.

**`\Drupal::` static calls belong in procedural code only** — `.module`,
`.install`, `.theme`, `.deploy.php` files, and inside a `create()` factory body.
In a class that has a constructor you can inject into, DrupalPractice flags the
static call. Never inject the container itself to dodge this.

`autowire: true` is supported by this core, but the existing modules declare
arguments explicitly — match that unless you have a reason not to.

---

## 3. Config schema

Every key in shipped config needs a schema entry, or config inspection and
strict-schema kernel tests fail. Schema lives in
`MODULE/config/schema/MODULE.schema.yml`.

```yaml
ys_core.settings:
  type: config_object
  label: 'YaleSites core settings'
  mapping:
    site_name_prefix:
      type: label
      label: 'Site name prefix'
    enabled_features:
      type: sequence
      label: 'Enabled features'
      sequence:
        type: string
```

- **`config/install/`** ships when the module is installed; **`config/optional/`**
  installs only when its dependencies are already met.
- **Config entities** need `config_export` in the plugin annotation *and* a
  matching `MODULE.entity_type.*` schema entry.
- Type cheatsheet: `config_object` (simple settings), `mapping` (fixed keys),
  `sequence` (list), `label` (short translatable), `text` (long translatable),
  `string`, `integer`, `boolean`.

**Site-level exported config is separate** from module `config/install/`. It
lives in `web/profiles/custom/yalesites_profile/config/sync/` and is exported
with `npm run confex` — always via the npm script, never bare `drush cex`, so the
paths resolve correctly.

Adding or changing a component style option is a config change: edit
`ys_themes/config/install/ys_themes.component_overrides.yml`, then export.

---

## 4. Update hooks and deploy ordering

**This is the section that bites.** `drush deploy` runs database updates
**before** config import, so an update hook that writes to active config is
silently undone on every deploy.

Verified order, read from
`vendor/drush/drush/src/Commands/core/DeployCommands.php:43-64`:

```
1. drush updatedb        <- hook_update_N, then hook_post_update_NAME
2. drush config:import   <- re-applies config/sync, OVERWRITING step 1's config edits
3. drush cache:rebuild
4. drush deploy:hook     <- hook_deploy_NAME  (MODULE.deploy.php)
5. drush cache:warm      <- core >= 11.2 only; does NOT run on this 10.6.13 platform
```

`npm run confim` is exactly `lando drush deploy`, so local config imports follow
the same ordering as a real deploy.

### Picking the right hook

| You need to… | Use | Runs |
|---|---|---|
| Change a DB schema, migrate stored data | `hook_update_N()` in `MODULE.install` | step 1 |
| Touch entities/content after schema updates settle | `hook_post_update_NAME()` in `MODULE.post_update.php` | end of step 1 |
| **Act on config, or on anything config import would clobber** | `hook_deploy_NAME()` in `MODULE.deploy.php` | step 4 |

The project already uses the deploy-hook pattern — `ys_core`, `ys_themes`,
`ys_layouts`, and `ys_views_basic` each ship a `.deploy.php`. Follow
`ys_core_deploy_10001()` as the model rather than inventing a new shape.

### The failure mode to watch for

When you bump a **contrib** module whose own `hook_update_N` renames its config
keys, that hook fires at step 1 and config import at step 2 puts the old keys
straight back from your stale `config/sync`. The site then reads a key the new
code no longer writes.

Fixing it takes two moves, and the first is the one people forget:

1. Bring exported `config/sync` to the **post-migration** state — rename the keys
   there, preserving values. Run the update locally, `npm run confex`, and commit
   the resulting diff.
2. Update YaleSites-specific wiring the contrib hook cannot see — Key
   `config_override` `config_item` values, custom `hook_form_*_alter` field names.

A unit test that parses the exported YAML and rejects legacy-prefixed keys stops
this recurring.

Worked example and the full incident write-up:
`references/update-hooks-and-deploy.md`.

---

## Before calling Drupal work done

- `composer code-sniff` (Drupal **and** DrupalPractice, fails on warnings) over
  the whole custom tree — a per-file pass is not the same gate as CI.
- `lando drush cr` if you added a new hook implementation.
- If you changed config, `npm run confex` and commit the `config/sync` diff.
- **CI does not run PHPUnit on this project** — `composer unit-test` is a stub.
  Never say a test will catch a regression in CI. See the `phpunit-drupal` skill.
