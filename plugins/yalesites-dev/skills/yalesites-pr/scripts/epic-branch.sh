#!/usr/bin/env bash
# Print the base branch for a YaleSites issue: the epic integration branch if the
# issue sits under an epic, else the repo default branch (also for the epic issue
# itself, whose own PR targets the default branch).
# The epic is the nearest of the issue, its parent, grandparent or great-grandparent
# carrying the YaleSites-Internal label "epic".
# Usage: epic-branch.sh <issue-number> <repo> [--ensure]
#   --ensure creates the epic branch (empty commit) and its draft Epic PR if missing.
# stdout is only the branch name. Diagnostics go to stderr. Works on bash 3.2.
set -euo pipefail

issue=${1:?usage: epic-branch.sh <issue> <repo> [--ensure]}
repo=${2:?usage: epic-branch.sh <issue> <repo> [--ensure]}
ensure=${3:-}
org=yalesites-org
repos=(yalesites-project atomic component-library-twig tokens)
default=develop
[[ $repo == tokens ]] && default=main
[[ " ${repos[*]} " == *" $repo "* ]] || { echo "unknown repo: $repo" >&2; exit 2; }

# shellcheck disable=SC2016  # $n is a GraphQL variable
q='fragment F on Issue{number title labels(first:20){nodes{name}}}
query($n:Int!){repository(owner:"yalesites-org",name:"YaleSites-Internal"){issue(number:$n){...F parent{...F parent{...F parent{...F}}}}}}'
info=$(gh api graphql -f query="$q" -F n="$issue" --jq '.data.repository.issue') \
  || { echo "cannot read issue $issue" >&2; exit 1; }
epic=$(jq -r '[., .parent, .parent.parent, .parent.parent.parent]
  | map(select(. != null and any(.labels.nodes[]; .name=="epic"))) | first
  | if . == null then "" else "\(.number)\t\(.title)" end' <<<"$info")
if [[ -z $epic ]]; then echo "$default"; exit 0; fi
IFS=$'\t' read -r num title <<<"$epic"
# The epic issue itself targets the default branch.
if [[ $num == "$issue" ]]; then echo "$default"; exit 0; fi
title=$(sed -E 's/^[[:space:]]*[Ee][Pp][Ii][Cc][[:space:]]*:[[:space:]]*//' <<<"$title")

# Prints the one branch named <epic>-* in repo $1 (empty if none); fails on API error or 2+ matches.
find_branch() {
  local refs m
  refs=$(gh api "repos/$org/$1/git/matching-refs/heads/$num-" --jq '.[].ref') \
    || { echo "API error listing branches in $1" >&2; return 1; }
  m=$(grep "^refs/heads/$num-" <<<"$refs" || true)
  m=${m//refs\/heads\//}
  if [[ $m == *$'\n'* ]]; then echo "several $num-* branches in $1: ${m//$'\n'/ }" >&2; return 1; fi
  printf '%s' "$m"
}

# Reuse any existing name: target repo first, then yalesites-project, then the rest.
order=("$repo")
[[ $repo != yalesites-project ]] && order+=(yalesites-project)
for r in "${repos[@]}"; do [[ $r != "$repo" && $r != yalesites-project ]] && order+=("$r"); done
branch="" found=""
for r in "${order[@]}"; do
  branch=$(find_branch "$r") || exit 1
  if [[ -n $branch ]]; then found=$r; break; fi
done
if [[ -z $branch ]]; then
  slug=$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed -E 's/^-+|-+$//g')
  slug=$(printf '%s' "$slug" | cut -c1-"$((40 - ${#num} - 1))" | sed -E 's/-+$//')
  branch="$num-$slug"
fi

if [[ $ensure == --ensure ]]; then
  api=repos/$org/$repo
  if [[ $found != "$repo" ]]; then
    echo "creating $branch in $repo" >&2
    read -r head tree < <(gh api "$api/commits/$default" --jq '.sha+" "+.commit.tree.sha')
    new=$(gh api "$api/git/commits" -f message="chore($num): start epic branch

Created with AI" -f tree="$tree" -f "parents[]=$head" --jq .sha)
    gh api "$api/git/refs" -f ref="refs/heads/$branch" -f sha="$new" --jq .ref >&2
  fi
  open=$(gh pr list -R "$org/$repo" --head "$branch" --state open --json number --jq length)
  if [[ $open == 0 ]]; then
    echo "opening draft PR for $branch in $repo" >&2
    label=()
    if out=$(gh api "$api/labels/Epic" 2>&1); then
      label=(--label Epic)
    elif [[ $out == *"Not Found"* || $out == *404* ]]; then
      echo "warning: no Epic label in $repo" >&2
    else
      echo "$out" >&2; exit 1
    fi
    gh pr create -R "$org/$repo" --draft --assignee @me ${label[@]+"${label[@]}"} --base "$default" --head "$branch" \
      --title "$num: $title" \
      --body "Integration branch for epic $org/YaleSites-Internal#$num. Sub-issue PRs target this branch.

References $org/YaleSites-Internal#$num

Created with AI" >&2
  fi
fi
echo "$branch"
