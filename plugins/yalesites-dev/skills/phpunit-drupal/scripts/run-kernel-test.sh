#!/usr/bin/env bash
# Build and run the correct PHPUnit invocation for a YaleSites module inside Lando.
#
# This exists because the command itself is the hard part, not the testing. Four
# things silently break the obvious version: `lando ssh -c` execs without a shell
# (so `VAR=value cmd` is not an assignment and quotes arrive literally), a
# relative `-c` path yields a bogus "Could not read phpunit.xml", the default
# suite fatals on contrib honeypot's broken test, and the DB host is the Lando
# service name rather than localhost. Encoding it once means nobody re-derives it
# under pressure.
#
# Usage:
#   run-kernel-test.sh [-n] [-u] [-f FILTER] <module> [test-file]
#
#   -n          Dry run: print the command and exit. Use this to check the
#               invocation without paying for a 1-7 minute bootstrap.
#   -u          Unit suite instead of Kernel (no database needed).
#   -f FILTER   Pass through to --filter, e.g. -f '(testFoo|testBar)'.
#   <module>    Module machine name, e.g. ys_views_basic.
#   [test-file] Optional single test file name within the suite dir,
#               e.g. MyThingTest.php. Omit to run the whole suite directory.
#
# Run one module at a time. Concurrent kernel runs contend on the MySQL test
# database and one gets SIGTERM (exit 143), which reads like a real failure.

set -uo pipefail

dry=0
suite=Kernel
filter=""

usage() { sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while getopts ':nuf:h' opt; do
  case "$opt" in
    n) dry=1 ;;
    u) suite=Unit ;;
    f) filter="$OPTARG" ;;
    h) usage 0 ;;
    :) printf 'error: -%s needs a value\n\n' "$OPTARG" >&2; usage 1 ;;
    \?) printf 'error: unknown option -%s\n\n' "$OPTARG" >&2; usage 1 ;;
  esac
done
shift $((OPTIND - 1))

module="${1:-}"
testfile="${2:-}"
[ -n "$module" ] || { printf 'error: module name required\n\n' >&2; usage 1; }

# Resolve the checkout by walking up for the profile marker, so the script works
# from anywhere inside the repo.
d="$PWD"
repo=""
while [ -n "$d" ] && [ "$d" != "/" ]; do
  if [ -d "$d/web/profiles/custom/yalesites_profile" ]; then repo="$d"; break; fi
  d=$(dirname "$d")
done
[ -n "$repo" ] || { echo "error: not inside a YaleSites checkout (no web/profiles/custom/yalesites_profile above $PWD)" >&2; exit 1; }

# /app is the in-container docroot; host paths are irrelevant to the command.
rel="web/profiles/custom/yalesites_profile/modules/custom/$module/tests/src/$suite"
[ -d "$repo/$rel" ] || echo "warning: $rel does not exist in this checkout" >&2

target="/app/$rel"
[ -n "$testfile" ] && target="$target/$testfile"

if [ ! -x "$repo/vendor/bin/phpunit" ]; then
  echo "warning: $repo/vendor/bin/phpunit is missing — this checkout is not composer-installed, so the run will fail" >&2
fi

# Unit tests need no database; kernel tests do. Dropping the env prefix entirely
# for Unit keeps the emitted command honest about which suite depends on the
# container DB.
inner="php /app/vendor/bin/phpunit -c /app/phpunit.xml $target"
if [ "$suite" != "Unit" ]; then
  inner="env SIMPLETEST_DB=mysql://pantheon:pantheon@database/pantheon?module=mysql SIMPLETEST_BASE_URL=http://appserver $inner"
fi

# Deliberately unquoted: `lando ssh -c` execs without a shell, so quotes would be
# passed through as literal characters (the same trap that breaks SIMPLETEST_DB).
# Parentheses and pipes are safe here for that reason, but a filter containing
# spaces will not survive tokenisation.
[ -n "$filter" ] && inner="$inner --filter $filter"
inner="$inner --testdox"

if [ "$dry" = "1" ]; then
  printf 'lando ssh -c "%s"\n' "$inner"
  exit 0
fi

echo "repo:  $repo" >&2
echo "runs:  lando ssh -c \"$inner\"" >&2
echo "note:  expect 1-7 minutes; exit 1 with all tests green is a deprecation tally, not a failure" >&2
cd "$repo" || exit 1
exec lando ssh -c "$inner"
