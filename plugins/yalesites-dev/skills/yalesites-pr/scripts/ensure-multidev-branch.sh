#!/usr/bin/env bash
# Make sure yalesites-project has a same-named branch with at least one commit,
# so a companion PR (atomic, component-library-twig, tokens) gets a multidev.
#
#   ensure-multidev-branch.sh <branch> <companion-repo#N> <yalesites-project checkout>
#
# yalesites-project's build (.ci/build/build_frontend) builds the component
# library and atomic branch that share its PR branch's name, so a companion
# change is only testable in Drupal once a yalesites-project PR exists on the
# same branch. When the change has no yalesites-project code, that branch holds
# one empty commit.
#
# Never checks anything out and never touches the working tree: the commit is
# built with `git commit-tree`, so a shared local checkout is left as it is.
#
# Prints one line: `existing` (branch already on origin with its own commits, no
# change made) or `created <sha>` (empty commit pushed).
set -euo pipefail

branch="${1:?usage: $0 <branch> <companion-repo#N> [checkout]}"
companion="${2:?usage: $0 <branch> <companion-repo#N> <yalesites-project checkout>}"
repo="${3:?usage: $0 <branch> <companion-repo#N> <yalesites-project checkout>}"
issue="${branch%%-*}"

origin_url=$(git -C "$repo" remote get-url origin)
case "$origin_url" in
  *yalesites-org/yalesites-project|*yalesites-org/yalesites-project.git) ;;
  *) echo "refusing: $repo origin is $origin_url, not yalesites-org/yalesites-project" >&2; exit 1 ;;
esac

git -C "$repo" fetch -q origin develop
if git -C "$repo" ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  git -C "$repo" fetch -q origin "$branch"
  ahead=$(git -C "$repo" rev-list --count "origin/develop..origin/$branch")
  if [ "$ahead" -gt 0 ]; then
    echo existing
    exit 0
  fi
fi

sha=$(git -C "$repo" commit-tree 'origin/develop^{tree}' -p origin/develop -F - <<MSG
chore($issue): open multidev for $companion

No yalesites-project change. This branch shares its name with
$companion so CI builds that branch into a multidev for testing.

Created with AI
MSG
)
# Push the commit by sha: no local ref moves, so it works even when `branch` is
# checked out (or not present) locally.
git -C "$repo" push origin "$sha:refs/heads/$branch"
echo "created $sha"
