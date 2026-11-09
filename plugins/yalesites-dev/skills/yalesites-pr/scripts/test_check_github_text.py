#!/usr/bin/env python3
"""Tests for the pr-body template heading check in check-github-text.py."""

import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-github-text.py")

WITH_ISSUE = """## [86: Title](https://github.com/yalesites-org/YaleSites-Internal/issues/86)

**TL;DR:** Adds a check.

### Description of work
- Added a check

### Functional testing steps:
- [ ] Run the checker

References yalesites-org/YaleSites-Internal#86
"""

NO_ISSUE = WITH_ISSUE.split("\n", 1)[0].replace("[86: Title](https://github.com/yalesites-org/YaleSites-Internal/issues/86)", "Brief change") + "\n" + WITH_ISSUE.split("\n", 1)[1].rsplit("\nReferences", 1)[0]

ADR = """## [86: Title](https://github.com/yalesites-org/YaleSites-Internal/issues/86)

**TL;DR:** Records a decision.

[ADR](https://github.com/yalesites-org/YaleSites-Internal/blob/86-x/docs/adr/86-x.md)

References yalesites-org/YaleSites-Internal#86
"""


def kinds(body, surface="pr-body"):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(body)
    try:
        out = subprocess.run([sys.executable, SCRIPT, fh.name, "--surface", surface, "--json"],
                             capture_output=True, text=True)
        import json
        return [i["kind"] for i in json.loads(out.stdout)]
    finally:
        os.unlink(fh.name)


class PrHeadingTests(unittest.TestCase):
    def test_template_with_issue_passes(self):
        self.assertNotIn("pr_heading_missing", kinds(WITH_ISSUE))

    def test_template_without_issue_passes(self):
        self.assertNotIn("pr_heading_missing", kinds(NO_ISSUE))

    def test_wrong_level_headings_flagged(self):
        body = WITH_ISSUE.replace("### Description of work", "## Description of work") \
                         .replace("### Functional testing steps:", "## Testing")
        self.assertEqual(kinds(body).count("pr_heading_missing"), 2)

    def test_missing_description_flagged(self):
        body = WITH_ISSUE.replace("### Description of work", "### Summary")
        self.assertEqual(kinds(body).count("pr_heading_missing"), 1)

    def test_missing_testing_flagged(self):
        body = WITH_ISSUE.replace("### Functional testing steps:", "### Functional testing steps")
        self.assertEqual(kinds(body).count("pr_heading_missing"), 1)

    def test_adr_body_exempt(self):
        self.assertNotIn("pr_heading_missing", kinds(ADR))

    def test_other_surfaces_unaffected(self):
        self.assertNotIn("pr_heading_missing", kinds(ADR.replace("[ADR]", "x"), "ticket"))


if __name__ == "__main__":
    unittest.main()
