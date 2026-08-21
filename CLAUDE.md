# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


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
2. **User journey testing agent** (`tapit_ai/testing/`) — a deterministic Playwright browser-automation harness (no LLM involved despite the repo name). It is early-stage and **not yet wired into the CLI or packaging**: `playwright` is not declared in `pyproject.toml`/`requirements.txt`, and there is no `tapit-ai test` command.

## Setup & commands

Requires a `.env` file at the repo root with:
- `TAP_IT_BACKEND_PATH` / `TAP_IT_FRONTEND_PATH` — paths to sibling checkouts of the TapIt backend and frontend repos (e.g. `../tap-it-server`, `../tap-it-web`). Required; `config.py` raises `ValueError` at import time if either is unset.
- `OPENAI_API_KEY` — required by the contract reviewer.
- `TAPIT_BASE_URL`, `TAPIT_TEST_EMAIL`, `TAPIT_TEST_PASSWORD` — required by the testing agent's login scenario (read via bare `os.environ[...]`, so a missing var raises `KeyError` rather than a friendly message).

Only `config.py` (used by the contract reviewer) calls `load_dotenv()`. The testing agent (`tapit_ai/testing/`) never imports `config.py` and never loads `.env` itself, so the three `TAPIT_*` vars must actually be set in the process environment — putting them in `.env` alone has no effect for the testing agent.

Install and run:
```
pip install -e .
tapit-ai review contracts              # review all discovered backend/frontend contract pairs
tapit-ai review contracts --report     # include full per-issue detail in output
tapit-ai review contracts --file NAME  # review a single pair by schema/type filename stem
```

There is no test suite, linter, or formatter configured in this repo (no pytest/ruff/mypy config, no `tests/` directory) — don't assume `pytest`/`ruff` commands exist here.

The testing agent has no CLI entry point yet; it can only be run directly, e.g.:
```
python -c "from tapit_ai.testing.agent import run; run()"
```
This also requires `playwright` to be installed manually (`pip install playwright && playwright install chromium`) since it isn't declared as a project dependency.

## Architecture

**Contract reviewer flow** (`tapit_ai/cli.py` → `utils/discovery.py` → `reviewers/contract_reviewer.py` → `models/contract.py`):
- `discover_contract_pairs()` pairs up `*.py` files in `BACKEND_SCHEMA_DIR` with `*.ts` files in `FRONTEND_TYPES_DIR` by matching filename stem (e.g. `user.py` ↔ `user.ts`). This is a naming-convention pairing, not an explicit mapping file.
- `review_contract()` sends both files' raw source as text to an OpenAI model via `client.responses.parse(...)` with `text_format=ContractReview`, using structured-output parsing rather than manual JSON parsing. The compatibility rules and severity rubric (what counts as an "error" vs a "warning") are encoded entirely in the prompt string in `contract_reviewer.py`, not in code — check there first when the reviewer's judgment seems off.
- Errors vs. warnings drive the CLI's exit behavior in `cli.py`: any `error`-severity issue is treated as a review failure.

**Testing agent flow** (`tapit_ai/testing/`): `agent.py` (entry point, prints results) → `scenarios.py` (defines journeys as plain async functions, e.g. `test_login()`) → `browser.py` (`TapItBrowser`, a thin Playwright async-API wrapper: headed Chromium, 5s default timeout) → `models.py` (`TestResult`/`TestStatus` pydantic result shape). Scenarios use Playwright's semantic locators (`get_by_label`, `get_by_role`) rather than CSS selectors, never raise (failures are caught and returned as a `FAILED` `TestResult`), and always call `browser.stop()` in a `finally` block. New journeys should follow the `test_login()` pattern: one async function per scenario in `scenarios.py`, returning a `TestResult`.

Note: `test-results/.last-run.json` and the root-level `login_debug.png` are artifacts from ad hoc runs, not something the current code manages as a results directory — `login_debug.png` is a single hardcoded debug screenshot path written by `test_login()`, not a per-run/timestamped report.
