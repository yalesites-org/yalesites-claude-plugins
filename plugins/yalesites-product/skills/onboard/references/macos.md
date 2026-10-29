# Mac setup

Read this when the check says the computer is a Mac (`uname -s` prints `Darwin`). Run the check with `check-setup.sh`. It covers Command Line Tools, Homebrew, the command-line tools, and how to restart.

## Command Line Tools (`clt`)

These give the Mac `git` (tracks changes to files), `python3` (runs small helper scripts), and the compiler Homebrew needs when a tool has to be built from source.

If the check says `MISS clt`, the home-folder Homebrew install below is **blocked**. That install is not a git checkout, so `brew update` needs a real `git`. Without the Command Line Tools, `/usr/bin/git` is only an Apple placeholder that needs admin rights. Building from source needs the same compiler. So:

- Tell them in plain words: "Ask IT or desktop support to install 'Xcode Command Line Tools'. If your Mac has Yale's Self Service app, look for it there."
- Stop here. Do not install Homebrew and do not try `brew install git`. When they say it is installed, re-run the check and carry on once `OK clt` shows.

The official installer (the admin aside below) installs the Command Line Tools itself, so `MISS clt` does not block that path.

## Homebrew (`brew`)

Homebrew is an app store for command-line tools. Everything after this uses it.

If the check shows `WARN brew-path`, Homebrew is installed but this window cannot find it. Skip to "Link brew to the shell" below.

If `MISS brew`, ask this question in plain words. Use the `INFO admin` line only as a hint, because many Yale Macs give temporary admin through a "make me admin" button, and the check passes during that window:

> Can you install apps on this Mac yourself any time, without asking IT or using a "make me admin" button? If you are not sure, choose No.

**No, or not sure (the default): install into the home folder.** Only when the check shows `OK clt` (see above). No password, no admin rights. Tell them first: "Homebrew calls this way unsupported. Some tools get built from source on your Mac, so installs can take longer. gh, jq, and node usually come ready-made, but if not, it is only slower." Then ask "OK to install it?" and run:

```bash
mkdir -p "$HOME/homebrew" && curl -fsSL https://github.com/Homebrew/brew/tarball/master | tar xz --strip-components 1 -C "$HOME/homebrew"
eval "$("$HOME/homebrew/bin/brew" shellenv)"
brew update --force --quiet
```

The prefix is `$HOME/homebrew`.

**Yes (optional aside): the official installer.** It asks for the Mac password, which you cannot type for them. Ask them to open the Terminal app (press Command and Space, type Terminal, press Return), paste this one line, and press Return:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Warn them: when asked for a password, typing shows nothing on screen. That is normal. Type it and press Return. It may also open an Apple window offering the Command Line Tools. Say yes to it. When it finishes, ask them to tell you. The prefix is `/opt/homebrew` on Apple Silicon Macs or `/usr/local` on Intel Macs.

### Link brew to the shell

Whichever prefix was used, the Mac needs to know where brew lives. Claude Desktop gets its search path from the Terminal settings files, so write the line to BOTH. Ask: "OK if I add one line to your Terminal settings files so brew works everywhere?" Then add the line to `~/.zprofile` and `~/.zshrc`, only if it is not already there. Never add it twice:

```bash
LINE='eval "$(<prefix>/bin/brew shellenv)"'
for f in "$HOME/.zprofile" "$HOME/.zshrc"; do
  grep -qF "$LINE" "$f" 2>/dev/null || printf '\n%s\n' "$LINE" >> "$f"
done
```

Replace `<prefix>` with the real path before running. In your own commands, run the `eval` line first so brew works right now. The restart that makes it permanent is the "Restart Claude" step in `SKILL.md`.

## The tools

Ask once: "OK to install gh, jq, and node with Homebrew?" Install only what the check marked `MISS`. `git` and `python3` come with the Command Line Tools. Say what each is for:

- `gh`: lets Claude create and update tickets on GitHub for you.
- `git`: tracks changes to files. Already there once the Command Line Tools are installed.
- `jq`: reads the data GitHub sends back.
- `node`: runs a few small helper steps, including the browser helper (through `npm` and `npx`).
- `python3`: runs the ticket skill's text checker and screenshot helper. Already there once the Command Line Tools are installed.

```bash
brew install gh jq node
```

Re-run the check. In the home-folder install some packages may build from source, so allow extra time and say so.

## Mac details for the shared steps

- Check script: `bash "${CLAUDE_SKILL_DIR}/scripts/check-setup.sh"` (add `--browser` for the browser test).
- The GitHub login is stored in the Mac keychain and `~/.config/gh`, so it works in every folder. The person runs the login in the Terminal app (Command and Space, type Terminal, press Return).
- Browsers install into `~/Library/Caches/ms-playwright`.
- The default browser check uses the installed Google Chrome. Most Yale Macs have it. Without Chrome, use `--browser chromium`.
- Restart: quit Claude Desktop completely with Command and Q. Closing the window is not enough. Open it again and start a new session.
