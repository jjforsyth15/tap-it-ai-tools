# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.


## Code Modification Policy

Do not modify, create, delete, move, or rename files unless I explicitly
give permission to make the change.

By default, operate in an advisory capacity.

You may:
- inspect and search the repository
- read source code
- trace dependencies and application flows
- inspect Git history and diffs
- explain existing implementations
- propose changes
- provide code examples
- recommend tests
- identify bugs and technical debt

Before modifying code:
1. Explain what you propose changing.
2. Identify the files that would be affected.
3. Explain why the change is necessary.
4. Wait for my explicit approval to implement it.

Do not interpret discussion of a possible change as permission to implement it.

## What this is

`tap-it-ai-tools` is an internal AI-powered developer tooling package for the TapIt project. It is a standalone Python package (installed as the `tapit-ai` CLI) that reaches *out* into sibling checkouts of the TapIt backend and frontend repos rather than containing application code itself. Two features exist today, at very different levels of maturity:

1. **Contract reviewer** (`tapit_ai/reviewers/`) — wired into the CLI, uses the OpenAI API to diff FastAPI/Pydantic backend schemas against TypeScript frontend types and report mismatches.
2. **User journey testing agent** (`tapit_ai/testing/`) — a deterministic Playwright browser-automation harness (no LLM involved despite the repo name), wired into the CLI as `tapit-ai test init` (starts/checks the local backend+frontend dev servers) and `tapit-ai test journeys` (runs the journeys). Still early-stage: only one journey (`test_login`) exists so far.

## Setup & commands

Requires a `.env` file at the repo root with:
- `TAP_IT_BACKEND_PATH` / `TAP_IT_FRONTEND_PATH` — paths to sibling checkouts of the TapIt backend and frontend repos (e.g. `../tap-it-server`, `../tap-it-web`). Required; `config.py` raises `ValueError` at import time if either is unset.
- `OPENAI_API_KEY` — required by the contract reviewer.
- `TAPIT_BASE_URL`, `TAPIT_TEST_EMAIL`, `TAPIT_TEST_PASSWORD` — required by `test journeys`' login scenario. Validated together via the shared `require_env()` helper, which reports every missing variable in one clear message. Note `TAPIT_BASE_URL` is whatever frontend journeys should exercise (may be a deployed URL, not necessarily local).
- `TAPIT_BACKEND_URL` / `TAPIT_FRONTEND_URL` (optional) — used only by `test init` to check/wait for the *local* dev servers; default to `http://127.0.0.1:8000` / `http://localhost:5173` if unset. Deliberately separate from `TAPIT_BASE_URL` above so pointing journeys at a deployed environment doesn't confuse `test init`'s local-server detection.

`tapit_ai/utils/environment.py` loads `.env` and provides shared validation for both CLI features. Each command validates only its own required variables, so importing the CLI or running `--help` does not require either feature to be configured. All variables can live in `.env` at the repo root.

Install and run:
```
pip install -e .
playwright install chromium            # one-time browser install for the testing agent
tapit-ai review contracts              # review all discovered backend/frontend contract pairs
tapit-ai review contracts --report     # include full per-issue detail in output
tapit-ai review contracts --file NAME  # review a single pair by schema/type filename stem
tapit-ai test init                     # start/check the local backend + frontend dev servers
tapit-ai test journeys                 # run all registered user journey tests (Playwright)
```

There is no test suite, linter, or formatter configured in this repo (no pytest/ruff/mypy config, no `tests/` directory) — don't assume `pytest`/`ruff` commands exist here.

`playwright` is now a declared dependency (`pip install -e .` pulls in the Python package), but the Chromium browser binary is a separate one-time step: `playwright install chromium`.

## Architecture

**Contract reviewer flow** (`tapit_ai/cli.py` → `utils/discovery.py` → `reviewers/contract_reviewer.py` → `models/contract.py`):
- `discover_contract_pairs()` pairs up `*.py` files in `BACKEND_SCHEMA_DIR` with `*.ts` files in `FRONTEND_TYPES_DIR` by matching filename stem (e.g. `user.py` ↔ `user.ts`). This is a naming-convention pairing, not an explicit mapping file.
- `review_contract()` sends both files' raw source as text to an OpenAI model via `client.responses.parse(...)` with `text_format=ContractReview`, using structured-output parsing rather than manual JSON parsing. The compatibility rules and severity rubric (what counts as an "error" vs a "warning") are encoded entirely in the prompt string in `contract_reviewer.py`, not in code — check there first when the reviewer's judgment seems off.
- Errors vs. warnings drive the CLI's exit behavior in `cli.py`: any `error`-severity issue is treated as a review failure.

**Testing agent flow** (`tapit_ai/cli.py` → `testing/agent.py` → `testing/scenarios.py` → `testing/browser.py` / `testing/models.py`): `cli.py`'s `tapit-ai test journeys` command calls `agent.run()`, which runs every function listed in `scenarios.py`'s `SCENARIOS` registry (currently just `test_login`), printing and collecting a `TestResult` per scenario. `browser.py` (`TapItBrowser`) is a thin Playwright async-API wrapper: headed Chromium, 5s default timeout. `models.py` defines the `TestResult`/`TestStatus` pydantic result shape. Scenarios use Playwright's semantic locators (`get_by_label`, `get_by_role`) rather than CSS selectors, never raise (failures — including a missing `TAPIT_*` env var — are caught and returned as a `FAILED` `TestResult`), and always call `browser.stop()` in a `finally` block. New journeys should follow the `test_login()` pattern: one async function per scenario in `scenarios.py`, returning a `TestResult`, added to the `SCENARIOS` list. `cli.py` exits `1` if any journey fails, `0` if all pass.

**Dev environment flow** (`tapit_ai/cli.py`'s `test init` → `testing/dev_servers.py`): checks `is_backend_up()`/`is_frontend_up()` (plain HTTP reachability against `TAPIT_BACKEND_URL`/`TAPIT_FRONTEND_URL`) before doing anything. Both up → no-op. Neither up → `run_dev_environment()` launches `uvicorn app.main:app --reload` in `BACKEND_ROOT` and `npm run dev` in `FRONTEND_ROOT` (both from `config.py`, resolved lazily inside `test_init` after `_require_command_env` confirms `TAP_IT_BACKEND_PATH`/`TAP_IT_FRONTEND_PATH` are set) as `subprocess.Popen` processes, streams their output prefixed `[backend]`/`[frontend]` via daemon threads, polls both URLs until reachable, then blocks until Ctrl+C. On Windows, shutdown uses `taskkill /F /T` rather than `Popen.terminate()`, since `npm run dev`/`uvicorn --reload` spawn child processes that a plain terminate wouldn't reach. Exactly one already up → `cli.py` offers a 3-way choice (start the missing one only / stop-and-restart both, pausing on `wait_for_manual_stop()` until the user has actually stopped the running one / cancel) rather than `dev_servers.py` ever killing a process it didn't start itself.

Note: `test-results/.last-run.json` and the root-level `login_debug.png` are artifacts from ad hoc runs, not something the current code manages as a results directory — `login_debug.png` is a single hardcoded debug screenshot path written by `test_login()`, not a per-run/timestamped report.
