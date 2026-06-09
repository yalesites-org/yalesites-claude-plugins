---
name: commit-conventional
description: Create commits following Conventional Commits using Angular standard. ALWAYS use this skill when user asks to "make a commit", "create a commit", "make a conventional commit", "do a commit", or any similar commit request - never use Bash directly for commits.
allowed-tools:
  - Bash(git *)
  - Bash(lando composer code-sniff)
  - Bash(lando composer code-fix)
  - Bash(npm run lint*)
  - Bash(npx eslint *)
  - Bash(npx stylelint *)
---

# Conventional Commits

Create commits following Conventional Commits using Angular standard as defined in CLAUDE.md.

## Format
```
type(scope): brief summary

Detailed explanation of the change, including:
- Why the change was made
- What problem it solves
- Any important context or decisions
- References to relevant documentation or discussions
```

## Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

## Usage Examples
```bash
# Feature commit
git commit -m "feat(123): add user authentication module

Since we need CAS authentication, we decided to try this authentication
module to assist in logins."

# Bug fix commit
git commit -m "fix(124): resolve form validation error

The contact form was not properly validating email addresses with plus signs.
Updated the validation regex to include RFC-compliant email formats."

# Documentation commit
git commit -m "docs(125): update installation instructions

Added missing step for configuring local database settings and clarified
the Lando setup process for new developers."
```

## Standards
- **Scope**: Usually the GitHub issue number (###)
- **Message**: Present tense, lowercase
- **Always do more than the minimum**: Include detailed explanatory body text when it adds value
- Make small, atomic commits to track progress and enable easy reverting
- NEVER reference Claude in any commits

## Important Notes for YaleSites Projects
- **Before creating any commit**, always run `lando composer code-sniff` to check for code style issues
- Fix any issues found by the code sniffer before proceeding with the commit
- If auto-fix is available, use `lando composer code-fix` to automatically resolve formatting issues
