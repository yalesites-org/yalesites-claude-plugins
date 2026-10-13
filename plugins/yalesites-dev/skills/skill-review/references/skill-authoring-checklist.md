# Skill Authoring Checklist

Canonical source. Do not edit the synced copy inside `plugins/`. Edit this file, then
run `bash scripts/sync-standards.sh`. CI fails if the synced copy drifts from this one.

## What this is

Three rounds of review on six skill PRs (yalesites-org/yalesites-claude-plugins#57, #58,
#60, #62, #63, #64) produced about 165 findings. Almost all of them fall into thirteen
defect classes, and the same classes came back in every round. This checklist turns those
classes into checks an author, or their agent, runs before opening the PR.

Every item is a question with a yes or no answer. Under each item, **Why** names the PR
where the defect showed up and what went wrong, so the check does not read as a rule for
its own sake. The `skill-review` skill in `yalesites-dev` walks this list against a branch.

How to use it: diff your branch against `main`, then go through every section against the
changed files. Do the ones with commands by running the commands, not by reading them.

---

## 1. Cross-plugin and cross-skill references

Plugins cannot read each other's files at runtime. A pointer across the plugin boundary
is a request the other plugin may not be there to answer.

- [ ] Every pointer to a skill in another plugin says what to do when that plugin is not
  installed ("If the `yalesites-portfolio` skill is available ... otherwise skip this step").
  **Why:** yalesites-org/yalesites-claude-plugins#63 hard-required a skill from another plugin
  in six files. A user with only `yalesites-product` installed was told to load a skill that
  did not exist and to grep a CSV that resolved to the wrong folder.
- [ ] The guard goes both ways. A pointer from the `yalesites` plugin back to
  `yalesites-product` needs the same "if available" wording.
  **Why:** yalesites-org/yalesites-claude-plugins#63 guarded every pointer in one direction
  and left the reverse pointer bare.
- [ ] A rule the skill needs to act on is stated inline in one line, with the cross-plugin
  pointer as the place for detail. The pointer alone is not enough.
  **Why:** yalesites-org/yalesites-claude-plugins#58 pointed `yalesites-dev` at a reference
  file in the `yalesites` plugin for the only copy of the ADR location rule.
- [ ] A handoff to another skill lands on a step that skill has. Read the target skill and
  name the step.
  **Why:** yalesites-org/yalesites-claude-plugins#64 handed retaken screenshots to
  `yalesites-page-build` to "update the staged draft", but page-build had no step for placing
  an image, and its own rules told it to stop on exactly that page.
- [ ] A handoff does not skip the target skill's safety rules. If the target has production
  rules (never publish, no `drush uli`), the handoff says to follow them.
  **Why:** yalesites-org/yalesites-claude-plugins#64 told release-prep to edit a draft on
  production directly, with none of page-build's guardrails.
- [ ] Before adding a new method, check the sibling skills for one that exists.
  **Why:** yalesites-org/yalesites-claude-plugins#64 said the Playwright CLI had no way to
  point at an element and added 12 lines of DOM injection. `drive-it.md` already used
  `highlight`.
- [ ] No path outside the plugin that a marketplace install will not have (`~/code/...`,
  a local data checkout). If maintainers need it, mark it maintainer-only or give a URL.
  **Why:** yalesites-org/yalesites-claude-plugins#63 sent readers to a local data repo that
  exists on one machine.

## 2. Copied text that drifts

State a rule once and point to it. Every copy is a place the next change forgets.

- [ ] A rule that several skills need lives in one file. The other skills link to it and do
  not restate it. Run `git grep -n` for a distinctive phrase from the rule and count the hits.
  **Why:** yalesites-org/yalesites-claude-plugins#58 put the ADR rule in five places with
  three wordings. The copies had already drifted (`decisions?` in one regex, `decisions` in
  the doc) by round three. yalesites-org/yalesites-claude-plugins#64 restated four screenshot
  rules in a second skill and a third time in release-prep.
- [ ] The same rule is not stated twice in one file.
  **Why:** yalesites-org/yalesites-claude-plugins#58 had the ADR rule in a "Suggested
  approach" bullet and again in its own section of the same SKILL.md.
- [ ] A URL or environment name that two skills cite lives in one reference table
  (`yalesites-pr/references/preview-urls.md` for Pantheon and Netlify URLs).
  **Why:** yalesites-org/yalesites-claude-plugins#64 wrote the RC multidev URL into two
  skills and left it out of the URL table.
- [ ] Two sections that describe the same step agree. Read both after the edit. A change to
  one section of a reference usually has a twin in another section or file.
  **Why:** yalesites-org/yalesites-claude-plugins#57 changed drive-it.md to keep QA users,
  while beyond-ac-checks.md still said to delete them. The same PR said "a `pr-<N>` multidev"
  in one step and "the reviewed PR's own multidev" in another.
  yalesites-org/yalesites-claude-plugins#60 had review-board.md delete a file that
  prep-mode.md said to archive.
- [ ] Merged or regenerated reference files have no near-duplicate entries and no paragraph
  that gives two answers.
  **Why:** yalesites-org/yalesites-claude-plugins#63 shipped "Stat bands as proof" and "Stat
  band as proof" as separate patterns, and a Length paragraph with two different ranges.
- [ ] Copy-pasted paragraphs were rewritten for their new home.
  **Why:** yalesites-org/yalesites-claude-plugins#63 gave Post Feed the Calendar List
  guidance word for word, including "event actions".
- [ ] Duplicated code is a shared function, or the copy is justified in a comment that the
  reviewer can check. Scripts in one folder import shared pieces instead of copying them.
  **Why:** yalesites-org/yalesites-claude-plugins#62 copied a 155-line server with a comment
  saying skills cannot read each other's files, while another script in the same PR read a
  sibling skill's folder through `realpath`. The same PR had one id regex in three files.
- [ ] Two implementations of one format agree. If a script and a page both parse the same
  markdown, they parse it the same way.
  **Why:** yalesites-org/yalesites-claude-plugins#62 had `packet.py` treat `~~~` as a fence
  and the board treat only triple backticks, so the board mangled a file the script wrote
  correctly.
- [ ] A rule that exists to stop something unattended is not two rules that disagree.
  **Why:** yalesites-org/yalesites-claude-plugins#60 said "newest first" and
  "yalesites-project first" for the same cap, with no tie-break.

## 3. Steps and control flow

Read the skill as the agent will: top to bottom, taking each branch.

- [ ] A check that must always run is its own numbered step, not a sub-bullet of a step
  that only runs on one branch.
  **Why:** yalesites-org/yalesites-claude-plugins#58 nested the ADR check under "fetch the
  issue title", so a branch with no issue number skipped it.
- [ ] A rule that applies to several paths is in the shared part of the skill, not inside one
  path.
  **Why:** yalesites-org/yalesites-claude-plugins#58 added an acceptance criterion only in
  the epic flow, so a standalone spike ticket never got it.
- [ ] A step runs after the data it needs exists. Trace every input back to the step that
  produces it.
  **Why:** yalesites-org/yalesites-claude-plugins#58 ran the ADR check before the step that
  found the companion repos. yalesites-org/yalesites-claude-plugins#60 claimed a unit with a
  scope that Step 0 resolved later. yalesites-org/yalesites-claude-plugins#64 put the
  screenshot pass in the phase before the docs that carry the markers were drafted.
- [ ] A step that reads "do Step N exactly as written" was re-read after Step N changed.
  **Why:** yalesites-org/yalesites-claude-plugins#60 had prep mode run Step 1 as written
  after Step 1 gained a check that, in prep mode, hit the run's own claim and stopped it.
- [ ] A detection step covers every marker it is meant to find, not only the one the PR
  added.
  **Why:** yalesites-org/yalesites-claude-plugins#64 looked only for "placeholder" markers,
  so screenshots that were never taken went through the RC window with nothing prompting
  anyone.
- [ ] A commit the skill makes gets pushed by a step that runs after it. "Push if not already
  pushed" skips a branch that was on origin before the new commit.
  **Why:** yalesites-org/yalesites-claude-plugins#58 added a `git rm` commit after the push
  step had already decided the branch was pushed.
- [ ] Every placeholder in a command (`{scratch}`, `{repo}`, `{branch}`) is defined before its
  first use.
  **Why:** yalesites-org/yalesites-claude-plugins#58 used `{scratch}` without ever saying
  what it was.
- [ ] Data a later step needs from a skipped step is carried another way, and the skill
  says how.
  **Why:** yalesites-org/yalesites-claude-plugins#60 let prepped units skip the subagent whose
  return fed two later steps, and the packet did not carry it.

## 4. Commands: allowed-tools and the harness

The harness matches one command against one `allowed-tools` pattern. Anything else prompts,
and an unattended run has nobody to answer the prompt.

- [ ] Every command the skill tells the agent to run matches an entry in `allowed-tools`.
  List the commands from the diff, then check each against the frontmatter.
  **Why:** yalesites-org/yalesites-claude-plugins#58 added `git diff`, `gh repo clone`,
  `git mv`, `git rm`, `git commit`, and `cp` with no matching entries.
- [ ] No `for` or `while` loops in a command the agent must run under `allowed-tools`:
  `for f in ...; do grep ...; done` matches nothing. A pipeline or `&&` chain is allowed only
  when every segment matches an entry on its own (`a | b` needs an entry for `a` and one
  for `b`), so list each segment's entry.
  **Why:** yalesites-org/yalesites-claude-plugins#58 wrote the ADR check as a loop and a
  pipeline with no `grep` entry. In a `--bg` run it hit a prompt nobody answered.
- [ ] Entries are as narrow as the step needs. A bare `Bash(cp *)` or `Bash(git rm *)`
  grants more than one step should.
  **Why:** yalesites-org/yalesites-claude-plugins#58 added broad entries for a single move.
- [ ] No sleep-based waits, foreground or background. To wait for a file or a condition, use
  the `Monitor` tool with an until-condition.
  **Why:** yalesites-org/yalesites-claude-plugins#62 told the agent to run
  `until [ -f ... ]; do sleep 2; done` in the background. The harness blocks that pattern.

## 5. Commands: tested on macOS, as written

Run every command in the diff on a Mac, with the inputs the skill describes. Reading it is
not testing it.

- [ ] `\b` is not used in `git grep -E`. It matches nothing on macOS. Use `-P`, or drop it.
  Checked: `git grep -l -iE '^#.*(\bADR\b)'` prints nothing on a file whose first line is
  `# ADR 1: thing`. The same pattern with `-P` finds it.
  **Why:** yalesites-org/yalesites-claude-plugins#58 shipped a heading match that could
  never match.
- [ ] No `timeout`. It does not exist on macOS. BSD `sed -i` needs an argument (`sed -i ''`).
  `grep -P` is not in BSD grep. Check each GNU-only flag.
- [ ] Commands that redirect into a folder create the folder first.
  **Why:** yalesites-org/yalesites-claude-plugins#62 ran
  `git show ... > "$DIR/1770/README.current.md"` before anything made `$DIR/1770`.
- [ ] The output format of one command matches what the next command compares it to.
  `git grep -l ... {branch}` prints `{branch}:path`. `git diff --name-only` prints `path`.
  **Why:** yalesites-org/yalesites-claude-plugins#58 intersected those two lists, so the
  intersection was always empty.
- [ ] A snippet does what the prose around it says. A "check for one first" rule next to a
  block that runs `user:create` unconditionally is a snippet the agent will copy as written.
  **Why:** yalesites-org/yalesites-claude-plugins#57 had this twice: the create block ignored
  the check, and the rewritten `||` block reused any user even where the prose said not to.
- [ ] Quoting survives substitution. A selector inside a bash double-quoted string breaks on
  its own double quotes. A selector inside single-quoted JS breaks on single quotes. Fill in
  the documented example and run it.
  **Why:** yalesites-org/yalesites-claude-plugins#64 told readers to use single-quoted CSS
  attribute values and then wrapped the selector in `page.locator('...')`. Following both
  rules gave a syntax error.
- [ ] A rule that says "do X" names the method for X. "Circle the control" with no tool that
  draws circles is a rule the agent will skip or claim to have followed.
  **Why:** yalesites-org/yalesites-claude-plugins#64 required annotated screenshots with no
  way to annotate.

## 6. Unattended and attended paths

Any skill that can run with `--bg`, on a schedule, or from a dashboard button has two
readers: a person and nobody.

- [ ] Every "ask the user" has an unattended branch. Say what a run with nobody to ask does:
  skip, log, stop, or act on a strong signal only.
  **Why:** yalesites-org/yalesites-claude-plugins#58 said "only continue if the user
  explicitly says to" on a check that `not_dave_new --bg` would hit with nobody there.
- [ ] Unattended runs act only on strong signals. A detector with known false positives
  does not get to delete, move, or `git rm` on its own. On a weak match it leaves the file,
  says so in the PR body, and logs it for a person.
  **Why:** yalesites-org/yalesites-claude-plugins#58 auto-moved on any match while the path
  check alone matched `loadRoutes.js` and `quadrant.twig`. A `--bg` run would have removed
  code from the product PR.
- [ ] Attended and unattended paths use the same definition of "strong signal". Write it
  once and have the regex match it.
  **Why:** yalesites-org/yalesites-claude-plugins#58 defined the strong signal in prose one
  way and in the regex another.

## 7. Detection and matching

Test every regex and every match rule against inputs that should not match.

- [ ] A substring match is a path-segment or token match. `adr` hits `loadRoutes.js`,
  `badRequest.php`, and `quadrant.twig`. `image` hits `wrapped_image` and `image_banner`.
  Use `(^|/)adr(/|$)` for paths and `(^|;)name:` for tokens in a delimited field.
  **Why:** yalesites-org/yalesites-claude-plugins#58 (paths) and
  yalesites-org/yalesites-claude-plugins#63 (block machine names in a CSV).
- [ ] The match is scoped to the right files and columns. Add `-- '*.md'` when only markdown
  counts. A grep over a whole CSV row also hits the title and URL columns.
  **Why:** yalesites-org/yalesites-claude-plugins#58 grepped every added file.
  yalesites-org/yalesites-claude-plugins#63 grepped whole rows.
- [ ] A "new file" check uses `--no-renames` with `--diff-filter=A`, or renames are listed as
  adds by another route.
  **Why:** yalesites-org/yalesites-claude-plugins#58 dropped a file renamed into `docs/adr/`.
- [ ] A "first heading" rule checks the first heading, not any heading
  (`grep -m1 '^#' "$f"`, then match).
  **Why:** yalesites-org/yalesites-claude-plugins#58 flagged any file with a `## ADR links`
  section.
- [ ] The pattern is not so narrow that the real cases miss it. List the real forms
  (`docs/adr/`, `docs/decisions/`, `ADR-001.md`) and test each.
  **Why:** yalesites-org/yalesites-claude-plugins#58 caught `docs/adr-*.md` only.
- [ ] A check that blocks on a match blocks only on new files, not on edits to files that
  already exist and were allowed in.
  **Why:** yalesites-org/yalesites-claude-plugins#58 stopped a one-line fix to an existing ADR.
- [ ] A host check compares `urlparse(url).netloc` to the host. `url.startswith(SITE)`
  accepts `https://site.edu.example.com/` and `https://site.edu@evil.example/`.
  **Why:** yalesites-org/yalesites-claude-plugins#62.
- [ ] Text matching runs on text, not on rendered HTML. A quote highlighter that splits a
  rendered string injects `<mark>` into `href` attributes.
  **Why:** yalesites-org/yalesites-claude-plugins#62 broke every link whose URL contained the
  selected word.
- [ ] A rule that keys on a name pattern (`pr-<N>`) means the one thing it says. If "the PR's
  own multidev" is the rule, the check is against that one name, not against the pattern.
  **Why:** yalesites-org/yalesites-claude-plugins#57 kept QA content on another PR's
  multidev because it matched `pr-*`.

## 8. Environment named precisely

An agent cannot guess an environment. Name it so a command can be built from the name.

- [ ] Every environment has a URL or a URL pattern, or a place to look it up ("copy it from
  the Environments ready for review comment"). Check the pattern against a real example.
  **Why:** yalesites-org/yalesites-claude-plugins#64 said "the RC multidev" with no name,
  then gave `<release-branch>` with an example (`v2260`) that was not a branch name.
- [ ] The base branch is named per repo and read from the PR, not hardcoded. `tokens` and
  `YaleSites-Internal` default to `main`. yalesites-project hotfixes branch from `master`.
  **Why:** yalesites-org/yalesites-claude-plugins#58 hardcoded `--base develop` and
  `develop...HEAD`. On `tokens` the diff failed and read as "no match".
- [ ] Never `HEAD` of someone else's checkout. `git -C {repo} ... HEAD` reads whatever that
  checkout happens to be on. Use `{branch}` and `git show {branch}:path`, or a temporary
  worktree. Never `git checkout` a branch in a companion checkout and leave it there.
  **Why:** yalesites-org/yalesites-claude-plugins#58, twice.
- [ ] A step that targets a Pantheon environment says which one and why it is safe there.
  Production and PR multidevs (red "DO NOT CHANGE CONTENT" banner) are not places to make
  throwaway nodes.
  **Why:** yalesites-org/yalesites-claude-plugins#64 said "on a multidev" for a block-form
  shot, which includes PR multidevs under visual regression.
- [ ] The environment has what the step needs. A yalesites-project multidev carries one
  site's content. A CLT PR has Storybook, not a multidev.
  **Why:** yalesites-org/yalesites-claude-plugins#63 told reviewers to spot-check
  usability.yale.edu "on the multidev", and to rebuild content on a multidev for CLT PRs.
- [ ] Claims about environment lifecycle are checked against the workflow. "Pantheon
  deletes a PR multidev on merge" leaves out PRs closed without merging.
  **Why:** yalesites-org/yalesites-claude-plugins#57.
- [ ] A test setup does not change the thing under test. A viewport sized to a component
  changes anything that depends on viewport height.
  **Why:** yalesites-org/yalesites-claude-plugins#57.

## 9. Numbers and claims

Every number in prose came from a table. Every table came from one aggregate.

- [ ] Every number cited in a SKILL.md or example matches the reference file it came from.
  Grep for each number and compare.
  **Why:** yalesites-org/yalesites-claude-plugins#63 shipped an example line with 12.5%, 37
  sites, 166 instances next to data that said 12.8%, 38, 226.
- [ ] One denominator, named. "Of 296 crawled sites" and "of 299 live sites" are different
  claims. Pick one base and say it.
  **Why:** yalesites-org/yalesites-claude-plugins#63 had 181 of 300 in the headline, 180 of
  296 in the data, and "of live sites" on a crawled-sites figure.
- [ ] Table totals match the sum of the rows they came from. Regenerate both from one source.
  **Why:** yalesites-org/yalesites-claude-plugins#63 had table totals that differed from
  the CSV sums after a "reconcile counts" commit.
- [ ] No superlative that the table contradicts. "The most used block" and "the widest gap"
  are claims to check against the numbers.
  **Why:** yalesites-org/yalesites-claude-plugins#63 called two different blocks the most
  used, and named the wrong block for the widest gap.
- [ ] Reviewer notes agree with the measured data beside them. A note that says "suits the end
  of a page" next to a table that says the block opens 44% of pages is wrong once.
  **Why:** yalesites-org/yalesites-claude-plugins#63, Quick Links and Callout.
- [ ] Metrics are defined. If "opens page 100%" and "preceded by X 57 times" are both true, say
  what each counts.
  **Why:** yalesites-org/yalesites-claude-plugins#63, Grand Hero.
- [ ] A 1:1 count between two things is a crawler artifact until checked. Nested content
  counted as a following block inflates the parent's numbers.
  **Why:** yalesites-org/yalesites-claude-plugins#63, Pre-Built Form and In-Line Message
  (125 of 125), and "closes page 0.0%" on every block that wraps text.
- [ ] Names match the core reference. Two rows for one block (Gallery and Media Grid) is a
  mapping to state, and every machine name in a count has a row in the table.
  **Why:** yalesites-org/yalesites-claude-plugins#63.
- [ ] A claim the skill makes about its own data is true of the data. "Grep for
  `pages_crawled` 0 or 1 to find the missed sites" has to return the missed sites.
  **Why:** yalesites-org/yalesites-claude-plugins#63 said five sites were missing, elsewhere
  three, and the grep found two.
- [ ] "Not reviewed" is not "none met the bar".
  **Why:** yalesites-org/yalesites-claude-plugins#63 said no Gallery exemplar met the bar
  when every Gallery screenshot had failed to load.
- [ ] A step that ranks by a column uses a column that exists.
  **Why:** yalesites-org/yalesites-claude-plugins#63 asked for the "heaviest-usage sites" from
  a CSV with no per-block counts.
- [ ] No internal to-dos in published references. Re-run the thing or reword it as a known
  limitation.
  **Why:** yalesites-org/yalesites-claude-plugins#63 shipped "re-run before publishing".

## 10. State and files

Anything that writes a file, claims a lock, or leaves content behind has a second run,
a crashed run, and a concurrent run to think about.

- [ ] A second run on the same input works. Creates become check-then-create. Reruns of a
  move block do not fail on an existing clone.
  **Why:** yalesites-org/yalesites-claude-plugins#57 failed on `user:create` for a user the
  first run kept. yalesites-org/yalesites-claude-plugins#58 failed on `gh repo clone` for a
  second ADR.
- [ ] Reuse checks ownership, not existence. A node id that still exists may be real content
  after a rebuild. Require the QA title prefix or the `qa-` user before touching it.
  **Why:** yalesites-org/yalesites-claude-plugins#57.
- [ ] The run deletes only what it created. "Remove what `.created` lists" with
  `--delete-content` on a reused user deletes content someone else made.
  **Why:** yalesites-org/yalesites-claude-plugins#57, three findings across two rounds.
- [ ] A claim is atomic. Check-then-claim in two commands lets two runs both claim. Claim
  under the lock, record a token, and require the token on `ready`, `fail`, and `heartbeat`.
  **Why:** yalesites-org/yalesites-claude-plugins#60 across three rounds: `get` then `start`,
  `ready` without the token, optional `--claim`.
- [ ] A long-running claim is refreshed, and a refresh on an expired claim fails.
  **Why:** yalesites-org/yalesites-claude-plugins#60: a 90-minute TTL with nothing to refresh
  it, then a heartbeat that revived dead claims.
- [ ] Stale detection compares the head for every state, not only `ready`.
  **Why:** yalesites-org/yalesites-claude-plugins#60 reported an old `failed` against a new
  head.
- [ ] A multi-item unit is checked, claimed, and failed as a unit.
  **Why:** yalesites-org/yalesites-claude-plugins#60 checked one PR of a unit, and `fail`
  marked only the PRs passed.
- [ ] Archive, never delete. A rebuilt packet folder, an old `answers.json`, an earlier
  review's rulings: rename with a unique name (`<id>-<sha>-<builtAt>`), and define the name
  for a folder with no metadata.
  **Why:** yalesites-org/yalesites-claude-plugins#60: `rm` of the packet folder, then an
  archive name that collided on the same head, then a rename rule that needed a file a crashed
  run never wrote.
- [ ] A rename does not pull the rug from a reader. A symlink by path resolves to the new
  folder after the rename. Point readers at the versioned folder.
  **Why:** yalesites-org/yalesites-claude-plugins#60.
- [ ] Copies into a shared folder cannot collide. Files numbered from `01` in every packet
  overwrite each other in a batch folder.
  **Why:** yalesites-org/yalesites-claude-plugins#60.
- [ ] A corrupt or unreadable state file is an error, not an empty file. Fall back to empty
  on `FileNotFoundError` only. Exit on a parse error, or back the file up first.
  **Why:** yalesites-org/yalesites-claude-plugins#60 and
  yalesites-org/yalesites-claude-plugins#62 both silently replaced a corrupt `status.json`
  and dropped every other entry.
- [ ] No silent fallbacks. A missing value that falls back to a neighbor's value (a compare
  side with no `url` taking the block's) points at the wrong thing.
  **Why:** yalesites-org/yalesites-claude-plugins#57.
- [ ] What the state depends on is recorded with it. A packet filtered for one reviewer's
  scope records the scope, and a mismatch reads as stale.
  **Why:** yalesites-org/yalesites-claude-plugins#60.
- [ ] A crashed run's leftovers are surfaced. If a status says "failed: interrupted", the
  reader is pointed at the `.created` list and told to clean up first.
  **Why:** yalesites-org/yalesites-claude-plugins#60.
- [ ] Re-sent approvals do not rebuild. Mark built items and skip them on the next round.
  **Why:** yalesites-org/yalesites-claude-plugins#62 would have created a second draft on
  every revision round.
- [ ] One line format for every state marker, written at one point.
  **Why:** yalesites-org/yalesites-claude-plugins#57: `kept` and `reused` did not chain, so a
  third run could not find what the second run left.
- [ ] Kept state has the cleanup it still needs (a Layout Builder tempstore clear), and
  the report says which setting a kept page needs to reproduce a finding.
  **Why:** yalesites-org/yalesites-claude-plugins#57.
- [ ] A detection of "our own draft" survives a build. Layout Builder saves make revisions
  with no log message, so a check on the latest revision's log never matches afterwards.
  **Why:** yalesites-org/yalesites-claude-plugins#64.

## 11. Local servers and boards

A local HTTP server is reachable by every page open in the same browser.

- [ ] Every POST checks `Origin` or `Host` against `localhost` / `127.0.0.1` on the server's
  port, and requires `Content-Type: application/json`. Plain-text form posts skip the CORS
  preflight.
  **Why:** yalesites-org/yalesites-claude-plugins#62: any site in the reviewer's browser could
  write `decisions.json`, and the already-merged pr-feedback board had the same gap.
- [ ] Path traversal is rejected on POST as well as GET. A guard on reads that leaves
  `?packet=..` on writes puts the file in the parent folder.
  **Why:** yalesites-org/yalesites-claude-plugins#60.
- [ ] Every packet-supplied URL rendered as a link passes a scheme check
  (`/^https?:/i`). `javascript:` and `data:` URLs in a packet become clickable otherwise.
  **Why:** yalesites-org/yalesites-claude-plugins#57.
- [ ] "This session's server" is proven by something only this session has. A health check
  on a shared folder path says nothing about who started the server.
  **Why:** yalesites-org/yalesites-claude-plugins#60: two sessions served the same prep
  folder, and one stopped the other's board mid-review.
- [ ] The printed URL is the bound address. With `--port 0`, print
  `server.server_address[1]`, not the loop variable.
  **Why:** yalesites-org/yalesites-claude-plugins#62 printed `http://localhost:0`.

## 12. Scripts: correctness with real inputs

Run the script on the inputs the skill describes. Round-trip anything that round-trips.

- [ ] A split-and-render round trip reproduces the input byte for byte on all-keep ops. Test
  with `~~~` fences, fences longer than three, blank-line runs, and a removed last section.
  **Why:** yalesites-org/yalesites-claude-plugins#62, four findings over three rounds.
- [ ] A stemmer or tokenizer maps singular and plural, and bare verb and -ing form, to the
  same token. Test `image`/`images`, `setting`/`settings`, `create`/`creating`.
  **Why:** yalesites-org/yalesites-claude-plugins#62, three rounds.
- [ ] `validate` requires every field the consumer reads unguarded.
  **Why:** yalesites-org/yalesites-claude-plugins#62: a packet with no `ticket.title` passed
  validation and crashed the board.
- [ ] "Decided" means something actionable. A changes decision with an empty note is not
  decided.
  **Why:** yalesites-org/yalesites-claude-plugins#62.
- [ ] A capture reads what the reader will see, including collapsed accordion bodies and
  inactive tab panels. `display:none` is not "not content".
  **Why:** yalesites-org/yalesites-claude-plugins#62.
- [ ] Per-item error handling covers every loop, including the outer one. One failing child
  sitemap should not abort the refresh that tolerates failing pages.
  **Why:** yalesites-org/yalesites-claude-plugins#62.
- [ ] One constant per threshold. A flag that sets the max age and a warning that hardcodes
  24h disagree.
  **Why:** yalesites-org/yalesites-claude-plugins#62.
- [ ] A selector that matches nothing gives a clear error. Use a locator, not
  `querySelector(...).getBoundingClientRect()`.
  **Why:** yalesites-org/yalesites-claude-plugins#64.
- [ ] A drawn overlay stays in the viewport. An arrow 16px right of a control docked at the
  right edge is off screen.
  **Why:** yalesites-org/yalesites-claude-plugins#64.
- [ ] Nested structures are walked to the outermost match when the outer list is what is
  indexed.
  **Why:** yalesites-org/yalesites-claude-plugins#62: `closest('.layout')` returned the inner
  layout and the index came back as -1.
- [ ] Tests assert the thing, not a prefix of it. A test that passes on `http://localhost:0`
  tested nothing.
  **Why:** yalesites-org/yalesites-claude-plugins#62.

## 13. User-facing text

- [ ] The PR title type matches the CONTRIBUTING versioning table. New rules, new reference
  files, or expanded coverage is `feat:`, not `docs:`. The squash title is the commit.
  **Why:** yalesites-org/yalesites-claude-plugins#64 shipped four new rules under `docs:`,
  which release-please reads as PATCH.
- [ ] The PR body matches the diff. Every file the diff touches is in the description, in
  the right place, and nothing described is missing from the diff.
  **Why:** yalesites-org/yalesites-claude-plugins#64 said Phase 5 when the diff said Phase 2.
  yalesites-org/yalesites-claude-plugins#62 said the server was a separate copy when the diff
  changed the shared one.
- [ ] Step numbers and cross-references were updated when a step was inserted. "List it in
  the Step 5 report" has a matching bullet in Step 5. A checklist that gates a step has a line
  for every step.
  **Why:** yalesites-org/yalesites-claude-plugins#64 and
  yalesites-org/yalesites-claude-plugins#63.
- [ ] In a decision table, the specific case comes before the catch-all. A model reads top
  down and stops at the first match.
  **Why:** yalesites-org/yalesites-claude-plugins#64 put "our own staged draft" after "Status:
  Draft, stop and ask", so the new row could never be reached.
- [ ] Examples use real values that follow the rule they illustrate. An example filed under
  the path rule is matched by the path rule.
  **Why:** yalesites-org/yalesites-claude-plugins#57 titled content after the issue number
  where the rule said PR number. yalesites-org/yalesites-claude-plugins#58 listed a
  heading-only example under the path bullet.
- [ ] Dates are ISO (`2026-12-01`), and references are `owner/repo#N` with a link.
  **Why:** yalesites-org/yalesites-claude-plugins#64 wrote "12-01-26" and "our review" with
  no link.
- [ ] A new skill is listed in the plugin README, `plugin.json`, the marketplace entry, and
  the root README table, with the same text.
  **Why:** yalesites-org/yalesites-claude-plugins#63 updated `plugin.json` only.
- [ ] Reflow paragraphs after an edit. A UI separator is not reused for a different level
  of thing.
  **Why:** yalesites-org/yalesites-claude-plugins#57: a stub line left by an edit, and a
  legend joined with the same ` · ` the header used for PR refs.
- [ ] Plain words. "Fodder" became "noise" in review.
  **Why:** yalesites-org/yalesites-claude-plugins#63.

## 14. What reviewers withdrew

Eleven of the findings were withdrawn by the reviewer in round three. They show what is
not worth pre-empting, and what a review should not raise.

- **"What might go wrong" with no failure in the files.** Two findings on
  yalesites-org/yalesites-claude-plugins#64 (Cancel not clearing tempstore, reload leaving a
  tray open) were withdrawn as scenarios the reviewer could not confirm. One on
  yalesites-org/yalesites-claude-plugins#62 (localStorage lost on a port change) described a
  path the skill never takes. One on yalesites-org/yalesites-claude-plugins#57 (a reused
  user missing its role) assumed a state the run cannot reach. Do not add defensive rules
  for these. If a reviewer raises one, ask for the failing input.
- **Scope the file already limits.** A finding about atomic and CLT PRs on
  yalesites-org/yalesites-claude-plugins#57 was withdrawn because the reference's first
  lines limit it to yalesites-project. Read the scope line before writing a rule for a case
  it excludes.
- **Code the PR did not change.** A finding about header links on
  yalesites-org/yalesites-claude-plugins#57 was withdrawn because the PR never touched them.
  Fix only what the diff touches. File the rest.
- **Undoing an earlier ask.** Two findings on yalesites-org/yalesites-claude-plugins#57 were
  withdrawn because they reversed changes the reviewer asked for in an earlier round. When
  a fix was requested and made, do not second-guess it in the next round.
- **Design suggestions and efficiency nits.** A "move this to the script" suggestion and a
  "this re-parses a list" nit on yalesites-org/yalesites-claude-plugins#60 were withdrawn as
  not defects. Do not restructure to pre-empt them.
- **Repeats of an open thread.** One finding on yalesites-org/yalesites-claude-plugins#62
  restated a thread that was still open. One fix per thread.

What was never withdrawn: anything verified by running a command, anything where two
files in the PR disagreed, and any number that did not match its source. Those are the
checks above.
