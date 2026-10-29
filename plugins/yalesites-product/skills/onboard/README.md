# Onboard: set up your computer for YaleSites tickets

This sets up your computer so Claude can create YaleSites tickets for you, and take browser screenshots to go with them. Claude does the installing. You only step in for a few things, like signing in to GitHub.

**What this covers:** getting you ready to use Claude to create and groom YaleSites tickets (`/yalesites-product:ticket`), plus taking browser screenshots for those tickets. It does not set up a developer computer (Lando, Docker, Drupal, code changes) or other YaleSites workflows. More may be added later.

## Before you start

- A Mac, or a Windows computer. (Most people use a Mac. The Windows steps have not been tested on a real Windows computer yet, so tell the YaleSites team if something looks different.)
- On a Mac only: **Xcode Command Line Tools**. These are Apple's free developer tools. They give your Mac `git` and the build tools everything else needs. To check, open Terminal (Command and Space, type Terminal, press Return) and run `xcode-select -p`. If it prints a folder path, you have them. If you do not have admin rights, ask IT or look in Yale's Self Service app for them BEFORE you start, so you do not stall halfway. If you have permanent admin rights, the official Homebrew installer adds them for you.
- The Claude desktop app, installed and signed in.
- A GitHub account that is a member of the `yalesites-org` organization. If you are not a member yet, ask the YaleSites team to invite you.
- About 20 to 30 minutes.
- You do **not** need admin rights.

## Step by step

### On a Mac

1. Open the Claude desktop app and go to the **Code** tab. Any folder is fine. Your home folder works.
2. Type this and press Return:
   ```
   /plugin marketplace add yalesites-org/yalesites-claude-plugins
   ```
3. Type these two lines, one at a time, pressing Return after each. If it asks where to install, pick the user choice, not "project". That makes them work in every folder.
   ```
   /plugin install yalesites-product@yalesites-claude-plugins
   /plugin install yalesites@yalesites-claude-plugins
   ```
4. Type this and follow along:
   ```
   /yalesites-product:onboard
   ```

### On Windows

Do the same four steps. Use the Claude desktop app and its **Code** tab. Claude then installs a tool called Scoop, which also needs no admin rights.

### What to expect

- Claude asks before it installs anything. Say yes to each one.
- It asks whether you have permanent admin rights on your computer. If you are not sure, say **No**. That is the normal answer here.
- It installs a package manager (Homebrew on a Mac, Scoop on Windows) into your own folder. Then it installs `gh` (talks to GitHub), `git`, `jq`, `node`, and `python`. Then, if you agree, a browser tool and three browsers.
  - Chromium is the engine Chrome is built on.
  - Firefox is Firefox.
  - WebKit is the engine behind Safari.
- You sign in to GitHub once, in your browser. You copy an 8-character code from the window into the GitHub page.
- At the end, quit Claude completely and open it again (see the table below). Then run `/yalesites-product:onboard` once more. Everything should show OK.

Later browser steps pick a browser with `--browser chromium`, `--browser firefox`, or `--browser webkit`. With no flag, they use Google Chrome. If you only have Edge, use `--browser chromium` (or `--browser msedge`).

## When you see this, do this

| You see | What to do |
|---|---|
| Claude says "OK to install...?" | Say yes. It tells you what the thing is for. |
| Claude asks a Claude permission question to run a command | Read the short description. If it matches what Claude said it was about to do, choose to allow it. |
| A Mac password prompt (only on the admin path, which you will not see by default) | Type your Mac password. Nothing shows on screen while you type. That is normal. Press Return. |
| A GitHub page asking for a one-time code | Copy the 8-character code from the window, paste it on the page, sign in, and click **Authorize**. |
| A GitHub button saying **Authorize yalesites-org** (single sign-on) | Click it and sign in with your Yale login. |
| An Apple pop-up about "Command Line Tools", or Claude says they are missing (Mac) | If the pop-up asks, click Install. If you cannot, ask IT or desktop support to install "Xcode Command Line Tools", or look in Yale's Self Service app. Claude stops and waits, because the Mac setup needs them. Tell Claude when they are installed and it carries on. |
| Windows SmartScreen or a PowerShell security question | This is expected for the Scoop install. Choose the option that lets it run (for the PowerShell question, type `Y` and press Return). If your computer blocks it, ask IT. |
| Windows asks about Credential Manager or saved credentials | Allow it. This is where Windows keeps your GitHub sign-in. |
| "Quit Claude and reopen it" | On a Mac, press Command and Q. On Windows, close Claude, then click the small arrow near the clock, right-click the Claude icon, and choose Quit. Closing the window is not enough. |

