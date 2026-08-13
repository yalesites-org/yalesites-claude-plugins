# Update hooks and deploy ordering — the long version

Read this when an update hook is not sticking, when a contrib bump ships config
changes, or when deciding between `hook_update_N`, `hook_post_update_NAME`, and
`hook_deploy_NAME`.

## The verified order

`drush deploy` is a thin orchestrator. From
`vendor/drush/drush/src/Commands/core/DeployCommands.php`, `deploy()`, lines
43-64 (Drush 13.7.4):

| Line | Step | What it runs |
|---|---|---|
| 44 | `drush updatedb` | all pending `hook_update_N()`, then all pending `hook_post_update_NAME()` |
| 48 | `drush config:import` | re-applies everything in `config/sync` to active config |
| 51 | `drush cache:rebuild` | |
| 54 | `drush deploy:hook` | all pending `hook_deploy_NAME()` |
| 60-63 | `drush cache:warm` | guarded by `version_compare($version, '11.2-dev', '>=')` — **skipped on core 10.6.13** |

Both update phases live inside `updatedb`: `UpdateDBCommands::updateDoOne()`
dispatches `MODULE_update_N`, and `UpdateDBCommands::updateDoOnePostUpdate()`
dispatches `MODULE_post_update_NAME`. Neither runs after config import.

`deploy:hook` uses its own `UpdateRegistry` (`DeployHookCommands::getRegistry()`,
line 41) keyed separately from post-updates, scanning `MODULE.deploy.php`. That
registry is why a deploy hook and a post-update with the same name do not
collide, and why deploy hooks each run exactly once per environment.

## Why "update hook writes config" is a trap

```
updatedb        active config: old_key -> new_key   (your hook, or contrib's)
config:import   active config: new_key -> old_key   (stale config/sync wins)
```

Config import is not additive. It reconciles active config against the exported
files, so anything your update hook changed that is *also* represented in
`config/sync` is reverted — every deploy, forever, not just the first one.

This is invisible locally if you only ever run `drush updatedb` while testing.
Reproduce with the real command: `npm run confim` (== `lando drush deploy`).

## Worked example: the Mailchimp Transactional API key

**Symptom** (YaleSites-Internal #1340): visitors submitting a webform saw
"Failed to load Mailchimp Transactional API Key" followed by core's "Unable to
send email". Intermittent-looking, but actually deterministic after any deploy.

**Cause chain:**

1. `mailchimp_transactional` 1.2.0 renamed its config key
   `mailchimp_transactional_api_key` to `api_key`.
2. The module shipped `mailchimp_transactional_update_8001()` to migrate the key
   in active config. That ran at step 1 and worked.
3. `config:import` at step 2 re-applied the exported `config/sync`, which still
   carried the **old** key name — reintroducing `mailchimp_transactional_api_key`
   and dropping `api_key`.
4. The Key module / Pantheon Secret wrote the credential into the old key. New
   module code read `api_key`, found nothing, and resolved the API key empty.

The module's own update hook was correct. The repo's exported config was what
made it wrong.

**Fix, both halves:**

1. Rename the keys in `config/sync` to the new schema, preserving values, so
   config import stops fighting the update hook. Practically: run the update
   locally, `npm run confex`, inspect the diff, commit it.
2. Repair the wiring the contrib hook could not reach — the Key entity's
   `config_override.config_item` pointer, and any custom `hook_form_*_alter()`
   that referenced the old field name by string.

**Regression guard:** a plain unit test that loads the exported YAML and asserts
no legacy-prefixed keys remain. It needs no database and runs in the Unit suite,
so it is cheap. Note that it will not run in CI on this project (CI executes no
PHPUnit) — it is a local and code-review guard only.

## Choosing a hook

**`hook_update_N()`** — `MODULE.install`. Numbering is
`<major><minor><sequence>`, e.g. `10001` for the first Drupal 10 update. Takes
`&$sandbox` for batched work. Use for schema changes and stored-data migration.
Runs before config import.

**`hook_post_update_NAME()`** — `MODULE.post_update.php`. Runs after every
`hook_update_N` in the same `updatedb` pass, so the schema is fully current and
the entity API is safe to use. The function *name* is the registry key, so it
cannot be renumbered or renamed after it has run anywhere. Still before config
import.

**`hook_deploy_NAME()`** — `MODULE.deploy.php`. A Drush concept, not core. Runs
after config import and a cache rebuild. **The only safe place for imperative
work that reads or writes config**, or that depends on config import having
finished.

Prior art in this repo — read one before writing a new one:

- `ys_core/ys_core.deploy.php`
- `ys_themes/ys_themes.deploy.php`
- `ys_layouts/ys_layouts.deploy.php`
- `ys_views_basic/ys_views_basic.deploy.php`

`ys_core_deploy_10001()` is the canonical shape: it guards on current state
(`if ($vocab && $vocab->get('name') === NULL)`) so re-running is harmless, edits
config via `\Drupal::configFactory()->getEditable()`, and invalidates the
discovery cache when done. Deploy hooks run once per environment, but writing
them idempotently costs nothing and survives a registry reset.

## Checklist for a config-touching change

- [ ] Decide the hook by *when it must run relative to config import*, not by habit.
- [ ] If it touches config, it belongs in `.deploy.php` — or the change belongs in `config/sync` and needs no hook at all.
- [ ] Export with `npm run confex` and commit the `config/sync` diff.
- [ ] Verify with `npm run confim` (full `drush deploy`), not `drush updatedb` alone.
- [ ] Re-run `npm run confim` a second time and confirm the state holds — a one-deploy fix that reverts on the next deploy looks identical to a working one on the first pass.
- [ ] `composer code-sniff` before committing.
