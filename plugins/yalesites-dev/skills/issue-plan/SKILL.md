---
name: issue-plan
description: Analyze a GitHub issue from YaleSites-Internal and produce a concrete implementation plan. Use when you are ready to start implementing a ticket — not just reading it. Explores the codebase, maps relevant files, and enters plan mode with specific file-level changes described. If you just want to understand a ticket without committing to an implementation approach, use issue-lookup instead.
argument-hint: "<issue-number>"
---

# GitHub Issue Implementation Planner

Your job is to produce an implementation plan for issue #$ARGUMENTS — but keep your own context clean by delegating all research to a subagent. All the codebase exploration and file reading happens in the agent; only the distilled summary comes back here.

## Step 0: Load YaleSites platform context

Invoke the **yalesites** skill (the YaleSites platform-knowledge plugin in this marketplace — install it if you haven't) to load platform context. Extract a concise architectural summary — repo layout, module and component structure, config export conventions, and any patterns relevant to the issue type. You will append this to the research agent prompt in Step 1. If that skill isn't available, derive an equivalent summary by briefly inspecting the repo layout instead.

## Step 1: Spawn a research agent

Use the Agent tool with `model: "opus"` and the following prompt (substitute the real issue number for $ARGUMENTS):

---
Research GitHub issue #$ARGUMENTS in yalesites-org/YaleSites-Internal and the local codebase.

1. Fetch the full issue including comments:
   `gh issue view $ARGUMENTS --repo yalesites-org/YaleSites-Internal --comments`

2. Analyze the issue:
   - Type (bug fix, feature, enhancement)
   - Explicit and implied acceptance criteria
   - Affected components, modules, or systems

3. Explore the codebase to find:
   - Relevant files and what role they play
   - Existing patterns and conventions in the affected area
   - Related functionality that might be impacted by this change

4. Return a structured summary with these sections:
   - **Issue** — title, type, full description, acceptance criteria
   - **Relevant files** — path + what each file does in this context
   - **Current implementation** — how the affected area works today
   - **Suggested approach** — concrete direction for the implementation
   - **Risks and unknowns** — anything that needs clarification or warrants care

Be thorough in file reading — partial understanding leads to bad plans. Do not create or modify any files.

**YaleSites platform context:** {Append the architectural summary from Step 0 here. This orients you on module structure, component hierarchy, config export conventions, and repo layout before you begin exploring.}
---

## Step 2: Enter plan mode

Once the agent returns its summary, use EnterPlanMode to present a concrete implementation plan covering:

- What needs to be done and why
- Files to create or modify (with specific changes described)
- Step-by-step implementation approach
- Testing strategy
- Risks or open questions

Apply YaleSites conventions throughout:
- PHP: Drupal + DrupalPractice standards, 2-space indentation
- Verify with `lando composer code-sniff` before any commit
- WCAG 2.1 AA compliance in all UI-facing changes
- Export config after any config changes (`npm run confex`)

## Cross-repo workflow

If the research agent determines the changes live in `component-library-twig` or `atomic`, read `references/cross-repo-workflow.md` and include those steps in the plan (multidev companion PR + Netlify deploy preview links).

## Next step

Once the plan is approved and implemented, use the **commit-conventional** skill for commits and the **yalesites-pr** skill to open the pull request(s).
