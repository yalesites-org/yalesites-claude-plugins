#!/usr/bin/env bash
# Run the test suite that ships alongside any skill script.
#
# `unittest discover` is deliberately not used. Python 3.11 removed
# namespace-package discovery, so `_find_test_path` refuses to recurse into a
# directory without an `__init__.py` -- and scattering package markers through
# shipped skill directories is worse than running the files. Discovery over
# `plugins/` therefore reports "Ran 0 tests ... OK" and exits 0, which is a
# green check that tested nothing.
#
# This asserts the invariant instead of the absence of failures: at least one
# test file must be found, and each file must report a non-zero test count.
set -uo pipefail

ERRORS=0
FOUND=0

for base_dir in plugins external_plugins; do
  [[ -d "$base_dir" ]] || continue
  while IFS= read -r test_file; do
    FOUND=$((FOUND + 1))
    echo "Running $test_file..."
    output=$(python3 "$test_file" 2>&1)
    status=$?
    if [[ $status -ne 0 ]]; then
      echo "$output"
      echo "  ERROR: tests failed"
      ERRORS=$((ERRORS + 1))
      continue
    fi
    # "Ran 0 tests" passes unittest but means the suite is empty.
    if ! grep -qE '^Ran [1-9][0-9]* test' <<<"$output"; then
      echo "$output"
      echo "  ERROR: no tests were collected"
      ERRORS=$((ERRORS + 1))
      continue
    fi
    echo "  $(grep -oE '^Ran [0-9]+ tests? in [0-9.]+s' <<<"$output")"
  done < <(find "$base_dir" -type f -name 'test_*.py' | sort)
done

echo ""
if [[ $FOUND -eq 0 ]]; then
  echo "No skill test files found. Expected at least one plugins/**/test_*.py."
  exit 1
fi
if [[ $ERRORS -gt 0 ]]; then
  echo "Skill tests failed in $ERRORS file(s) across $FOUND file(s)."
  exit 1
fi
echo "All $FOUND skill test file(s) passed."
