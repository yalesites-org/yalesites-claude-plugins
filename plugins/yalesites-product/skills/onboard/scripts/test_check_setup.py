#!/usr/bin/env python3
"""Tests for check-setup.sh using a fake PATH of stub executables.

Nothing here touches the network or the real gh: PATH holds only stubs.

    python3 test_check_setup.py

CI runs this via `scripts/run-skill-tests.sh`, which also asserts the tests were
actually collected.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(_HERE, "check-setup.sh")

AUTH_WITH_PROJECT = (
    "github.com\n  - Logged in to github.com account someone (keyring)\n"
    "  - Token scopes: 'gist', 'project', 'read:org', 'repo'\n"
)
AUTH_NO_PROJECT = (
    "github.com\n  - Logged in to github.com account someone (keyring)\n"
    "  - Token scopes: 'gist', 'read:org', 'read:project', 'repo'\n"
)

GH_STUB = """#!/bin/bash
echo "$@" >> "$STUB_DIR/gh-calls.log"
case "$1" in
  --version) echo "gh version 2.50.0 (stub)" ;;
  auth) [ "$GH_STUB_AUTH" = "none" ] && exit 1; printf '%s\\n' "$(<"$STUB_DIR/auth.txt")" ;;
  api) echo "yalesites-org/YaleSites-Internal" ;;
  project) echo "YaleSites Board" ;;
