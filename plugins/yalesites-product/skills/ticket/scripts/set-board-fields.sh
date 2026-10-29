#!/usr/bin/env bash
# Put an issue on the YaleSites Board and set its single-select fields in one write.
# Usage: set-board-fields.sh <issue-number> Field=Value [Field=Value ...] [-R owner/repo]
#   set-board-fields.sh 2009 Status="To Do" Priority=Medium Risk=Low
# Prints the fields as read back from the board. Exits non-zero on any failure.
#
# Why not `gh project item-edit --url`: on a board this size each call looks the item up
# again and is expensive. A batch of tickets trips GitHub's per-minute limit. This script
# makes four cheap calls per ticket: add (returns the item id), one field lookup, one
# mutation with every field, one read-back. Works on bash 3.2.
set -euo pipefail

repo=yalesites-org/YaleSites-Internal
num=""
pairs=()
while [[ $# -gt 0 ]]; do
  case $1 in
    -R) repo=$2; shift 2 ;;
    *=*) pairs+=("$1"); shift ;;
    *) num=$1; shift ;;
  esac
done
[[ -n $num && ${#pairs[@]} -gt 0 ]] || { echo "usage: set-board-fields.sh <issue> Field=Value ... [-R owner/repo]" >&2; exit 2; }

project=$(gh api graphql -f query='{organization(login:"yalesites-org"){projectV2(number:6){id}}}' \
  --jq .data.organization.projectV2.id)
node=$(gh api "repos/$repo/issues/$num" --jq .node_id)

# Adding an item that's already on the board returns the existing item, so this is safe to repeat.
item=$(gh api graphql -f query="mutation{addProjectV2ItemById(input:{projectId:\"$project\",contentId:\"$node\"}){item{id}}}" \
  --jq .data.addProjectV2ItemById.item.id)

fields=$(gh api graphql -f query="query{node(id:\"$project\"){... on ProjectV2{fields(first:50){nodes{... on ProjectV2SingleSelectField{id name options{id name}}}}}}}" \
  --jq '[.data.node.fields.nodes[] | select(.name)]')

body=""
i=0
for pair in "${pairs[@]}"; do
  f=${pair%%=*}; v=${pair#*=}
  fid=$(jq -r --arg f "$f" '.[] | select(.name==$f) | .id' <<<"$fields")
  oid=$(jq -r --arg f "$f" --arg v "$v" '.[] | select(.name==$f) | .options[] | select(.name==$v) | .id' <<<"$fields")
  [[ -n $fid ]] || { echo "no single-select field named \"$f\" on the board" >&2; exit 1; }
  [[ -n $oid ]] || { echo "\"$v\" is not an option of $f (check capitalization)" >&2; exit 1; }
  body+="f$i: updateProjectV2ItemFieldValue(input:{projectId:\"$project\",itemId:\"$item\",fieldId:\"$fid\",value:{singleSelectOptionId:\"$oid\"}}){projectV2Item{id}} "
  i=$((i+1))
done
gh api graphql -f query="mutation{ $body }" --silent

# Read back every field we wrote.
gh api graphql -f query="query{node(id:\"$item\"){... on ProjectV2Item{fieldValues(first:30){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}}}}}}}" \
  --jq '[.data.node.fieldValues.nodes[] | select(.field) | "\(.field.name)=\(.name)"] | join(", ")'
