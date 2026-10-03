#!/usr/bin/env python3
"""Push a screenshot to yalesites-org/ys-screenshots and print a markdown image line.

GitHub's own image upload (the `user-attachments` URLs you get from dragging an
image into a comment) only works from a logged-in browser. `gh` and API tokens
cannot reach it. This script is the workaround: it commits the image to a private
org repo and prints an <img> tag that points at it. Paste that tag into a ticket
or comment.

    python3 post-screenshot.py shot.png --ticket yalesites-org/YaleSites-Internal#1785 \\
        --alt "Results & filters tab renders blank" --slug item5-results-filters-blank

How the image renders, from the 2026-10-02 tests (YaleSites-Internal#1865):

- The link must be a `github.com/<org>/<repo>/raw/<ref>/<path>` URL. GitHub does
  not route those through its image proxy, so the viewer's browser sends its own
  GitHub login. A `raw.githubusercontent.com` link renders as a broken image.
- Only people with access to ys-screenshots see the image. That is every org
  member, so it works in YaleSites-Internal (private). In a public repo, outside
  readers get a broken image, so the script refuses a public target outright.
- The link is pinned to the commit that added the file, so it survives a file
  being moved by mistake. Files in ys-screenshots are never deleted.

Exit codes: 0 success, 2 bad input, 3 public target repo, 4 GitHub call failed.

Stdlib only. Shells out to `gh`, which must be logged in with write access to
ys-screenshots (every org member has it by default).
"""

from __future__ import annotations

import argparse
import base64
import datetime
import html
import json
import os
import re
import subprocess
import sys
from typing import Callable

DEST_REPO = "yalesites-org/ys-screenshots"
DEFAULT_OWNER = "yalesites-org"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_BYTES = 5 * 1024 * 1024
DEFAULT_WIDTH = 600
SLUG_MAX = 60


class InputError(ValueError):
    """Bad arguments or an unusable file. Exit code 2."""


class PublicRepoError(RuntimeError):
    """The ticket lives in a public repo, where the image would not render. Exit code 3."""


class GitHubError(RuntimeError):
    """A `gh` call failed. Exit code 4."""


# ---------------------------------------------------------------------------
# Pure helpers (covered by test_post_screenshot.py, no network)
# ---------------------------------------------------------------------------


def parse_ticket(ref: str) -> tuple[str, str, int]:
    """Split `owner/repo#123` (or `repo#123`) into (owner, repo, number).

    The team always writes cross-repo references in full `owner/repo#number`
    form, so that is the form accepted here. A bare `#123` is rejected because it
    does not say which repo the ticket is in.
    """
    m = re.fullmatch(r"(?:([A-Za-z0-9-]+)/)?([A-Za-z0-9._-]+)#(\d+)", ref.strip())
    if not m:
        raise InputError(
            f"--ticket must look like yalesites-org/YaleSites-Internal#1785, got {ref!r}"
        )
    owner, repo, number = m.group(1) or DEFAULT_OWNER, m.group(2), int(m.group(3))
    if number <= 0:
        raise InputError(f"ticket number must be positive, got {number}")
    return owner, repo, number


def slugify(text: str) -> str:
    """Lowercase, hyphen-separated, ASCII-only, at most SLUG_MAX characters."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = slug[:SLUG_MAX].rstrip("-")
    if not slug:
        raise InputError(f"could not make a file name out of {text!r}; pass --slug")
    return slug


def check_file(name: str, size: int) -> str:
    """Return the normalised extension, or raise if the file can't be posted."""
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise InputError(f"{name}: unsupported file type {ext or '(none)'}; use one of {allowed}")
    if size > MAX_BYTES:
        raise InputError(f"{name}: {size / 1024 / 1024:.1f}MB is over the 5MB limit")
    if size == 0:
        raise InputError(f"{name}: file is empty")
    return ".jpg" if ext == ".jpeg" else ext


def build_path(repo: str, number: int, date: datetime.date, slug: str, ext: str) -> str:
    """`<repo>/<number>/<YYYY-MM-DD>-<slug><ext>`, the layout in the ys-screenshots README."""
    return f"{repo}/{number}/{date.isoformat()}-{slug}{ext}"


def next_free_path(path: str, exists: Callable[[str], bool]) -> str:
    """Return `path`, or the first `-2`, `-3`, ... variant that doesn't exist yet.

    Files in ys-screenshots are never overwritten: an old ticket may already
    link to the existing one.
    """
    if not exists(path):
        return path
    stem, ext = os.path.splitext(path)
    for n in range(2, 100):
        candidate = f"{stem}-{n}{ext}"
        if not exists(candidate):
            return candidate
    raise InputError(f"{path}: 98 files with this name already exist; pick a different --slug")


