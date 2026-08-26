# tap-it-ai-tools

Internal AI-powered developer tooling for the TapIt project. Reaches into
sibling checkouts of `tap-it-server` and `tap-it-web` rather than containing
application code itself — see the root `tap-it/CLAUDE.md` for how the repos
relate.

## `review contracts` — AI contract reviewer

Diffs FastAPI/Pydantic backend schemas (`tap-it-server/app/schemas/*.py`)
against hand-written TypeScript frontend types (`tap-it-web/src/types/*.ts`)
using the OpenAI API, and reports where they've drifted out of sync — missing
or extra fields, wrong types, incorrect nullability, mismatched
request/response shapes.

### Setup

Requires a `.env` file at the repo root:

- `TAP_IT_BACKEND_PATH` / `TAP_IT_FRONTEND_PATH` — relative paths to sibling
  checkouts (e.g. `../tap-it-server`, `../tap-it-web`).
- `OPENAI_API_KEY` — required to call the reviewer.

These paths are resolved relative to the current working directory at
runtime, not to the `.env` file's location — so run `tapit-ai` commands from
inside the `tap-it-ai-tools` directory itself.

### Usage
tapit-ai review contracts # review every discovered contract pair
tapit-ai review contracts --report # include full per-issue detail
tapit-ai review contracts --file user # review a single pair by filename stem (user.py <-> user.ts)
tapit-ai review contracts --fix # offer to generate and apply fixes for pairs with issues


Pairs are discovered by matching filename stem between the two directories
(`user.py` ↔ `user.ts`) — this is a naming-convention pairing, not an
explicit mapping, so a schema and type file must share a name to be compared.

### Severity

- **error** — the frontend may mishandle real backend data: missing response
  fields, nullability mismatches, incorrect response mappings.
- **warning** — a frontend request type is narrower than what the backend
  accepts, but still valid.

### `--fix`

When a contract pair has issues, `--fix` generates a corrected version of the
frontend type file addressing all of that pair's issues at once, shows a diff
against the current file, and asks for confirmation before writing. Fixes
only ever rewrite the frontend `.ts` file — never the backend schema, since
the reviewer treats the backend as the source of truth. This is a manual,
interactive command: don't wire `--fix` into the pre-commit hook or CI, since
neither can answer a confirmation prompt and pipelines shouldn't silently
rewrite frontend types.

### Known limitations

- No automated test suite for this package yet.
- The CLI currently always exits `0`, even when error-severity issues are
  found across pairs — it isn't yet safe to use as a hard gate (e.g. in CI or
  a pre-commit hook) until that's fixed.

## `test journeys` — user journey testing agent

Runs a deterministic Playwright browser-automation suite against a live
TapIt frontend (no LLM involved, despite the package name) and reports which
user journeys still work.

### Setup

`playwright` is installed as part of `pip install -e .`, but the Chromium
browser binary is a separate one-time step:
playwright install chromium

Also requires these variables, in `.env` at the repo root or the process
environment — the testing agent loads `.env` itself, independently of the
contract reviewer's config:

- `TAPIT_BASE_URL` — base URL of the frontend to test against.
- `TAPIT_TEST_EMAIL` / `TAPIT_TEST_PASSWORD` — credentials for a test account
  used by the login scenario.

### Usage
tapit-ai test journeys # run every registered user journey

Launches a visible (headed) Chromium window. Exits `1` if any journey fails,
`0` if all pass.

### Known limitations

- Only one journey exists today (`test_login` in
  `tapit_ai/testing/scenarios.py`). Add more by writing an async function
  that returns a `TestResult` and adding it to the `SCENARIOS` list in that
  file.
- Always runs headed; there's no `--headless` option yet.
- `test_login` writes a debug screenshot to a hardcoded `login_debug.png` at
  the repo root on every run, not only on failure.