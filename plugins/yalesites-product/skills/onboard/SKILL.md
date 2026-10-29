---
name: onboard
description: "Walk a non-technical product or content person through setting up their Mac or Windows computer so the `ticket` skill works, from a blank machine to a green check. Claude runs the checks and installs, explains each step in plain words, and stops only where the person must act (a browser login, an org invite). Covers a package manager that needs no admin rights (Homebrew on Mac, Scoop on Windows), gh, git, jq, node, python3, the GitHub login with the `project` scope, access to the yalesites-org GitHub org and the YaleSites Board, an optional browser for screenshots, and the Claude Code plugins. Use when the user says 'onboard', 'set up my computer for YaleSites', 'get me set up to make tickets', 'install the prerequisites', 'I have never used a terminal', or when the ticket skill reports that gh is not installed or not authenticated or lacks the project scope. Safe to re-run: on a ready machine it reports all green in a few lines. Scope today: getting ready to create and groom tickets with `/yalesites-product:ticket`, plus browser screenshots for them. NOT for developer environment setup (Lando, Docker, Drupal, code changes, SSH keys, git name and email) or other YaleSites workflows."
---

# Onboard

Get a non-technical teammate's computer ready so `/yalesites-product:ticket` can create and groom tickets from start to finish. You run the checks and the installs. The person only acts where a computer cannot act for them.

Everything is set up for the user, not for one project folder. This skill works from any folder, including the home folder. Do not assume a working directory.

## How to talk

The reader has never used a terminal. Keep it plain.

- Short sentences. No em dashes. No jargon without a few-word gloss.
- Say what each thing is for in one line. Example: "gh lets Claude create tickets on GitHub for you."
- Before any install, say what it is and ask "OK to install it?" Do not install without a yes.
- Never paste a wall of command output. Summarize it.

## Scope

Mac and Windows. Linux is out of scope: say so politely, suggest they ask the YaleSites team lead, and stop.

Scope today is getting ready to create and groom tickets with `/yalesites-product:ticket`, plus browser screenshots for those tickets. More may be added later. Out of scope, and do not offer: developer setup such as Lando, Docker, Drupal, code changes, git name and email, SSH keys, and setup for other YaleSites workflows. If asked, say that is developer setup and point them to the team.

## Never do these

- Do not run `gh auth login`, `gh auth refresh`, or any command that asks for a password or opens a code prompt. You cannot answer them. The person runs them.
- Do not use `sudo`, and do not ask for an administrator window.
- Do not create a real GitHub issue. The final check is a dry run only.
- Do not edit shell files without asking first.

## Step 1. Pick the system, then run the check

Find out which system this is. On a Mac, `uname -s` prints `Darwin`. On Windows it contains `MINGW`, `MSYS`, or `CYGWIN` (Git Bash), or `$env:OS` is `Windows_NT` (PowerShell). Then read the matching file and use its check command:

- Mac: `references/macos.md`, check with `scripts/check-setup.sh`
- Windows: `references/windows.md`, check with `scripts/check-setup.ps1`

Use `${CLAUDE_SKILL_DIR}` for the skill folder. If it is empty, use the full path to this skill's folder. The scripts only read. They print one line per item: `OK`, `MISS` (not installed), `FAIL` (installed but not usable), `WARN` (works but needs a fix), `SKIP` (not checked), or `INFO` (just a fact).

