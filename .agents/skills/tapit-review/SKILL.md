---
name: tapit-review
description: Performs a consistent review of TapIt code changes -- correctness, regressions, security, API/type contract consistency, maintainability, and testing gaps. Use when asked to review a diff, a PR, changes, or recently written TapIt code. Reports findings only; does not modify code unless fixes are explicitly requested.
disallowed-tools: Write, Edit, NotebookEdit
---

# TapIt Review

Report-only by default: findings, not fixes. This skill's tool restriction covers the turn it runs in -- if you separately, explicitly ask for the fix afterward, that's a normal follow-up request, not this skill overriding its own policy.

## Ground yourself first

Get enough context to judge the change correctly before reviewing it. These are the same lightweight principles `tapit-context` uses, inlined here rather than invoked, since Codex skills don't compose by calling one another:

- Check `tap-it-vault/Home.md` -> `Current-State.md` for current project state.
- Search the vault by topic (`Known-Issues.md`, relevant `Reference/*`, `Repos/*`) for anything already known about the area being changed -- known bugs, established contract drift, deferred-by-design items.
- Trust current source over vault notes where they disagree.

## Steps

1. Determine what changed (`git diff` / `git status` / the files in question) and the intended behavior.
2. Ground yourself per above.
3. Inspect the actual changed code, not just the diff in isolation -- check callers/callees where it matters.
4. Check for: correctness, regressions, security (auth, admin routes, cross-user data access, input validation, secrets), API/type contract consistency between `tap-it-server` and `tap-it-web`, maintainability, and testing gaps -- there's no automated suite yet, so also check whether `docs/TESTING.md` needs a matching update.
5. If backend Pydantic schemas or frontend TS types are among the changed files, also run `tapit-ai review contracts` (from `tap-it-ai-tools/`, requires its own `.env` -- see that repo's `AGENTS.md`) instead of re-deriving contract diffs by hand.
6. Prioritize concrete, verified findings over stylistic nits.
7. Report findings. Do not modify source code -- including in `tap-it-ai-tools`, which has its own stricter advisory-only policy -- unless the user explicitly asks for the fix.
