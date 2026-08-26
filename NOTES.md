# Notes

## Manual verification: `--fix` flag on `tapit-ai review contracts`

1. Pick a real contract pair (e.g. one with a `tap-it-web/src/types/*.ts` counterpart in `FRONTEND_TYPES_DIR`).
2. Temporarily introduce a small deliberate mismatch in the frontend `.ts` file (rename a field, flip a type, drop an optional field).
3. `tapit-ai review contracts --file <name>` (no `--fix`) — confirm the issue is still detected/reported as before.
4. `tapit-ai review contracts --file <name> --fix` — confirm: "Generating fix..." prints, a unified diff prints with correct `(current)`/`(fixed)` headers, and the `Apply this fix to <file>? [y/N]` prompt appears.
5. Decline — confirm "Fix not applied." and the file on disk is untouched (`git diff` still shows only the manually introduced change).
6. Re-run with `--fix`, accept — confirm "Applied fix to <file>." and `git diff` shows the fix written.
7. Re-run `tapit-ai review contracts --file <name>` (no `--fix`) — confirm zero issues now, proving the fix actually resolves the mismatch.
8. `git checkout` the frontend file afterward to restore it cleanly (AI output may not byte-match the original even if semantically equivalent).
