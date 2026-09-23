# Researching a YaleSites feature from the code

The goal is to describe what shipped, not what was planned. Everything below lives in `yalesites-org/yalesites-project` on the `develop` branch.

## Finding the implementing PR

The ticket usually lives in `yalesites-org/YaleSites-Internal` and names the PR (e.g. "shipped in yalesites-project#1288"). If it doesn't, search closed PRs in `yalesites-project` for the feature name or the internal issue number.

Read the PR body for the shape of the work and the functional testing steps. Those steps are a good inventory of user-visible behavior. Treat them as a map, then confirm each claim in the code.

Get the file list before the diff. `get_pull_request_files` returns the changed
paths for a PR, and reading the interesting ones with `get_file_contents` costs
far less than paging through a large diff. If the file list itself is too big to
return, fall back to `gh pr view <number> --repo yalesites-org/yalesites-project
--json files`, which you can pipe through `jq` or save and grep.

## Where things live

Custom platform code sits under:

```
web/profiles/custom/yalesites_profile/
├── config/sync/                     # site config, including views
│   ├── views.view.<name>.yml
│   └── user.role.<role>.yml         # which permissions each role holds
└── modules/custom/
    ├── ys_core/                     # dashboard, settings forms, search, alerts
    │   ├── src/Form/*.php           # settings forms: field labels, defaults, #access
    │   ├── src/Controller/*.php
    │   ├── templates/*.html.twig     # section headings, conditional rendering
    │   ├── config/install/*.yml      # shipped default values
    │   └── ys_core.routing.yml       # paths and their permission requirements
    ├── ys_ai/
    ├── ys_alert/
    ├── ys_localist/
    └── ys_campus_groups/
```

## What each file answers

**`*.routing.yml`:** the path, the page title, and the `_permission` requirement. This is where you learn what it takes to reach a page.

**`user.role.*.yml`:** the permission list for a role. To answer "can a site admin see this?", find the route's permission, then grep for it in `user.role.site_admin.yml`. Most YaleSites admin pages sit behind `yalesites manage settings`, which **site administrators hold**. Do not assume an `/admin/yalesites/*` path is internal-only.

**Form classes (`src/Form/*.php`):** `buildForm()` gives you exact field labels, `#description` help text, `#default_value`, `#min`/`#max`, and `#states` visibility conditions. An `#access` callback on a fieldset is how individual sections get gated to a role; check whether the gate is on the whole route or only on one fieldset, because that changes what a site admin actually sees.

**Views config (`views.view.*.yml`):** for any table or list. Grep for `label:` to get column headings in order, `items_per_page` for the row limit, `content:` under `empty:` for the empty-state text, `sorts:` for default ordering, and `filters:` for what's included (e.g. `status: '1'` means published only). `path:` under `alter:` tells you where a linked title goes.

**Twig templates:** section headings in reading order, and `{% if %}` guards showing what disappears when a setting is off.

**`config/install/*.yml`:** the values a fresh site ships with.

## The permission trace, worked

For the editorial Dashboard:

1. `ys_core.routing.yml` → `ys_core.admin_dashboard` requires `yalesites manage settings`
2. `user.role.site_admin.yml` → contains `yalesites manage settings`
3. Therefore site administrators can reach it

And for the settings page's internal fieldset:

1. `DashboardSettingsForm::buildForm()` → the `source` fieldset has `'#access' => $this->isPlatformAdmin()`
2. `isPlatformAdmin()` → true only for uid 1 or the `platform_admin` role
3. Therefore only that one fieldset is internal; the rest of the page is not

That distinction is exactly the kind of thing a ticket summary flattens and a reader would trip over.

## Sanity checks before you write

- Does every label you used appear verbatim in the code?
- Have you traced the permission for every "only X can do this" sentence?
- Are your row limits and defaults from config, not from the PR description?
- Does anything you're documenting only exist on an unmerged branch?
