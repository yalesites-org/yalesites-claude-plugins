---
name: phpunit-drupal
description: Run Drupal PHPUnit Unit, Kernel, and Functional tests in a YaleSites Lando environment. Use this whenever the user wants to run, write, debug, or verify PHPUnit tests in a yalesites-* or Drupal checkout — the correct `lando ssh -c` invocation is non-obvious and the commonly copied form fails silently, so reach for the skill even for a request as plain as "run the tests" or a bare test file path. Reach for it just as readily when a run is going wrong rather than being started: "Class ... not found", a run killed with exit 143, exit 1 while every test shows green, HTTP 500 on every route in a BrowserTestBase test, "Could not read phpunit.xml", SIMPLETEST_DB errors, or tests that will not run from a git worktree. It is also the place that records why a green suite here is not a CI gate. Use it even if the user never says PHPUnit, Lando, or kernel test.
---

# PHPUnit on YaleSites / Lando

## Use the bundled script

`scripts/run-kernel-test.sh` builds the invocation below correctly. Prefer it
over retyping the command — the quoting is the part that goes wrong.

```bash
# whole Kernel suite for a module
scripts/run-kernel-test.sh ys_views_basic

# one file, narrowed to two tests
scripts/run-kernel-test.sh -f '(testFoo|testBar)' ys_views_basic MyThingTest.php

# Unit suite (no database)
scripts/run-kernel-test.sh -u ys_core

# print the command without running it — cheap way to check before a 7-minute run
scripts/run-kernel-test.sh -n ys_views_basic
```

Run it from anywhere inside the checkout; it walks up to find the profile root
and warns if `vendor/` is not installed. Launch real runs with
`run_in_background: true`.

## The invocation it builds

Read this when the script is not available or you need to vary something it does
not expose.

```bash
lando ssh -c "env SIMPLETEST_DB=mysql://pantheon:pantheon@database/pantheon?module=mysql \
  SIMPLETEST_BASE_URL=http://appserver \
  php /app/vendor/bin/phpunit -c /app/phpunit.xml \
  /app/web/profiles/custom/yalesites_profile/modules/custom/<MODULE>/tests/src/Kernel/ \
  --testdox"
```

Launch it with `run_in_background: true`. A kernel run takes **1-7 minutes** —
it bootstraps the whole install profile, and some individual tests take ~50s
each (e.g. `ys_node_access` grants).

Every part of that command is load-bearing. Details below.

## Four things that make the obvious command fail

**1. `lando ssh -c` does not run a shell.** It execs the command directly, so
the familiar `VAR=value command` prefix is not interpreted as an assignment —
and quotes inside the value are passed through literally. This form:

```bash
# BROKEN — do not copy
lando ssh -c "SIMPLETEST_DB='mysql://pantheon:pantheon@database/pantheon' vendor/bin/phpunit ..."
```

fails with `Can not convert ''mysql://...''` — note the doubled quotes, which are
the literal single quotes arriving as part of the value. Use the `env` binary
and **unquoted** values, as in the working command above.

**2. Use an absolute `-c` path.** A relative `-c phpunit.xml` produces a spurious
`Could not read "phpunit.xml"` — a subprocess re-reads the config from a
different working directory. It looks exactly like a test failure and is not.

**3. Target a path, never the default suite.** `lando phpunit` (the tooling from
`.lando.upstream.yml`) runs the configured suites, which scan all of `web/` and
**fatal** on a pre-existing broken contrib test: `honeypot`'s unit test
references a missing `Drupal\Tests\rules\...` class. Passing an explicit module
`tests/` path bypasses discovery entirely.

**4. The DB URL is `pantheon:pantheon@database/pantheon`.** User, password, and
database are all `pantheon`; the host is the service name `database`. Confirm for
a given checkout with `lando info`.

The `?module=mysql` driver parameter is in the primary form because a Drupal 10
run failed without it. A run *without* it has also been recorded working, so if
you hit a URL-parsing error, try toggling that parameter rather than assuming the
credentials are wrong.

Why the `env` prefix wins at all: `phpunit.xml` declares
`<env name="SIMPLETEST_DB" value=""/>` with no `force` attribute, so the empty
default does not override a variable already present in the environment.
(Mechanism inferred from the config and PHPUnit 9 semantics; the *outcome* —
`env` prefix works — is confirmed by repeated use.)

## Which suites actually work here

| Suite | Needs | Status |
|---|---|---|
| **Unit** | nothing | Works. `lando phpunit <path>/tests/src/Unit/` is fine — no DB. |
| **Kernel** | `SIMPLETEST_DB` | Works. The command at the top. |
| **Functional** (`BrowserTestBase`) | full test-site install | **Broken locally.** |

Functional tests **HTTP 500 on every route** in local Lando, independent of the
code under test — verified by running on a clean baseline, where it 500s
identically with and without changes. The isolated test-site install does not
come up. Invocation, if you want to see it fail for yourself:

```bash
lando ssh -c "env SIMPLETEST_DB=mysql://pantheon:pantheon@database/pantheon \
  SIMPLETEST_BASE_URL=http://appserver_nginx BROWSERTEST_OUTPUT_DIRECTORY=/tmp \
  ./vendor/bin/phpunit <path>"
```

Never report a Functional 500 as a regression without first confirming it fails
the same way on a clean baseline (`git stash`, rerun). For a change only
Functional tests would cover, verify with `php -l` + phpcs + explicit
behavior-preserving reasoning, and say plainly that runtime verification was not
possible.

## Running more than one test

