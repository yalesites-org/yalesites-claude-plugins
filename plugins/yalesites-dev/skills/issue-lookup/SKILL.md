---
name: issue-lookup
description: Look up a GitHub issue from yalesites-org/YaleSites-Internal to read and understand its context, requirements, and current state. Use when starting a session to orient yourself on a ticket, when you want to understand what an issue is asking before deciding what to do next, or when you need to read the issue to add context or edit it. For full implementation planning with codebase exploration, use the issue-plan skill instead.
argument-hint: [issue-number] [optional: org/repo]
---

# GitHub Issue Lookup

Fetch and analyze a GitHub issue to understand its requirements and context.

## Usage

Look up an issue from the default repository:
```
/issue-lookup 123
```

Look up an issue from a different repository:
```
/issue-lookup 456 yalesites-org/yalesites-project
```

## Task

Retrieve and analyze GitHub issue $ARGUMENTS[0] from ${ARGUMENTS[1]:-yalesites-org/YaleSites-Internal}.

Execute the following steps:

1. Fetch the issue details using the GitHub CLI:
   ```bash
   gh issue view $ARGUMENTS[0] --repo ${ARGUMENTS[1]:-yalesites-org/YaleSites-Internal}
   ```

2. Analyze and summarize the issue, including:
   - Issue title and number
   - Current status (open/closed)
   - Description and requirements
   - Any acceptance criteria or implementation notes
   - Labels and assignees
   - Related comments that provide important context

3. Provide a clear summary of what needs to be done, highlighting:
   - The core problem or feature request
   - Any specific implementation requirements
   - Technical constraints or considerations mentioned
   - Dependencies on other issues (if referenced)

The issue details are now available in context for you to proceed with the related work.
