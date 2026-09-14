# Preview URLs and Testing Links

Two of the four repos build a disposable environment where a change can actually be seen. A
testing step that says "verify the accordion collapses" makes the reviewer go find that
environment, then go find an accordion. A testing step that **links the words to the exact
route or story** drops them on the page with the work already in front of them.

So: when a step names a place, link it. Not every step needs a link — "confirm no console
errors" has nowhere to point — but the step that starts the job almost always does.

## Which environment tests which repo

| Repo changed | Test it on | URL |
|---|---|---|
| `yalesites-project` | Pantheon multidev, built by the `Deploy to Pantheon` job | `https://pr-<N>-yalesites-platform.pantheonsite.io` |
| `component-library-twig` | Netlify deploy preview of Storybook | `https://deploy-preview-<N>--dev-component-library-twig.netlify.app` |
| `atomic` | the multidev of its **cross-linked yalesites-project PR** | that PR's multidev URL |
| `tokens` | usually nothing — see below | often no link to give |

**Only yalesites-project and component-library-twig build a preview of their own.** Neither
`atomic` nor `tokens` has a deploy workflow, so a change there is seen through a companion
PR's environment.

**An atomic PR should be cross-linked to a yalesites-project PR, and that PR's multidev is
the one to target.** This is not a special case to work around — Step 3 already detects the
matching-name branch and Step 6 already writes the `Other work completed in:
yalesites-org/yalesites-project#NNN` line, so the number needed for the URL is the number
that line carries. yalesites-project's `build_frontend` requires `dev-<branch>` of atomic
when that branch exists, which is what puts the theme change into the multidev. If an atomic
change has no companion yalesites-project PR, the gap is the missing PR, not the missing
link: an atomic change is not reviewable outside a site that renders it, so raise that rather
than shipping testing steps with nowhere to go.

**A tokens PR usually has no site to point at.** Tokens reaches the multidev only
indirectly, through the CLT branch that consumes it, so unless companion CLT and
yalesites-project PRs exist there is genuinely nothing to link — say so in the step instead
of linking a URL that will 404.

**`<N>` is the PR number of the repo that owns the environment, not the PR you are
writing.** The multidev URL always takes the yalesites-project PR number and the Netlify
URL always takes the component-library-twig PR number. An atomic PR linking to a multidev
uses the *yalesites-project* number; a cross-repo pair links to both environments, each
with its own number.

`yalesites-platform` is the Pantheon site behind the canonical `yalesites-org/yalesites-project`
repo. Do not substitute a local checkout's `.lando.local.yml` `config.site` — that is the
DB source for local work, not the CI deploy target.

## Ordering: the numbers only exist after the PRs do

You cannot write a real URL into a body you have not created yet. Handle it in the step
that already rewrites bodies:

1. **Step 5** — draft and create the PRs, companions first, yalesites-project last.
2. **Step 6** — you are already editing each body to add the cross-repo links. Substitute
   the real PR numbers into the testing-step URLs in the same `gh pr edit`.

Never publish a body still containing `<N>`, `XX`, or `<PR_NUMBER>`. If you show the user
a draft with placeholders in Step 5, say that Step 6 fills them in.

## Component Library Twig: finding the right story

Storybook ids are derived, so they can be worked out from the source before the preview
finishes building:

- Take `title` from the component's `.stories.js` — e.g. `title: 'Molecules/Accordion'`.
- Lowercase it and collapse every run of non-alphanumeric characters to a single `-`:
  `molecules-accordion`. Nested titles keep every segment: `Molecules/Quotes/Pull Quote`
  becomes `molecules-quotes-pull-quote`.
- If the component has an `.mdx` alongside it with `<Meta ... name="Overview" />`, the
  docs page id is `<slug>--overview` and **that is the page to link** — it carries the
  description, the interactive canvas, and the props table:

  ```
  https://deploy-preview-732--dev-component-library-twig.netlify.app/?path=/docs/molecules-accordion--overview
  ```

- With no `.mdx`, link a single story instead — same slugging on the export name:
  `/?path=/story/<slug>--<export-slug>`.
- Ignore `*.visreg.stories.js` (`.../Visreg` titles). Those are per-theme snapshot
  fixtures, not a page a human reviews.

**Verify rather than trust the derivation.** Once the Netlify preview is up it serves a
full Storybook index at `/index.json` listing every real `docs` and `story` id:

```bash
curl -s https://deploy-preview-<N>--dev-component-library-twig.netlify.app/index.json \
  | python3 -c "import json,sys; print('\n'.join(f\"{v['type']:5} {k}\" for k,v in json.load(sys.stdin)['entries'].items() if 'accordion' in k))"
```

If the preview has not built yet, derive the id and say in the draft that it is unverified
rather than silently shipping a link that may 404 into Storybook's "story not found".

## yalesites-project: finding the right route

Link the route that *starts* the task, not the home page. These are stable:

| To do this | Path |
|---|---|
| Log in with CAS | `/cas` |
| Log in with a local account | `/user/login` |
| Create content | `/node/add/page`, `/node/add/post`, `/node/add/event`, `/node/add/profile`, `/node/add/resource` |
| Find existing content | `/admin/content` |
| Add a reusable block | `/block/add` |
| Site settings hub | `/admin/yalesites` |
| Theme and color dials | `/admin/yalesites/themes` |
| Header / footer | `/admin/yalesites/header`, `/admin/yalesites/footer` |
| Integrations | `/admin/yalesites/integrations` |
| Platform admin | `/admin/platform-admin` |

For anything the PR itself added or moved, **read the path out of the code** rather than
guessing — the route is the source of truth:

```bash
grep -rn "path:" web/profiles/custom/yalesites_profile/modules/custom/<module>/<module>.routing.yml
```

A new config form, a new API endpoint, a new local task — all of them have a literal
`path:` in a `*.routing.yml`, and that string is the link. Same for a new view (`path` in
the `views.view.*.yml` display) and a new menu item (`route_name` in
`*.links.menu.yml`, resolved through its routing file).

Layout Builder is the exception: its routes need a node id, so link the **node** the
tester should edit (`/node/12/layout`) only if you know the id exists on that multidev.
Otherwise point at `/node/add/page` and let the step say to add the component.

**CAS on a fresh multidev may not round-trip** — the host is new and the redirect may not
be registered. Say `/cas` where CAS is the point of the test; otherwise a local login is
the reliable path, and the tester can mint one with:

```bash
terminus drush yalesites-platform.pr-<N> -- uli
```

## Worked example

A PR touching the accordion component in component-library-twig and wiring it up in
yalesites-project produces two PRs, each linking both environments:

```markdown
### Functional testing steps:
- [ ] In Storybook, open the [Accordion overview](https://deploy-preview-732--dev-component-library-twig.netlify.app/?path=/docs/molecules-accordion--overview)
      and confirm each item opens and closes with the heading as the trigger
- [ ] [Log in to the multidev](https://pr-1550-yalesites-platform.pantheonsite.io/cas),
      [create a new Page](https://pr-1550-yalesites-platform.pantheonsite.io/node/add/page),
      and add an Accordion component with three items
- [ ] Confirm the saved page renders all three items collapsed
- [ ] Check the browser console for errors on both

References yalesites-org/YaleSites-Internal#1543
```
