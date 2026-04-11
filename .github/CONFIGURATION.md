# GitHub Configuration For BriefBiz

This directory contains the repository-level collaboration, review, and automation files that power the BriefBiz GitHub workflow.

It is separate from the application code so the repo can keep issue templates, pull request guidance, ownership rules, and CI definitions in one predictable place.

## What Lives Here

### `workflows/`

GitHub Actions workflow definitions used to validate and maintain the repository.

Current workflow coverage includes:

- backend quality checks
- frontend build validation
- pull request and push event automation

The main workflow file is:

- [`.github/workflows/ci.yml`](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\.github\workflows\ci.yml)

That workflow is responsible for:

- installing backend dependencies
- running backend lint checks with Ruff
- compiling backend modules to catch import and syntax errors
- running the backend pytest suite
- installing frontend dependencies
- building the frontend production bundle

## Issue Templates

The [`ISSUE_TEMPLATE`](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\.github\ISSUE_TEMPLATE) folder provides structured templates for new GitHub issues.

These templates help contributors open cleaner issues with enough context for triage.

Included templates:

- [bug_report.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\.github\ISSUE_TEMPLATE\bug_report.md)
- [feature_request.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\.github\ISSUE_TEMPLATE\feature_request.md)

Use them to standardize:

- reproduction steps
- expected versus actual behavior
- environment details
- requested product or engineering improvements

## Pull Request Template

The repository also includes a default pull request template:

- [pull_request_template.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\.github\pull_request_template.md)

This helps contributors consistently describe:

- what changed
- why it changed
- how it was tested
- any follow-up work or rollout considerations

## Code Ownership

Review ownership is defined in:

- [CODEOWNERS](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\.github\CODEOWNERS)

This file allows GitHub to automatically request review from the right people when files in certain paths are modified.

## How This Fits Into The Repo

The `.github/` directory is operational metadata for the repository. It does not contain application runtime code, but it affects how the team collaborates and how GitHub validates incoming changes.

In practice, this directory supports:

- repository hygiene
- contributor onboarding
- consistent code review
- automated validation before merges
- clearer bug and feature intake

## Related Top-Level Project Docs

If you are looking for application setup instead of repo automation, use these files instead:

- [README.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\README.md) for the full project overview
- [CONTRIBUTING.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\CONTRIBUTING.md) for contribution guidelines
- [SECURITY.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\SECURITY.md) for vulnerability reporting
- [AGENTS.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\AGENTS.md) for repository workflow guidance

## When To Update Files In `.github/`

You should usually update this directory when:

- CI requirements change
- new test or lint steps are added
- branch or PR policies are updated
- reviewer ownership changes
- issue or PR templates need more context
- the project onboarding flow changes

## Quick Maintenance Notes

- Keep workflow names stable when possible so required GitHub checks do not break unexpectedly.
- Prefer small, targeted CI changes and verify them in a branch before updating default branch protections.
- Keep issue and PR templates concise enough that contributors will actually use them.
- Update `CODEOWNERS` whenever team ownership changes or major folders are reorganized.

## Summary

This folder is the GitHub operations layer of BriefBiz. It defines how the repository is checked, how contributions are structured, and how reviews are routed, while the rest of the repo contains the product and platform code itself.
