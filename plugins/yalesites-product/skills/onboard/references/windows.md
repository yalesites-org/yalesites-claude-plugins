# Windows setup

Read this when the check says the computer is Windows (`uname -s` contains MINGW, MSYS, or CYGWIN, or `$env:OS` is `Windows_NT` in PowerShell). This path has not been tested on a real Windows machine yet. If something behaves differently from what is written here, say so plainly, fix what you can, and tell the person to ask the YaleSites team lead.

Linux is out of scope. Say so politely and stop.

## Which check script

Run the PowerShell check, even when the session uses Git Bash:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\check-setup.ps1"
```

`-ExecutionPolicy Bypass` applies to that one run only and changes no setting. Add `-Browser` for the browser test. The lines look the same as on a Mac. Extra Windows lines: `scoop` (the package manager), and `<tool>-path` warnings when a tool is installed but not yet visible.

## Package manager: Scoop

Scoop installs tools into the user's own folder, needs no admin rights, and adds itself to the user's search path. Use it as the default, whether or not the person has admin rights. (People who already use winget can use `winget install --scope user <id>` instead. Do not push it.)

If the person asks about admin rights, ask the same plain question as on a Mac: "Can you install apps on this computer yourself any time, without asking IT? If you are not sure, choose No." The answer does not change the default. Scoop is used either way.

Say first: "Scoop is an app store for command-line tools. It installs into your own folder and needs no password." Then ask "OK to install it?" and run it in PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

The first line lets PowerShell run Scoop's own scripts. It is for this user only. If Windows shows a SmartScreen or policy question, tell them it is expected and to choose the option that lets it run (for the policy question, `Y`). If the computer blocks it by company policy, they should ask IT, and you stop that branch.

## The tools

Claude Code on Windows needs Git for Windows (it brings Git Bash), so install git first. Ask once: "OK to install git, gh, jq, node, and python with Scoop?" Install only what the check marked `MISS`:

```powershell
scoop install git
scoop install gh jq nodejs-lts python
```

What each is for:

- `git`: tracks changes to files, and gives Claude its command window (Git Bash).
- `gh`: lets Claude create and update tickets on GitHub for you.
- `jq`: reads the data GitHub sends back.
- `nodejs-lts` (`node`): runs a few small helper steps, including the browser helper.
- `python` (`python3`): runs the ticket skill's text checker and screenshot helper. On Windows the command is `python`.

Scoop adds its folder (`%USERPROFILE%\scoop\shims`) to the user's search path. Claude only sees that after a full restart (see below). Until then the check shows `WARN` lines such as `gh-path`. The check also looks in `%USERPROFILE%\scoop\shims` and in `%USERPROFILE%\scoop\apps\nodejs-lts\current` and its `bin` folder, because node, npm and npx live there, and `npm -g` puts `playwright-cli` there too. It reports a `WARN <tool>-path` line when a tool is in one of those folders but not on the search path. To carry on before the restart, open a new window, or run the tool by its full path from the folder named in the warning.

Re-run the check.

## Windows details for the shared steps

- The GitHub login is stored in Windows Credential Manager, so it works in every folder. The person runs the login in PowerShell (press the Windows key, type PowerShell, press Return) or in Git Bash.
- Browsers install into `%LOCALAPPDATA%\ms-playwright`.
- With no `--browser` flag, playwright-cli 0.1.22 uses Google Chrome only, never Edge. Someone with only Edge uses `--browser chromium`, or `--browser msedge`, which is also valid. If the default fails, Chromium covers it.
- The global helper is `npm install -g @playwright/cli@0.1.22`. It needs no admin rights because Scoop's node keeps global packages in the user folder.
- Restart: close every Claude window, then fully quit Claude from the system tray. Click the small arrow near the clock (bottom right), right-click the Claude icon, and choose Quit. Closing the window is not enough. Open Claude again and start a new session.
