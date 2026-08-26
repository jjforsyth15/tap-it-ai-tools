---
name: tapit-document
description: Records or updates TapIt project knowledge in the shared Obsidian vault -- decisions, current state, known issues, or reference notes. Use ONLY when explicitly asked to document, record, preserve, or update project knowledge -- never automatically after a task, review, or conversation.
disable-model-invocation: true
---

# TapIt Document

Manual-only: this skill runs only when invoked directly (`/tapit-document`) or explicitly requested. Claude does not trigger it automatically on its own judgment -- `disable-model-invocation` enforces that at the tool level, not just by instruction.

## Canonical policy

`tap-it-vault/AI Context/AI Agent Instructions.md` ("Vault Editing Policy") and `tap-it-vault/Home.md` ("Etiquette -- when to update what") define what belongs in the vault and how. Read them if not already in context; the steps below operationalize them, not replace them.

## Steps

1. Confirm there's something genuinely worth preserving (a decision, a state change, a known issue, a reusable lesson) -- not a routine conversation summary.
2. Search the vault for the most relevant existing note by topic before writing anything.
3. Prefer updating that note. Create a new note only for a genuinely new concept with no existing home.
4. Keep the edit concise and factual; use `[[wikilinks]]` to connect related notes.
5. Tag status explicitly: implemented / in progress / planned / deferred / experimental.
6. Verify any implementation claim against the current source before writing it down -- don't take the conversation's word for what code does.
7. Never write secrets, credentials, tokens, or `.env` contents into the vault.
8. Append rather than rewrite in `Decisions.md`; move fixed items into `Known-Issues.md`'s "Resolved" section with a date rather than deleting them, per the vault's own etiquette.