## Check it worked

After the restart, run `/yalesites-product:onboard` again. Every required line should say OK. The browser lines are optional.

Then try `/yalesites-product:ticket` with a small sample idea, like "add a dark mode toggle to the footer". Tell Claude it is only a test and to stop before it creates anything.

## If something goes wrong

- **A pop-up asks to install command line developer tools (Mac):** If you have admin rights, click Install. If not, ask IT to install "Xcode Command Line Tools".
- **"command not found" after setup:** Quit Claude completely and open it again, then start a new session.
- **"Not a member of yalesites-org":** Ask the YaleSites team to invite you. Accept the email invite, then run onboarding again.
- **GitHub shows a 403 or single sign-on message:** Open the link GitHub shows and click Authorize next to yalesites-org.
- **Installs are slow:** Normal on the no-admin path. Some tools get built on your computer. Let it finish.
- **Not sure where you are:** Run `/yalesites-product:onboard` again. It is always safe to re-run. It skips anything already done.

## Keeping things up to date

About once a month, or when something stops working, update your tools. The easiest way: run `/yalesites-product:onboard` again. It checks everything and offers updates.

To do it by hand:

- **Mac tools:** `brew update && brew upgrade`
- **Windows tools:** `scoop update; scoop update *`
- **Browser helper:** `npm install -g @playwright/cli@0.1.22`. The team pins this version on purpose, so do not switch to `@latest`. When a skill changes the pinned version, running onboarding again installs the new one.
- **Browsers:** run the three `npx -y @playwright/cli@0.1.22 install-browser` lines again, with `chrome-for-testing`, `firefox`, and `webkit`.
- **GitHub sign-in:** it lasts until you or GitHub revoke it. Run `gh auth status` only when something fails.
- **Claude plugins:** run `/plugin marketplace update yalesites-claude-plugins`, then open `/plugin` and choose update, or run `/reload-plugins`.
- **Command Line Tools (Mac):** use Software Update in System Settings. If you do not have admin rights, ask IT.

## What it changes on your computer

| What | Where | Undo |
|---|---|---|
| Homebrew (Mac, no admin path) | `~/homebrew` | Delete the `~/homebrew` folder. |
| Homebrew (Mac, admin path) | `/opt/homebrew` or `/usr/local` | Run Homebrew's official uninstall script (needs admin). |
| Two lines that start with `eval "$(` and mention `brew shellenv` | `~/.zprofile` and `~/.zshrc` (Mac) | Delete those lines. |
| Scoop and the tools it installs (Windows) | `%USERPROFILE%\scoop` | Run `scoop uninstall scoop`, or delete the `%USERPROFILE%\scoop` folder. |
| `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` (Windows, run by the Scoop install) | Your user's PowerShell settings | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Undefined`. |
| Your GitHub sign-in | Mac keychain, or Windows Credential Manager | Run `gh auth logout`. |
| The browser tool | A global npm package, `@playwright/cli` | Run `npm uninstall -g @playwright/cli`. |
| Chromium, Firefox, and WebKit | `~/Library/Caches/ms-playwright` (Mac) or `%LOCALAPPDATA%\ms-playwright` (Windows) | Delete that folder. |
| The two Claude plugins | Your Claude Code settings | Run `/plugin uninstall yalesites-product@yalesites-claude-plugins` and the same for `yalesites@yalesites-claude-plugins`. |

Everything is installed for your user only. Nothing is tied to one folder.