**Sequentially, never in parallel.** Several kernel runs at once contend on the
MySQL test database and one gets SIGTERM — exit code 143. If a single file is
too slow, narrow it instead:

```bash
--filter '(testFooBar|testBazQux)'
```

## Scope the run to the diff — a full run is ~4 HOURS

**Never run the whole suite as an iteration loop.** A full run takes roughly
**4 hours** (2026-09). An unscoped run is a blocker, not feedback, and it
serializes everything else — parallel runs kill each other, and source files
must not be edited while a run is in flight.

Scope by cost, in this order:

1. **The whole `tests/src/Unit` directory is effectively free** — hundreds of
   tests in about a second. Run it in full; never bother narrowing it.
2. **Kernel and Functional tests are the expensive part** (historically ~4m45s
   *per class*). Run only the individual test **files covering the code the diff
   touches**. Derive them from the diff: for each changed source file, its sibling
   test under `<module>/tests/src/{Kernel,Functional}/`, plus any test that names
   the changed class or service. **One path per invocation, sequentially** — see
   the first-path-argument trap below.
3. **A full-module run is a single pre-commit gate at most.** Say up front that
   it is one run and roughly how long it will take.

If the loop would exceed a few minutes per iteration, propose the narrower scope
rather than waiting to be asked.

### If you are dispatching a subagent to run tests

A subagent does not inherit this judgment and **will** reach for the whole suite
and burn hours. Put the scope in the prompt. Include all of:

- **The exact test paths to run** — you derive them from the diff; do not make
  the subagent guess — plus the full working `lando ssh -c` invocation above, and
  the instruction to run **one path per invocation** (see below).
- **An explicit prohibition:** "Run ONLY these paths. Do NOT run the module's
  whole `tests/` directory, the default suite, or anything under `web/core` or
  `web/modules/contrib` — a full run takes about 4 hours."
- **The baseline** (counts *and* already-failing names) so it reports a delta
  instead of re-deriving one.
- **A time budget:** "if this exceeds ~10 minutes, stop and report what you have."

The same applies to Playwright or accessibility subagents: name the specific
pages and flows, never hand over the whole site.

### PHPUnit honours only the FIRST path argument

Passing two paths in one invocation silently runs only the first and reports a
total that looks like it covered both:

```bash
# WRONG - only ys_ai_tester runs; ys_ai_tester_legacy is silently skipped
lando ssh -c "php /app/vendor/bin/phpunit -c /app/phpunit.xml \
  $B/modules/ys_ai_tester/tests/src/Unit/ $B/modules/ys_ai_tester_legacy/tests/src/Unit/"
```

Run one path per invocation, sequentially, and record the count per module. This
matters most for a **baseline**: one captured this way understates what it covers,
so "no regressions" is measured against the wrong number.

## Reading the result

**Exit 1 with every test green** is usually not a failure. If the output shows
all `✔` plus only the skips you intended (`↩`), PHPUnit is failing on its
deprecation-notice tally, not on a test. Read the summary before reporting a
regression.

Record the baseline before you change anything: pass/fail counts *and the names*
of already-failing tests. "No regressions" means nothing without a number to
diff against.

## Two limits worth stating out loud

**CI runs no PHPUnit at all.** In `yalesites-project`, `.ci/test/static/run`
calls `composer unit-test`, and that script is literally
`echo 'No unit test step defined.'`. The GitHub Actions `Test` job runs only
`lint:php`, `code-sniff`, and `npm run lint:styles`. So:

- Kernel and Unit tests run **only** when a developer runs them locally.
- Never tell a reviewer that "CI will catch that" for anything covered
  by a PHPUnit test. `composer code-sniff` is the real gate.
- An acceptance criterion like "each PR keeps the suite green" is a convention,
  not an enforced gate — say so when scoping.

**A git worktree cannot run tests.** A worktree contains only tracked files;
`web/core`, `web/modules/contrib`, `web/themes/contrib`, and `vendor` are
composer-installed and gitignored, so they do not exist there. Lando is bound to
the main checkout at `/app`, and Drupal's test class loader scans relative to
that DRUPAL_ROOT — it never sees the worktree. Symptom: `Class ... not found`.

Workaround: author in the worktree, copy the changed and new PHP + test files
into the main checkout, run there, then restore
(`git checkout HEAD -- <tracked files>`, `rm` the new ones). Do not disturb
unrelated uncommitted work in the main checkout while doing it.

## Picking the right Lando app

Multiple YaleSites checkouts run Lando simultaneously, so `lando list` alone does
not tell you which app maps to your directory. Read `.lando.local.yml` → `name:`
for the app name and `tooling.drush.env.DRUSH_OPTIONS_URI` for the site URL, or
run `lando info` from the checkout.

Note that `yalesites-project` itself currently has an **empty `vendor/`** — it is
not composer-installed, so nothing runs there. Which of your own checkouts are
actually built (composer-installed) is machine- and developer-specific — check
with `ls vendor/bin/phpunit` from each checkout rather than assuming any
particular one is ready.

## Test layout

```
web/profiles/custom/yalesites_profile/modules/custom/ys_<name>/
  tests/src/Unit/        Drupal\Tests\ys_<name>\Unit
  tests/src/Kernel/      Drupal\Tests\ys_<name>\Kernel
  tests/src/Functional/  Drupal\Tests\ys_<name>\Functional   (see above — 500s locally)
```

Kernel tests must declare every module they need in `protected static $modules`,
and call `$this->installEntitySchema()` / `installConfig()` for anything they
touch. A missing entry surfaces as a plugin-not-found or table-missing error, not
as a helpful message.
