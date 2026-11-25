# Read-only setup check for the YaleSites ticket workflow (Windows).
# PowerShell mirror of check-setup.sh with the same line format.
#
# Prints one line per item: OK, MISS (not installed), FAIL (installed but not
# usable), WARN (works, needs a fix), SKIP (not checked) or INFO (a fact).
# Exits 0 when every item is OK, 1 otherwise. It never installs, writes, or
# prompts.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File check-setup.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File check-setup.ps1 -Browser
#
# -Browser also tests Google Chrome, Chromium, Firefox and WebKit through
# Playwright (downloads packages, briefly opens each browser).

param([switch]$Browser)

$ErrorActionPreference = 'Continue'
$env:GH_PROMPT_DISABLED = '1'
$env:GIT_TERMINAL_PROMPT = '0'
$env:NO_COLOR = '1'

$Org = 'yalesites-org'
$Repo = 'yalesites-org/YaleSites-Internal'
$BoardNumber = '6'
# Pinned like the other skills. Source: pr-feedback/references/drive-it.md
# ("Browsers"). Bump the pin there and here together.
$PlaywrightCli = '@playwright/cli@0.1.22'

$script:Problems = 0

function Show-Line([string]$Status, [string]$Item, [string]$Detail) {
  Write-Output ('{0,-4} {1,-14} {2}' -f $Status, $Item, $Detail)
}

function Report([string]$Status, [string]$Item, [string]$Detail) {
  Show-Line $Status $Item $Detail
  if ($Status -ne 'OK' -and $Status -ne 'INFO') { $script:Problems++ }
}

function First-Line($Text) {
  $line = ($Text | Out-String) -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 1
  if ($line) { return $line.Trim() }
  return ''
}

function Error-Line($Text) {
  $lines = ($Text | Out-String) -split "`r?`n"
  $hit = $lines | Where-Object { $_ -like 'Error:*' -and $_ -notlike '*Daemon pid=*' } | Select-Object -First 1
  if ($hit) { return $hit.Trim() }
  $last = $lines | Where-Object { $_.Trim() } | Select-Object -Last 1
  if ($last) { return $last.Trim() }
  return ''
}

# --- Operating system ------------------------------------------------------
if ($env:OS -ne 'Windows_NT') {
  Report 'FAIL' 'os' 'this script is for Windows. On a Mac run check-setup.sh'
  exit 1
}
Report 'OK' 'os' 'Windows'

# Admin rights decide which install paths are possible. Informational.
$isAdmin = $false
try {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $isAdmin = ([Security.Principal.WindowsPrincipal]$id).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
} catch { }
if ($isAdmin) { Report 'INFO' 'admin' 'yes (this window is running as administrator)' }
else { Report 'INFO' 'admin' 'no (normal user window)' }

# --- Scoop (per-user package manager) --------------------------------------
$ScoopShims = Join-Path $env:USERPROFILE 'scoop\shims'
if (Get-Command scoop -ErrorAction SilentlyContinue) {
  Report 'OK' 'scoop' (First-Line (& scoop --version 2>&1))
} elseif (Test-Path (Join-Path $ScoopShims 'scoop.ps1')) {
  Report 'WARN' 'scoop-path' "scoop at $ScoopShims but not on PATH (open a new window, or restart Claude)"
  $env:PATH = "$ScoopShims;$env:PATH"
} else {
  Report 'MISS' 'scoop' 'Scoop not installed'
}

# --- Tools -----------------------------------------------------------------
# Scoop puts most tools in scoop\shims, but node, npm and npx live in the
# nodejs-lts app folders, and `npm -g` puts playwright-cli in the same place.
$ExtraDirs = @(
  $ScoopShims,
  (Join-Path $env:USERPROFILE 'scoop\apps\nodejs-lts\current'),
  (Join-Path $env:USERPROFILE 'scoop\apps\nodejs-lts\current\bin')
)

# Windows ships a "python.exe" placeholder in WindowsApps that opens the Store
# when run. Never run that one: skip any result under WindowsApps, and fall
# back to the extra folders whenever no real one is on PATH.
function Find-Tool([string[]]$Names) {
  foreach ($n in $Names) {
    $real = Get-Command $n -All -CommandType Application, ExternalScript -ErrorAction SilentlyContinue |
      Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1
    if ($real) { return $real }
  }
  foreach ($n in $Names) {
    foreach ($dir in $ExtraDirs) {
      foreach ($ext in '.exe', '.cmd', '.ps1') {
        $p = Join-Path $dir ($n + $ext)
        if (Test-Path $p) {
          Show-Line 'WARN' "$n-path" "found in $dir but not on PATH (open a new window, or restart Claude)"
          $script:Problems++
          $env:PATH = "$dir;$env:PATH"
          return [pscustomobject]@{ Source = $p }
        }
      }
    }
  }
  return $null
}

function Check-Tool([string]$Item, [string[]]$Names, [switch]$NoRun) {
  $cmd = Find-Tool $Names
  if (-not $cmd) { Report 'MISS' $Item 'not installed'; return }
  if ($NoRun) { Report 'OK' $Item "found at $($cmd.Source)"; return }
  Report 'OK' $Item (First-Line (& $cmd.Source --version 2>&1))
}