def image_url(sha: str, path: str, dest_repo: str = DEST_REPO) -> str:
    """Commit-pinned github.com raw URL. Never raw.githubusercontent.com (it won't render)."""
    return f"https://github.com/{dest_repo}/raw/{sha}/{path}"


def img_tag(url: str, alt: str, width: int | None = DEFAULT_WIDTH) -> str:
    """An <img> tag rather than ![](), so the width can be capped like dragged-in images are."""
    width_attr = f'width="{width}" ' if width else ""
    return f'<img {width_attr}alt="{html.escape(alt, quote=True)}" src="{url}" />'


# ---------------------------------------------------------------------------
# GitHub calls
# ---------------------------------------------------------------------------


def gh(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["gh", *args], input=stdin, capture_output=True, text=True, timeout=60
        )
    except FileNotFoundError:
        raise GitHubError("gh is not installed or not on PATH") from None
    except subprocess.TimeoutExpired:
        raise GitHubError(f"gh {' '.join(args[:2])} timed out") from None


def repo_visibility(owner: str, repo: str) -> str:
    r = gh(["api", f"repos/{owner}/{repo}", "--jq", ".visibility"])
    if r.returncode != 0:
        raise GitHubError(f"could not read {owner}/{repo}: {r.stderr.strip()}")
    return r.stdout.strip().lower()


def path_exists(path: str, dest_repo: str = DEST_REPO) -> bool:
    r = gh(["api", f"repos/{dest_repo}/contents/{path}", "--silent"])
    if r.returncode == 0:
        return True
    if "404" in r.stderr or "Not Found" in r.stderr:
        return False
    raise GitHubError(f"could not check {path}: {r.stderr.strip()}")


def put_file(path: str, data: bytes, message: str, dest_repo: str = DEST_REPO) -> str:
    """Create the file via the contents API (no local clone) and return the commit SHA."""
    body = json.dumps(
        {"message": message, "content": base64.b64encode(data).decode("ascii"), "branch": "main"}
    )
    r = gh(
        ["api", "-X", "PUT", f"repos/{dest_repo}/contents/{path}", "--input", "-", "--jq", ".commit.sha"],
        stdin=body,
    )
    if r.returncode != 0:
        raise GitHubError(f"could not upload {path}: {r.stderr.strip()}")
    sha = r.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise GitHubError(f"unexpected response uploading {path}: {r.stdout.strip()!r}")
    return sha


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Push a screenshot to ys-screenshots and print an <img> tag for a ticket or comment."
    )
    ap.add_argument("image", help="path to the image (PNG, JPG, WebP or GIF, up to 5MB)")
    ap.add_argument("--ticket", required=True, help="where it will be posted, e.g. yalesites-org/YaleSites-Internal#1785")
    ap.add_argument("--alt", required=True, help="alt text: what the screenshot shows, in plain words")
    ap.add_argument("--slug", help="short file name, e.g. item5-results-filters-blank (default: from the alt text)")
    ap.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"display width in px, 0 for none (default {DEFAULT_WIDTH})")
    ap.add_argument("--date", help="YYYY-MM-DD for the file name (default: today)")
    ap.add_argument("--dry-run", action="store_true", help="check everything and print the path, but upload nothing")
    args = ap.parse_args(argv)

    try:
        owner, repo, number = parse_ticket(args.ticket)
        if not args.alt.strip():
            raise InputError("--alt can't be empty; screen reader users need it")
        if not os.path.isfile(args.image):
            raise InputError(f"{args.image}: no such file")
        ext = check_file(args.image, os.path.getsize(args.image))
        slug = slugify(args.slug or args.alt)
        try:
            date = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
        except ValueError:
            raise InputError(f"--date must be YYYY-MM-DD, got {args.date!r}") from None

        visibility = repo_visibility(owner, repo)
        if visibility != "private":
            raise PublicRepoError(
                f"{owner}/{repo} is {visibility or 'not private'}. Images from ys-screenshots only show for "
                "org members, so outside readers there would see a broken image. Drag the image into "
                "the comment by hand instead."
            )

        path = next_free_path(build_path(repo, number, date, slug, ext), path_exists)
        if args.dry_run:
            print(f"dry run: would upload {args.image} to {DEST_REPO}/{path}", file=sys.stderr)
            print(img_tag(image_url("<sha>", path), args.alt, args.width or None))
            return 0

        with open(args.image, "rb") as fh:
            data = fh.read()
        sha = put_file(path, data, f"chore: add screenshot for {owner}/{repo}#{number}")
        print(img_tag(image_url(sha, path), args.alt, args.width or None))
        return 0
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except PublicRepoError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 3
    except GitHubError as e:
        print(f"github: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
