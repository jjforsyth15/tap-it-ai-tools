---
name: tapit-context
description: Orients on TapIt project context before substantial work -- current state, architecture, known issues, and history from the shared Obsidian vault, cross-checked against live source. Use before non-trivial TapIt work: architecture, feature implementation, debugging, refactors, code review, or testing strategy across tap-it-server, tap-it-web, tap-it-ai-tools, tap-it-client, or tap-it-vault. Skip for trivial or narrowly-scoped questions.
disallowed-tools: Write, Edit, NotebookEdit
---

# TapIt Context

Read-only orientation. Ground yourself before non-trivial TapIt work -- do not write, edit, or otherwise modify anything (source, config, or vault) as part of this skill.

## Canonical policy

`tap-it-vault/AI Context/AI Agent Instructions.md` is the canonical policy for this workflow, the source-of-truth hierarchy, and the source-editing rules. If it isn't already in context this session, read it first -- the steps below are its operational summary, not a replacement for it.

## Steps

1. Read `tap-it-vault/Home.md` for the vault's current index, then retrieve whichever notes it currently points to for project state and priorities (today that's `Current-State.md`; a dedicated "TapIt Overview" / "Current Priorities" note may not exist yet). Don't assume a fixed filename -- `Home.md`'s index is the source of truth for what currently exists, and it changes over time.
2. Identify the task's topic (which repo(s), which feature/area) and search the vault by that topic rather than a fixed path: check `Known-Issues.md`, then search `Reference/` and `Repos/` for matching keywords. Retrieve only the notes that actually match -- don't dump the whole vault into context.
3. Inspect the current source/config for the repo(s) involved -- start with that repo's own `AGENTS.md`, then the actual code.
4. Where the vault and the source disagree, trust the source. Vault notes, especially anything under `Reference/`, are documentation snapshots, not the current implementation.
5. Summarize what you found back into the conversation in a few sentences -- enough to proceed with the task, not a transcript of every file read.

Not required for trivial or narrowly-scoped questions -- use judgment.
