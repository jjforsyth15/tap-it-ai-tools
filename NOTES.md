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

## Manual verification: `tapit-ai test init`

Verified in this session: `py_compile`, a full stub-based smoke test of all
three `cli.py` branches (both up / neither up / exactly-one-up x each of the
3 choices), and a real functional test of `dev_servers.run_dev_environment`
substituting two `python3 -m http.server` processes for uvicorn/npm on this
(Linux) sandbox -- confirmed it correctly detects not-running, starts both,
streams prefixed output, detects readiness, handles Ctrl+C (SIGINT) cleanly,
and both processes are confirmed stopped afterward.

NOT verified (needs your machine): the real `uvicorn`/`npm run dev` commands
specifically, and the Windows `taskkill /F /T` shutdown path (this sandbox
is Linux, so only the `terminate()`/`kill()` branch ran). Confirm for real:

1. Close any already-running backend/frontend. `tapit-ai test init` --
   confirm it starts both, streams recognizable uvicorn/vite startup logs
   prefixed `[backend]`/`[frontend]`, and prints "Environment ready" once
   both are up.
2. Ctrl+C -- confirm both actually stop (check e.g. `http://127.0.0.1:8000`
   and `http://localhost:5173` are no longer reachable, and no leftover
   `uvicorn`/`node` process for them in Task Manager).
3. Start just the frontend manually (`npm run dev`), then `tapit-ai test
   init` -- confirm it reports "frontend is already running; backend is
   not" and offers the 3 choices; try each one.
4. While frontend is running manually, choose "restart both" -- confirm it
   prompts you to stop the frontend yourself, keeps re-prompting if you hit
   Enter without actually stopping it, and only proceeds to start both once
   it's actually down.
5. Confirm `TAPIT_BASE_URL` in `.env` (if pointed at a deployed URL) does
   NOT affect `test init`'s "is the frontend up" detection -- only
   `TAPIT_FRONTEND_URL`/the `localhost:5173` default should.

## Found while testing `tapit-ai test init` for real: tap-it-server env-load ordering bug

Real run on Windows: backend subprocess crashed with `ValueError:
DATABASE_URL_DIRECT environment variable is not set` even though frontend
started fine. Root cause is in `tap-it-server/app/main.py`, not
tap-it-ai-tools: `load_dotenv()` is called after `from app.routes import
beta, cards, profile_images`, and that import chain reaches
`app.database`, which needs `DATABASE_URL_DIRECT` at import time --
before .env has been loaded. Works when Joe runs uvicorn manually only
because that variable is already present in his shell some other way;
tapit-ai launching it as a subprocess doesn't have that.

Fixed defensively on the tapit-ai side: `dev_servers.py` now merges
tap-it-server/.env into the backend subprocess's own environment itself
(`_subprocess_env()`), independent of whatever main.py does internally.
Verified with a stand-in script that only succeeds if the env var is
present, run with DATABASE_URL_DIRECT deliberately absent from the
launching process's own environment.

Not fixed (different repo, needs Joe's go-ahead, tap-it-server has its own
stricter modification policy): the actual ordering bug in
tap-it-server/app/main.py. The real fix there is moving `import os` /
`from dotenv import load_dotenv` / `load_dotenv()` to the very top of the
file, before any `app.*` imports.