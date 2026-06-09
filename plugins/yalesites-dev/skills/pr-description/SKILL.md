---
name: pr-description
description: Generate a PR description by analyzing the current branch's commits, diffs, and file changes, then filling in a provided markdown template. Use when you need a PR body, want to summarize branch work for a pull request, or need to fill in a PR template.
disable-model-invocation: true
argument-hint: "<template>"
---

# Branch Summary

Analyze the current git branch changes and fill in a provided markdown template with intelligent summaries based on commits, diffs, and file changes.

## Usage

```
/pr-description <template>
```

Where `<template>` is your markdown template pasted inline after the command.

## Example

```
/pr-description ## [YSP-XXXX: Title](https://yaleits.atlassian.net/browse/YSP-XXXX)

### Description of work
- Placeholder

### Functional testing steps:
- [ ] Step 1
```

## Instructions

When this command is invoked:

1. **Extract branch information**:
   - Get current branch name
   - Parse ticket number from branch (e.g., `1167` from `1167-feature-name`)
   - Get base branch (usually `develop`)
   - If issue number is found, fetch issue details from GitHub:
     - Run `gh issue view <number> --repo yalesites-org/YaleSites-Internal --json title,url`
     - Use the fetched title instead of deriving from branch name
     - Use the fetched URL for the issue link

2. **Analyze changes**:
   - Run `git log develop..HEAD --oneline` to get commit messages
   - Run `git diff develop...HEAD --stat` for file statistics
   - Run `git diff develop...HEAD` to understand code changes
   - Identify patterns: new features, bug fixes, refactoring, configuration changes

3. **Fill in the template**:
   - **Preserve exact template structure** (headers, formatting, checkboxes)
   - Replace ticket placeholder (`YSP-XXXX`, `XX`, etc.) with actual ticket number from branch
   - Replace "Title" placeholder with:
     - If GitHub issue was found: Use the title from `gh issue view`
     - Otherwise: Use descriptive title derived from branch name
   - Replace issue link with:
     - If GitHub issue was found: Use the URL from `gh issue view`
     - Otherwise: Construct link based on template pattern
   - **Generate "Description of work" bullets** based on:
     - Commit messages (group related commits)
     - Types of changes (adds, fixes, updates, refactors)
     - File patterns (e.g., "Updates theme configuration", "Adds new component")
   - **Add "Closes" link** at the end of the description section:
     - If GitHub issue was found: Add blank line followed by `Closes <issue_url>`
     - This automatically links and closes the issue when PR is merged
   - **Leave testing steps as placeholders** or suggest based on functional changes
   - Keep all other sections intact

4. **Output format**:
   - Use `git rev-parse --show-toplevel` to find the git root
   - Delete any existing `CLAUDE_PR_DESCRIPTION.md` file first using `rm -f CLAUDE_PR_DESCRIPTION.md` (this avoids unnecessary Read operations)
   - Write the filled template to `CLAUDE_PR_DESCRIPTION.md` in the git root directory using the Write tool
   - Maintain all original template sections
   - Use bullet points matching the template style
   - Be concise but descriptive (2-5 word bullets preferred)
   - After writing the file, automatically copy it to clipboard with `pbcopy < CLAUDE_PR_DESCRIPTION.md`
   - Inform the user the markdown has been copied to their clipboard

5. **Important guidelines**:
   - Do NOT add new sections unless in template
   - Do NOT list individual files changed
   - Focus on WHAT changed functionally, not technical details
   - Use consistent verb forms (Adds, Fixes, Updates, Refactors)
   - Group related changes into single bullets

## Example Output

For a branch named `1167-reference-card-colors` where GitHub issue #1167 exists:

```markdown
## [1167: Reference Card Theme Slot Background Colors](https://github.com/yalesites-org/YaleSites-Internal/issues/1167)

### Description of work
- Adds theme color pass-through to reference card collection
- Updates card component to accept background color slots
- Fixes color inheritance in nested card layouts

Closes https://github.com/yalesites-org/YaleSites-Internal/issues/1167

### Functional testing steps:
- [ ] Verify reference cards display with correct theme colors
- [ ] Test color variations across different theme settings
- [ ] Check background color inheritance in collections
```
