#!/usr/bin/env bash
# Read-only setup check for the YaleSites ticket workflow (macOS).
# On Windows use check-setup.ps1, which prints the same line format.
#
# Prints one line per item: "OK", "MISS" (not installed), "FAIL" (installed but
# not usable), "WARN" (works, but needs a fix such as a PATH line), "SKIP" (not
# checked because something earlier is missing) or "INFO" (a fact, never a
# problem). Exits 0 when every item is OK, 1 otherwise.
#
# It never installs, writes, or prompts. Plugin install state cannot be read
# from the shell, so the onboard skill covers that part by asking.
#
#   bash check-setup.sh              fast, read-only, works offline
#   bash check-setup.sh --browser    also test that Playwright can open Chrome,
#                                    Chromium, Firefox and WebKit (downloads
#                                    packages, briefly opens each browser)

set -u

# Never wait for input: no gh prompts, no git credential prompts, no stdin.
export GH_PROMPT_DISABLED=1
export GIT_TERMINAL_PROMPT=0
export NO_COLOR=1
exec </dev/null

ORG="yalesites-org"
REPO="yalesites-org/YaleSites-Internal"
BOARD_NUMBER="6"

# Pinned like the other skills. Source: pr-feedback/references/drive-it.md
# ("Browsers"). Bump the pin there and here together.
PLAYWRIGHT_CLI="@playwright/cli@0.1.22"

RUN_BROWSER=0
for arg in "$@"; do
  case "$arg" in
    --browser) RUN_BROWSER=1 ;;
    *) echo "usage: check-setup.sh [--browser]" >&2; exit 2 ;;
  esac
done

PROBLEMS=0

report() { # status item detail
  printf '%-4s %-18s %s\n' "$1" "$2" "$3"
  [[ "$1" == "OK" || "$1" == "INFO" ]] || PROBLEMS=$((PROBLEMS + 1))
}

first_line() { # prints the first line of stdin
  local line=""
  IFS= read -r line || true
  printf '%s' "$line"
}

error_line() { # prints the most useful line of stdin: the first "Error:" line
  # that is not the Daemon line, else the last non-empty line.
  local line last=""
  while IFS= read -r line; do
    [[ -n "${line//[[:space:]]/}" ]] && last="$line"
    if [[ "$line" == Error:* && "$line" != *"Daemon pid="* ]]; then
      printf '%s' "$line"
      return
    fi
  done
  printf '%s' "$last"
}

# --- Operating system ------------------------------------------------------
OS="$(uname -s 2>/dev/null || echo unknown)"
case "$OS" in
  Darwin) ;;
  MINGW* | MSYS* | CYGWIN*)
    report INFO os "Windows detected: run check-setup.ps1 in PowerShell instead"
    echo "powershell -NoProfile -ExecutionPolicy Bypass -File \"$(dirname "${BASH_SOURCE[0]}")/check-setup.ps1\""
    exit 1
    ;;
  *)
    report FAIL os "this guide covers macOS and Windows, found $OS"
    exit 1
    ;;
esac
report OK os "macOS"

# Admin rights decide which Homebrew install path is possible. Informational.
group_list="$(id -Gn 2>/dev/null || true)"
if [[ " $group_list " == *" admin "* ]]; then
  report INFO admin "yes (in the admin group right now, which may be temporary)"
else
  report INFO admin "no (not in the admin group)"
fi

# --- Tool lookup -----------------------------------------------------------
# On a Mac without the Command Line Tools, /usr/bin/git and /usr/bin/python3 are
# Apple placeholders that pop up an install dialog when run. Never run those.
CLT_OK=0
clt_path=""
if clt_path="$(xcode-select -p 2>/dev/null)"; then
  CLT_OK=1
fi