Check-Tool 'git' @('git')
Check-Tool 'gh' @('gh')
Check-Tool 'jq' @('jq')
Check-Tool 'node' @('node')
Check-Tool 'python3' @('python', 'python3')
# npx is only looked up, never run: running it can download packages.
Check-Tool 'npx' @('npx') -NoRun

$haveGh = [bool](Get-Command gh -ErrorAction SilentlyContinue)
$haveNpx = [bool](Get-Command npx -ErrorAction SilentlyContinue)

# --- GitHub login, scope, and access ---------------------------------------
if (-not $haveGh) {
  foreach ($i in 'gh-auth', 'gh-scope', 'gh-repo', 'gh-board') { Report 'SKIP' $i 'gh is not installed' }
} else {
  $authOut = (& gh auth status -h github.com 2>&1 | Out-String)
  if ($LASTEXITCODE -ne 0) {
    Report 'FAIL' 'gh-auth' 'not logged in to GitHub'
    foreach ($i in 'gh-scope', 'gh-repo', 'gh-board') { Report 'SKIP' $i 'not logged in' }
  } else {
    Report 'OK' 'gh-auth' 'logged in to github.com'
    $scopesLine = ($authOut -split "`r?`n" | Where-Object { $_ -like '*Token scopes:*' } | Select-Object -First 1)
    if (-not $scopesLine) { Report 'FAIL' 'gh-scope' 'could not read token scopes (token from an environment variable?)' }
    elseif ($scopesLine -like "*'project'*") { Report 'OK' 'gh-scope' 'token has project scope' }
    else { Report 'FAIL' 'gh-scope' 'token lacks project scope' }

    function Sso-Hint([string]$Text) {
      if ($Text -match 'SAML|SSO|HTTP 403') { return ' (HTTP 403: the org may need you to authorize your login for SSO)' }
      return ''
    }

    $repoOut = (& gh api "repos/$Repo" --jq .full_name 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -eq 0) { Report 'OK' 'gh-repo' $repoOut }
    else { Report 'FAIL' 'gh-repo' ("cannot read $Repo" + (Sso-Hint $repoOut)) }

    $boardOut = (& gh project view $BoardNumber --owner $Org --format json --jq .title 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -eq 0) { Report 'OK' 'gh-board' $boardOut }
    else { Report 'FAIL' 'gh-board' ("cannot read YaleSites Board (project $BoardNumber)" + (Sso-Hint $boardOut)) }
  }
}

# playwright-cli is optional (screenshots). Missing is a warning only.
$pwFound = $false
foreach ($dir in $ExtraDirs) {
  foreach ($ext in '.exe', '.cmd', '.ps1') {
    if (Test-Path (Join-Path $dir ('playwright-cli' + $ext))) { $pwFound = $true; $pwDir = $dir }
  }
}
if (Get-Command playwright-cli -ErrorAction SilentlyContinue) {
  Report 'OK' 'playwright' 'playwright-cli is installed'
} elseif ($pwFound) {
  Show-Line 'WARN' 'playwright-path' "playwright-cli found in $pwDir but not on PATH (open a new window, or restart Claude)"
} else {
  Show-Line 'WARN' 'playwright' 'playwright-cli not installed (optional, for screenshots)'
}

# --- Browsers for screenshots (optional) -----------------------------------
# chrome = the default: the installed Google Chrome (no --browser flag; Edge is
# not used. Edge-only users run with --browser chromium or msedge). Missing is only a WARN, because Chromium covers it.
function Check-Browser([string]$Item, [string]$Label, [string]$Engine) {
  $session = "-s=onboard-$Label"
  $cliArgs = @('-y', $PlaywrightCli, $session, 'open', 'about:blank')
  if ($Engine) { $cliArgs += @('--browser', $Engine) }
  $out = (& npx @cliArgs 2>&1 | Out-String)
  if ($LASTEXITCODE -eq 0) { Report 'OK' $Item "$Label opens" }
  elseif (-not $Engine) { Show-Line 'WARN' $Item ("Google Chrome did not open (Chromium covers it): " + (Error-Line $out)) }
  else { Report 'FAIL' $Item ("$Label did not open: " + (Error-Line $out)) }
  & npx -y $PlaywrightCli $session close *> $null
}

if (-not $Browser) {
  Show-Line 'SKIP' 'browser' 'run with -Browser to test (optional)'
} elseif (-not $haveNpx) {
  Report 'SKIP' 'browser' 'npx is not installed'
} else {
  Check-Browser 'browser-chrome' 'chrome' ''
  Check-Browser 'browser-chromium' 'chromium' 'chromium'
  Check-Browser 'browser-firefox' 'firefox' 'firefox'
  Check-Browser 'browser-webkit' 'webkit' 'webkit'
}

if ($script:Problems -eq 0) {
  Write-Output 'ALL OK'
  exit 0
}
Write-Output "$($script:Problems) item(s) need attention"
exit 1
