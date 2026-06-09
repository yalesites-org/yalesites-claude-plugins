# Cross-Repo Workflow

## Multidev companion (component-library-twig or atomic changes)

When changes live entirely in `component-library-twig` or `atomic`, the plan must include a **multidev companion** in `yalesites-project`:

1. Create a matching branch name in `yalesites-project` with a trivial README.md edit
2. Create a PR in `yalesites-project` titled `<issue>: <title> — For multidev only` with label `don't merge`
3. In the `component-library-twig` (or `atomic`) PR:
   - Add the `yalesites-project` PR URL to the **Testing Link(s)** section so reviewers can navigate to the Drupal multidev from the CL PR
   - Add a final **Functional Review Step**: `Test functionality in the [Drupal Multidev](<yalesites-project PR URL>)`
4. The `yalesites-project` PR body should note the companion PR with: `Other work completed in: yalesites-org/component-library-twig#NNN`

## Netlify deploy preview (component-library-twig only)

After the CL PR is created, Netlify will post a deploy preview comment. Once it appears:

1. Check the PR comments for the deploy preview URL: `gh pr view <number> --comments | grep -A5 "deploy preview"`
2. Find the relevant story paths by checking `*.stories.js` files for the components affected:
   - `grep -E "title:|export const" <story-file>` to get the title and export names
   - Storybook URL format: `?path=/story/<title-kebab-case>--<export-kebab-case>` (e.g., `Atoms/Lists` + `TagsList` → `atoms-lists--tags-list`)
3. Update the PR's **Testing Link(s)** to replace the placeholder with direct links to each affected story using the real deploy preview domain
4. Include a link for every place the change is visible — atom story, molecule stories that use it, organism stories that use it