esac
"""


def _stub(directory, name, body):
    path = os.path.join(directory, name)
    with open(path, "w") as f:
        f.write("#!/bin/bash\n" + body + "\n")
    os.chmod(path, 0o755)


class CheckSetupTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = self._tmp.name
        _stub(self.dir, "uname", 'echo Darwin')
        _stub(self.dir, "xcode-select", 'echo /Library/Developer/CommandLineTools')
        _stub(self.dir, "id", 'echo "staff everyone"')
        _stub(self.dir, "brew", 'echo "Homebrew 4.0.0"')
        _stub(self.dir, "git", 'echo "git version 2.40.0"')
        _stub(self.dir, "jq", 'echo "jq-1.7"')
        _stub(self.dir, "npx", 'echo "$@" >> "$STUB_DIR/npx-calls.log"; echo 10.0.0')
        _stub(self.dir, "node", 'echo "v20.0.0"')
        _stub(self.dir, "python3", 'echo "Python 3.12.0"')

    def add_gh(self, auth_text=AUTH_WITH_PROJECT):
        with open(os.path.join(self.dir, "gh"), "w") as f:
            f.write(GH_STUB)
        os.chmod(os.path.join(self.dir, "gh"), 0o755)
        with open(os.path.join(self.dir, "auth.txt"), "w") as f:
            f.write(auth_text)

    def run_check(self, *args, **extra_env):
        env = {"PATH": self.dir, "STUB_DIR": self.dir, "HOME": self.dir}
        env.update(extra_env)
        proc = subprocess.run(
            ["/bin/bash", SCRIPT, *args], env=env, capture_output=True, text=True, timeout=30
        )
        return proc.returncode, proc.stdout

    def calls(self):
        path = os.path.join(self.dir, "gh-calls.log")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return f.read().splitlines()

    def test_all_present_and_authed_exits_zero(self):
        self.add_gh()
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("OK   gh-scope", out)
        self.assertIn("OK   gh-board", out)
        self.assertNotIn("MISS", out)
        self.assertNotIn("FAIL", out)

    def test_gh_missing_reports_miss_and_skips_network(self):
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("MISS gh ", out)
        self.assertIn("SKIP gh-repo", out)
        self.assertIn("SKIP gh-board", out)
        self.assertEqual(self.calls(), [])

    def test_missing_project_scope_reports_fail(self):
        self.add_gh(AUTH_NO_PROJECT)
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("FAIL gh-scope", out)
        self.assertIn("lacks project scope", out)

    def test_not_logged_in_skips_network(self):
        self.add_gh()
        code, out = self.run_check(GH_STUB_AUTH="none")
        self.assertEqual(code, 1)
        self.assertIn("FAIL gh-auth", out)
        self.assertIn("SKIP gh-repo", out)
        self.assertFalse(any(c.startswith(("api", "project")) for c in self.calls()))

    def test_brew_only_in_home_warns_about_path(self):
        self.add_gh()
        os.remove(os.path.join(self.dir, "brew"))
        home_bin = os.path.join(self.dir, "homebrew", "bin")
        os.makedirs(home_bin)
        _stub(home_bin, "brew", 'echo "Homebrew 4.0.0"')
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("WARN brew-path", out)
        self.assertIn(os.path.join(self.dir, "homebrew"), out)

    def test_admin_is_info_only(self):
        self.add_gh()
        _stub(self.dir, "id", 'echo "staff admin everyone"')
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"INFO admin\s+yes")

    def test_default_run_skips_browser_and_never_calls_npx(self):
        self.add_gh()
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("SKIP browser", out)
        self.assertIn("OK   npx", out)
        # npx must not even be run for a version number: no calls at all.
        self.assertFalse(os.path.exists(os.path.join(self.dir, "npx-calls.log")))
        self.assertIn("--browser", out)

    def test_browser_flag_checks_all_four_and_chrome_missing_only_warns(self):
        self.add_gh()
        _stub(
            self.dir,
            "npx",
            'case "$*" in *"open"*"--browser"*) echo ok;; *"open"*) echo "no chrome"; exit 1;; *) echo 10.0.0;; esac',
        )
        code, out = self.run_check("--browser")
        self.assertEqual(code, 0, out)
        self.assertIn("WARN browser-chrome", out)
        for name in ("chromium", "firefox", "webkit"):
            self.assertIn("OK   browser-" + name, out)

    def test_browser_failure_shows_the_error_line_not_a_file_path(self):
        self.add_gh()
        with open(os.path.join(self.dir, "npx-out.txt"), "w") as f:
            f.write(
                "Daemon pid=4242\n"
                "/Users/someone/node_modules/playwright/session.js:172\n"
                "      throw new Error(msg);\n"
                "Error: Browser \"chrome-for-testing\" is not installed; expected executable at "
                "/Users/someone/Library/Caches/ms-playwright/chromium-1/chrome. "
                "Run playwright-cli install-browser chrome-for-testing to install\n"
                "    at launch (session.js:172:11)\n"
            )
        _stub(
            self.dir,
            "npx",
            'echo "$@" >> "$STUB_DIR/npx-calls.log"; '
            'case "$*" in *" open "*chromium*) printf \'%s\\n\' "$(<"$STUB_DIR/npx-out.txt")"; exit 1;; '
            '*" open "*) echo ok;; *) echo 10.0.0;; esac',
        )
        code, out = self.run_check("--browser")
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r'FAIL browser-chromium\s+chromium did not open: Error: Browser "chrome-for-testing" is not installed')
        self.assertNotIn("session.js:172\n", out)
        self.assertNotIn("Daemon pid", out)
        self.assertIn("OK   browser-firefox", out)

    def test_missing_clt_reports_miss(self):
        self.add_gh()
        _stub(self.dir, "xcode-select", "exit 2")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("MISS clt", out)


class CheckSetupPowerShellTest(unittest.TestCase):
    """Smoke test of check-setup.ps1. Needs pwsh, so it is skipped without it.

    Off Windows (macOS or Linux pwsh) this only proves that the script runs and
    stops at its `FAIL os` line in the right line format. The real Windows
    checks are not exercised here.
    """

    def test_line_format(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("pwsh (PowerShell) is not installed")
        proc = subprocess.run(
            [pwsh, "-NoProfile", "-File", os.path.join(_HERE, "check-setup.ps1")],
            capture_output=True, text=True, timeout=120,
        )
        line = re.compile(r"^(OK|MISS|FAIL|WARN|SKIP|INFO) +\S+ +\S")
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        self.assertTrue(lines)
        for l in lines:
            if l.startswith("ALL OK") or "need attention" in l:
                continue
            self.assertRegex(l, line)
        self.assertIn(proc.returncode, (0, 1))


if __name__ == "__main__":
    unittest.main()
