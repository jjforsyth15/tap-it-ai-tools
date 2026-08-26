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


## Manual verification: `tapit-ai test journeys`

Not yet run end-to-end against a live frontend as of this change (the
sandbox this was wired up in had no network access to install `playwright`
and no real TapIt frontend to point at) — only verified statically
(`py_compile` + an import/wiring smoke test with stubbed-out dependencies).
Confirm for real:

1. `pip install -e .` then `playwright install chromium`.
2. Set `TAPIT_BASE_URL`, `TAPIT_TEST_EMAIL`, `TAPIT_TEST_PASSWORD` in `.env`
   (or the environment) for a real test account against a running frontend.
3. `tapit-ai test journeys` — confirm a headed Chromium window opens,
   navigates to `/login`, logs in, and reports `PASSED` with exit code `0`
   (`echo $?` on macOS/Linux, `echo $LASTEXITCODE` in PowerShell).
4. Temporarily unset one of the three `TAPIT_*` vars and re-run — confirm
   you get a clean `FAILED` result with the `"... is not set"` message
   (not a raw `KeyError` traceback), and exit code `1`.
5. Temporarily break the login flow (e.g. wrong password in `.env`) and
   re-run — confirm it still reports `FAILED` cleanly with exit code `1`
   rather than crashing.