find_real() { # prints the first match on PATH that is not an Apple placeholder
  local p all
  all="$(type -ap "$1" 2>/dev/null)"
  while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    if [[ "$p" == /usr/bin/* && $CLT_OK -eq 0 ]]; then
      continue
    fi
    printf '%s' "$p"
    return 0
  done <<<"$all"
  return 1
}

# --- mise (a no-admin way to get the tools without Command Line Tools) -------
MISE_BIN=""
MISE_SHIMS="$HOME/.local/share/mise/shims"
if command -v mise >/dev/null 2>&1; then
  MISE_BIN="$(command -v mise)"
elif [[ -x "$HOME/.local/bin/mise" ]]; then
  MISE_BIN="$HOME/.local/bin/mise"
  report WARN mise-path "mise at $MISE_BIN but not on PATH (activate line missing from ~/.zshrc)"
  PATH="$HOME/.local/bin:$PATH"
fi
if [[ -n "$MISE_BIN" ]]; then
  report INFO mise "$("$MISE_BIN" --version 2>/dev/null | first_line)"
  if [[ -d "$MISE_SHIMS" && ":$PATH:" != *":$MISE_SHIMS:"* ]]; then
    report WARN mise-path "mise tools in $MISE_SHIMS but not on PATH (shims line missing from ~/.zprofile)"
    PATH="$MISE_SHIMS:$PATH"
  fi
fi

# Are gh, jq, node and python3 all usable already? If so the Command Line Tools
# and Homebrew are not needed for the ticket workflow.
TOOLS_COMPLETE=1
for t in gh jq node python3; do
  find_real "$t" >/dev/null || TOOLS_COMPLETE=0
done
if [[ -n "$MISE_BIN" ]]; then
  NOT_NEEDED="not needed: tools come from mise"
else
  NOT_NEEDED="not needed: gh, jq, node and python3 are installed without it"
fi

# --- Command Line Tools ----------------------------------------------------
if [[ $CLT_OK -eq 1 ]]; then
  report OK clt "$clt_path"
elif [[ $TOOLS_COMPLETE -eq 1 ]]; then
  report INFO clt "Apple Command Line Tools not installed ($NOT_NEEDED)"
else
  report MISS clt "Apple Command Line Tools not installed"
fi

# --- Homebrew --------------------------------------------------------------
# Three possible homes: the user's own folder (no admin needed), Apple Silicon,
# and Intel. If brew is not on PATH, put its folder on PATH for the rest of this
# script so later checks are fair, and warn so the skill can fix the shell files.
if command -v brew >/dev/null 2>&1; then
  report OK brew "$(brew --version 2>/dev/null | first_line)"
elif [[ -n "$MISE_BIN" && $TOOLS_COMPLETE -eq 1 ]]; then
  report INFO brew "Homebrew not on PATH ($NOT_NEEDED)"
else
  brew_prefix=""
  for candidate in "$HOME/homebrew" /opt/homebrew /usr/local; do
    if [[ -x "$candidate/bin/brew" ]]; then
      brew_prefix="$candidate"
      break
    fi
  done
  if [[ -n "$brew_prefix" ]]; then
    report WARN brew-path "brew at $brew_prefix but not on PATH (shellenv line missing from ~/.zprofile and ~/.zshrc)"
    PATH="$brew_prefix/bin:$PATH"
  elif [[ $TOOLS_COMPLETE -eq 1 ]]; then
    report INFO brew "Homebrew not installed ($NOT_NEEDED)"
  else
    report MISS brew "Homebrew not installed"
  fi
fi

# --- Tools -----------------------------------------------------------------
check_tool() { # item command version-args...
  local item="$1" cmd="$2"
  shift 2
  local real first
  if ! real="$(find_real "$cmd")"; then
    if [[ "$item" == git && $CLT_OK -eq 0 ]]; then
      report INFO git "not installed (not needed for tickets)"
    elif [[ $CLT_OK -eq 0 ]] && command -v "$cmd" >/dev/null 2>&1; then
      report MISS "$item" "not installed (only the Apple placeholder is present)"
      if [[ "$item" == python3 && "$(command -v python3)" == /usr/bin/python3 ]]; then
        report WARN python3-stub "Apple's /usr/bin/python3 is only a placeholder; do not run it (click Cancel if a pop-up appears)"
      fi
    else
      report MISS "$item" "not installed"
    fi
    return
  fi
  first="$(command -v "$cmd" 2>/dev/null)"
  if [[ "$item" == python3 && "$first" == /usr/bin/python3 && $CLT_OK -eq 0 ]]; then
    report WARN python3-stub "Apple's /usr/bin/python3 comes first on PATH and is only a placeholder; put the mise or brew folder before /usr/bin (click Cancel if a pop-up appears)"
  elif [[ "$first" == /usr/bin/* && "$real" != "$first" ]]; then
    report WARN "$item-path" "the Apple placeholder comes first on PATH; mise or brew folders must come before /usr/bin"
  fi
  report OK "$item" "$("$real" "$@" 2>&1 | first_line)"
}

check_tool git git --version
check_tool gh gh --version
check_tool jq jq --version
check_tool node node --version
check_tool python3 python3 --version
# npx is only looked up, never run: running it can download packages.
if npx_path="$(command -v npx 2>/dev/null)"; then
  report OK npx "found at $npx_path"
else
  report MISS npx "not installed (comes with node)"
fi

# --- GitHub login, scope, and access --------------------------------------
if ! command -v gh >/dev/null 2>&1; then
  report SKIP gh-auth "gh is not installed"
  report SKIP gh-scope "gh is not installed"
  report SKIP gh-repo "gh is not installed"
  report SKIP gh-board "gh is not installed"
elif ! auth_out="$(gh auth status -h github.com 2>&1)"; then
  report FAIL gh-auth "not logged in to GitHub"
  report SKIP gh-scope "not logged in"
  report SKIP gh-repo "not logged in"
  report SKIP gh-board "not logged in"
else
  report OK gh-auth "logged in to github.com"

  scopes_line=""
  while IFS= read -r line; do
    if [[ "$line" == *"Token scopes:"* ]]; then
      scopes_line="$line"
      break
    fi
  done <<<"$auth_out"

  if [[ -z "$scopes_line" ]]; then
    report FAIL gh-scope "could not read token scopes (token from an environment variable?)"
  elif [[ "$scopes_line" == *"'project'"* ]]; then
    report OK gh-scope "token has project scope"
  else
    report FAIL gh-scope "token lacks project scope"
  fi

  sso_hint() { # output
    if [[ "$1" == *SAML* || "$1" == *SSO* || "$1" == *"HTTP 403"* ]]; then
      printf ' (HTTP 403: the org may need you to authorize your login for SSO)'
    fi
  }

  if repo_out="$(gh api "repos/$REPO" --jq .full_name 2>&1)"; then
    report OK gh-repo "$repo_out"
  else
    report FAIL gh-repo "cannot read $REPO$(sso_hint "$repo_out")"
  fi

  if board_out="$(gh project view "$BOARD_NUMBER" --owner "$ORG" --format json --jq .title 2>&1)"; then
    report OK gh-board "$board_out"
  else
    report FAIL gh-board "cannot read YaleSites Board (project $BOARD_NUMBER)$(sso_hint "$board_out")"
  fi
fi

# playwright-cli is optional (screenshots). A missing one is a warning, not a
# problem, so it does not change the exit code.
if command -v playwright-cli >/dev/null 2>&1; then
  report OK playwright "playwright-cli is installed"
else
  printf '%-4s %-18s %s\n' WARN playwright "playwright-cli not installed (optional, for screenshots)"
fi

# --- Browsers for screenshots (optional) -----------------------------------
# Off by default: it downloads packages and opens browsers. Recommended, not
# required: the ticket skill works without them. Each browser gets its own
# session, opened on a blank page and then closed.
#   chrome    the installed Google Chrome (no --browser flag). Missing is only a
#             WARN, because Chromium covers it.
#   chromium  Playwright's own Chrome engine
#   firefox   Firefox
#   webkit    the engine behind Safari
browser_check() { # item label [browser-flag-value]
  local item="$1" label="$2" engine="${3:-}" session="onboard-$2" out
  local args=()
  [[ -n "$engine" ]] && args=(--browser "$engine")
  if out="$(npx -y "$PLAYWRIGHT_CLI" "-s=$session" open about:blank "${args[@]+"${args[@]}"}" 2>&1)"; then
    report OK "$item" "$label opens"
  elif [[ -z "$engine" ]]; then
    printf '%-4s %-18s %s\n' WARN "$item" "Google Chrome did not open (Chromium covers it): $(error_line <<<"$out")"
  else
    report FAIL "$item" "$label did not open: $(error_line <<<"$out")"
  fi
  npx -y "$PLAYWRIGHT_CLI" "-s=$session" close >/dev/null 2>&1 || true
}

if [[ $RUN_BROWSER -eq 0 ]]; then
  printf '%-4s %-18s %s\n' SKIP browser "run with --browser to test (optional)"
elif ! command -v npx >/dev/null 2>&1; then
  report SKIP browser "npx is not installed"
else
  browser_check browser-chrome chrome
  browser_check browser-chromium chromium chromium
  browser_check browser-firefox firefox firefox
  browser_check browser-webkit webkit webkit
fi

if [[ $PROBLEMS -eq 0 ]]; then
  echo "ALL OK"
  exit 0
fi
echo "$PROBLEMS item(s) need attention"
exit 1
