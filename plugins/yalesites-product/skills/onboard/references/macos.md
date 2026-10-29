# Mac setup

Read this when the check says the computer is a Mac (`uname -s` prints `Darwin`). Run the check with `check-setup.sh`. It covers Command Line Tools, Homebrew, the command-line tools, and how to restart.

## Choose a path

Which way to get the tools depends on the Command Line Tools (`clt`) and admin rights. Ask the admin question from the Homebrew section when you need it.

| Situation | Path |
|---|---|
| `OK clt` | Homebrew in the home folder (no admin). |
| `MISS clt`, and they have permanent admin | The official Homebrew installer, which adds the Command Line Tools itself. |
| `MISS clt`, no admin, IT can help soon | Ask IT first (below), then Homebrew in the home folder. |
| `MISS clt`, no admin, IT cannot help or cannot help soon | mise (see "No admin and no Command Line Tools"). |

## Command Line Tools (`clt`)

These give the Mac `git` (tracks changes to files), `python3` (runs small helper scripts), and the compiler Homebrew needs when a tool has to be built from source.

If the check says `MISS clt` and they have no permanent admin, the home-folder Homebrew install needs them first. That install is not a git checkout, so `brew update` needs a real `git`, and without the tools `/usr/bin/git` is only an Apple placeholder that needs admin rights. So ask IT first:

- Put this first in the checklist. Tell them to send IT: "Please install Xcode Command Line Tools on my Mac." Yale's Self Service app may also offer them. With admin, `xcode-select --install` works.
- Pause until IT installs them, and re-run the check. Do not install Homebrew yet.
- If IT says no, or cannot help soon, offer the mise fallback below instead. Say plainly that it is a different route and that the person can switch to Homebrew later if IT installs the tools.

The official installer (the admin aside below) installs the Command Line Tools itself, so `MISS clt` does not block that path.

## No admin and no Command Line Tools: mise

`/yalesites-product:ticket` does not need `git` or a compiler. It needs `gh`, `jq`, `node` (for `npx` and the browser helper) and `python3`. mise is one small program that installs ready-made copies of those into the home folder. No password, no compiler, no Command Line Tools, no git.

Say first: "mise is a tool that downloads ready-made copies of gh, jq, node, and python into your own folder. It needs no password and no Apple developer tools." Ask "OK to install it?" Then:

```bash
curl https://mise.run | sh
MISE_PYTHON_COMPILE=0 ~/.local/bin/mise use -g node@lts gh jq python@3.12
```

`MISE_PYTHON_COMPILE=0` makes mise use ready-made Python and never try to compile one. Do not run `git` or `python3` from `/usr/bin` here. They are Apple placeholders that pop up an "install developer tools" window. If that window appears, tell them to click Cancel.

### Link mise to the shell (all three files)

Claude Desktop starts shells that are not interactive and not login shells, so `mise activate` alone is not enough. zsh reads `~/.zshenv` for every shell, so the tools must be on the search path there. Ask: "OK if I add lines to three of your Terminal settings files so the tools work in Terminal and in Claude?" Add each line only if it is not already there (grep first, never twice):

```bash
add_line() { grep -qF "$2" "$1" 2>/dev/null || printf '\n%s\n' "$2" >> "$1"; }
add_line "$HOME/.zshenv"   'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"'
add_line "$HOME/.zprofile" 'eval "$(~/.local/bin/mise activate zsh --shims)"'
add_line "$HOME/.zshrc"    'eval "$(~/.local/bin/mise activate zsh)"'
```

The `.zshenv` line puts mise first, ahead of `/usr/bin`, so mise's `python3` wins over Apple's placeholder. In your own commands, run `export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"` first.

After `npm install -g` for the browser helper, run `~/.local/bin/mise reshim` so `playwright-cli` appears. The helper is tied to this node version, so after a node upgrade, run onboarding again.

Update on this path with `~/.local/bin/mise upgrade` (no sudo).

## Homebrew (`brew`)

Homebrew is an app store for command-line tools. Everything after this uses it.

If the check shows `WARN brew-path`, Homebrew is installed but this window cannot find it. Skip to "Link brew to the shell" below.

If `MISS brew`, ask this question in plain words. Use the `INFO admin` line only as a hint, because many Yale Macs give temporary admin through a "make me admin" button, and the check passes during that window:

> Can you install apps on this Mac yourself any time, without asking IT or using a "make me admin" button? If you are not sure, choose No.

**No, or not sure (the default): install into the home folder.** Only when the check shows `OK clt` (see "Choose a path"). No password, no admin rights. Tell them first: "Homebrew calls this way unsupported. Some tools get built from source on your Mac, so installs can take longer. gh, jq, and node usually come ready-made, but if not, it is only slower." Then ask "OK to install it?" and run:

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

- Where a path says `brew`, the mise path uses `mise` instead (see above). Both end the same way: gh, jq, node, python3, and npx visible from every shell.
- Check script: `bash "${CLAUDE_SKILL_DIR}/scripts/check-setup.sh"` (add `--browser` for the browser test).
- The GitHub login is stored in the Mac keychain and `~/.config/gh`, so it works in every folder. The person runs the login in the Terminal app (Command and Space, type Terminal, press Return).
- Browsers install into `~/Library/Caches/ms-playwright`.
- The default browser check uses the installed Google Chrome. Most Yale Macs have it. Without Chrome, use `--browser chromium`.
- Restart: quit Claude Desktop completely with Command and Q. Closing the window is not enough. Open it again and start a new session.