Turn the result into a short checklist for the person: what is done, what is left, in plain words. On a Mac, if the check shows `MISS clt` and the person does not have permanent admin rights, put that first in the checklist as the thing that blocks the Homebrew route. Give them these exact words to send IT: "Please install Xcode Command Line Tools on my Mac." (Yale's Self Service app may also offer them.) If they do have admin rights, they can run `xcode-select --install` themselves. Ask IT first. If IT says no or cannot help soon, do not leave them stuck: the Mac file has a no-admin fallback (mise) that needs neither admin rights nor the Command Line Tools. Pause for IT only if they want to wait. Mark the browser items (`playwright`, `browser-*`) as optional. If everything required is `OK`, say so in a few lines and go to Step 8. Plugin state cannot be checked from a script, so ask about plugins in Step 7 even when the check is green.

## Step 2. Fix in this order

Fix one thing at a time, in dependency order, and re-run the check after each fix: the package manager and tools (from the system file), then the GitHub login, then org access, then the browsers, then a Claude restart, then plugins. A later step often depends on an earlier one.

## Step 3. Package manager and tools

Follow the system file. On a Mac, the file has a short table to choose the path: Homebrew in the home folder when the Command Line Tools are there, the official installer for people with permanent admin, and mise when there is no admin and IT cannot install the tools. Ask IT first, because it is the first choice. It covers the package manager (Homebrew or mise on a Mac, Scoop on Windows, all without admin rights), the tools `gh`, `git`, `jq`, `node`, and `python3`, and linking them so Claude can see them. Ask before each install.

## Step 4. GitHub account, login, and access

**Account and org.** They need a GitHub account that belongs to the `yalesites-org` organization, with access to `yalesites-org/YaleSites-Internal` and the YaleSites Board. If they do not have one, or the repo check fails because they are not a member, say: "Ask the YaleSites team lead or your manager to invite you to the yalesites-org GitHub organization." Do not name a person. When the invite arrives by email, they accept it. Stop this branch until they have.

**Login (`gh-auth`, `gh-scope`).** Claude cannot do this part. Ask them to run this in the Terminal (Mac) or PowerShell (Windows), after you read them the plan:

```
gh auth login -h github.com -p https -w -s project
```

What will happen, in plain words: it shows an 8-character one-time code, then asks them to press Return to open the browser. They paste the code on the GitHub page, sign in, and click Authorize. Any other question can take the default. The `-s project` part gives the login permission to edit the YaleSites Board. Without it, tickets can be created but the board fields cannot be set. The login is saved for the user, so it works in every folder.

If they are already logged in but the check says `FAIL gh-scope`, the login is missing that permission. They run:

```
gh auth refresh -h github.com -s project
```

`read:project` alone is not enough, because it can read the board but cannot write to it.

Re-run the check after they say they are done.

**Access (`gh-repo`, `gh-board`).** These are read-only calls. If they fail with a 403 and the output mentions SSO, tell them: GitHub needs them to approve their login for the organization. Ask them to open the link GitHub or gh shows, or go to github.com, Settings, Applications, Authorized OAuth Apps, find "GitHub CLI", and click Authorize next to yalesites-org. If there is no SSO message, they are probably not in the org yet, so go back to the org step.

## Step 5. Browsers for screenshots (optional)

This lets Claude open a web page to reproduce a problem and take screenshots for your ticket. Installing all of them means a bug that only shows in one browser can still be reproduced. It is recommended, not required: `/yalesites-product:ticket` works without it. Say so, and let them skip.

Say what each one is, in one line:

- Chrome is the Google Chrome already on the computer, if there is one. It is the default when no flag is given. Edge is not used by default, so someone with only Edge uses `--browser chromium` (or `--browser msedge`).
- Chromium is the engine Chrome is built on.
- Firefox is Firefox.
- WebKit is the engine behind Safari.

Install the helper once for the whole computer, so it works from any folder and any session. The version is pinned the same way as in `pr-feedback/references/drive-it.md` ("Browsers"), which is the place to bump it. Ask once: "OK to install the browser helper and three browsers for Claude to use? Together they are a few hundred megabytes, so it takes a few minutes. They go in your own folder and need no password." Then run:

```bash
npm install -g @playwright/cli@0.1.22
npx -y @playwright/cli@0.1.22 install-browser chrome-for-testing
npx -y @playwright/cli@0.1.22 install-browser firefox
npx -y @playwright/cli@0.1.22 install-browser webkit
```

(`chrome-for-testing` is the name Playwright gives to Chromium.) The browsers go in the user's own cache folder (the system file names it). Do not install Google Chrome itself, which needs admin rights.

Then test each one end to end. This briefly opens each browser, so say that first. Run the check with `--browser` (Mac, `check-setup.sh`) or `-Browser` (Windows, `check-setup.ps1`). You get one line each: `browser-chrome`, `browser-chromium`, `browser-firefox`, `browser-webkit`. Each opens a blank page in its own session and closes it. If Chrome is missing, that line is only a `WARN`, because Chromium covers it. A `FAIL` on the other three means that install did not work: re-run its install line once, then mark it skipped and move on.

Tell them how later browser steps pick a browser: `--browser chromium`, `--browser firefox`, or `--browser webkit`. With no flag, Google Chrome is used.

## Step 6. Restart Claude so it sees the new tools

Skip this step if you changed no shell settings and installed nothing new.

Claude is a normal desktop app. It reads the computer's search path only when it starts. Until it restarts, it cannot see brew or scoop, gh, node, or npx. Tell them plainly, using the restart text in the system file:

1. Quit Claude completely. Closing the window is not enough.
2. Open it again and start a new session.
3. Run `/yalesites-product:onboard` again from the new session.

Re-running the check from the new session proves Claude can find everything, from any folder. Do these checks on every path, not only one:

1. Run the check script from the new session.
2. Run `command -v gh node npx jq python3 playwright-cli` (on Windows, `Get-Command gh, node, npx, jq, python, playwright-cli | Select-Object Name, Source`) and confirm each path is the expected one: the mise shims folder, the Homebrew folder, or the Scoop folder. On the mise path, `python3` must NOT be `/usr/bin/python3`.
3. If a tool resolves wrong or is missing, the fix is the shell file line plus a full Command and Q restart, not a reinstall.

## Step 7. Claude Code plugins

The skill flow cannot read plugin state, so ask. This is the one step they type themselves, because slash commands are typed by the person, not run by Claude. Ask them to type each of these into Claude Code, one at a time, and press Return:

```
/plugin marketplace add yalesites-org/yalesites-claude-plugins
/plugin install yalesites-product@yalesites-claude-plugins
/plugin install yalesites@yalesites-claude-plugins
```

The first adds the YaleSites list of plugins. The second holds the ticket skill. The third adds the YaleSites knowledge base, which the ticket skill uses to check whether an idea already exists on the platform. They can skip any line they have already done. Since they are running this skill, `yalesites-product` is already installed, so likely only the `yalesites` plugin remains. Ask them to confirm, or to run `/plugin` and look at the Installed tab.

Plain `/plugin install` installs for the user, so the plugins work in every folder. If a menu offers a scope, pick the user one, not "project". After installing, they should run `/reload-plugins` or start a new session.

## Step 8. Final check and dry run

Run the check one last time, from the restarted session if Step 6 applied. When every required line is `OK`, tell them in two or three sentences that they are ready. Mention the browser items if they were skipped. Then suggest:

> Try `/yalesites-product:ticket` with a sample idea, like "add a dark mode toggle to the footer". Say it is just a test and stop before it creates anything.

Do not create a real issue yourself during onboarding.

**Offer updates when everything is already green.** On a machine that is fully set up, ask once: "Everything is up to date enough to work. Want me to also update your tools? It is safe to skip." Only on a yes, run the update for this system (no `sudo` on either path):

- Mac with Homebrew: `brew update && brew upgrade`
- Mac with mise: `~/.local/bin/mise upgrade`
- Windows: `scoop update; scoop update *`

Then, if the browser helper and browsers were set up, reinstall the pinned versions from Step 5 (the same `npm install -g @playwright/cli@0.1.22` and three `install-browser` lines). Never move to `@latest`: the team pins that version on purpose. Point the person to "Keeping things up to date" in `README.md` for the rest, such as plugins, and do not repeat it in full.

If anything required is still not green, name the one thing left and what to do about it, and say to ask the YaleSites team lead when you cannot fix it.
