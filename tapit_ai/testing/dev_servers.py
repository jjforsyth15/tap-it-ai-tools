"""Starts/monitors the local tap-it-server + tap-it-web dev processes so the
journey testing agent has something to run against. See ``tapit_ai.cli``'s
``test init`` command for the interactive decision-making this is built for.
"""

import os
import platform
import shutil
import subprocess
import threading
import time
from pathlib import Path
import urllib.error
import urllib.request

from dotenv import dotenv_values, load_dotenv

load_dotenv()

# Deliberately separate from TAPIT_BASE_URL (used by the journey scenarios,
# which may point at a deployed environment) -- these two always mean the
# local dev servers this command starts/checks. Overridable if your local
# ports differ from tap-it-server's CURRENT_URL / Vite's default dev port.
BACKEND_URL = os.getenv("TAPIT_BACKEND_URL", "http://127.0.0.1:8000")
FRONTEND_URL = os.getenv("TAPIT_FRONTEND_URL", "http://localhost:5173")

BACKEND_COMMAND = ["uvicorn", "app.main:app", "--reload"]
FRONTEND_COMMAND = ["npm", "run", "dev"]

READY_TIMEOUT_SECONDS = 30
POLL_INTERVAL_SECONDS = 1.0


def is_reachable(url: str, timeout: float = 1.5) -> bool:
    """True if something answers at ``url`` -- any HTTP response counts,
    not just a 2xx, since we only care whether a server is listening."""
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except urllib.error.HTTPError:
        return True
    except (urllib.error.URLError, OSError):
        return False


def is_backend_up() -> bool:
    return is_reachable(BACKEND_URL)


def is_frontend_up() -> bool:
    return is_reachable(FRONTEND_URL)


def _resolve_command(command: list[str]) -> list[str]:
    """Look up the command's full path via PATH (handles npm's .cmd wrapper
    on Windows, which subprocess.Popen won't find on its own)."""
    resolved = shutil.which(command[0])

    if resolved is None:
        raise RuntimeError(
            f"'{command[0]}' was not found on PATH. Run this from the same "
            f"shell/environment you'd normally use to start it manually."
        )

    return [resolved, *command[1:]]


def _subprocess_env(app_root: Path) -> dict[str, str]:
    """The current process env with app_root/.env merged on top. We read the
    child app's own .env ourselves rather than relying on it to load its own
    -- tap-it-server's main.py currently calls load_dotenv() after several
    imports that already need env vars it sets, so waiting on it isn't
    reliable when we're the one launching the process."""
    return {**os.environ, **dotenv_values(app_root / ".env")}


def _stream_output(process: "subprocess.Popen[str]", label: str) -> None:
    if process.stdout is None:
        return

    for line in process.stdout:
        print(f"[{label}] {line.rstrip()}")


def _start_process(command: list[str], cwd: Path, label: str, env: dict[str, str] | None = None) -> "subprocess.Popen[str]":
    resolved = _resolve_command(command)
    print(f"Starting {label}: {' '.join(command)}  (in {cwd})")

    process = subprocess.Popen(
        resolved,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )

    thread = threading.Thread(target=_stream_output, args=(process, label), daemon=True)
    thread.start()

    return process


def _stop_process(process: "subprocess.Popen[str]", label: str) -> None:
    if process.poll() is not None:
        return

    print(f"Stopping {label}...")

    if platform.system() == "Windows":
        # npm/uvicorn --reload spawn their own child processes on Windows;
        # terminate() alone only kills the wrapper, not the tree.
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def _wait_until_ready(url: str, label: str) -> bool:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        if is_reachable(url):
            return True

        time.sleep(POLL_INTERVAL_SECONDS)

    return False


def wait_for_manual_stop(url: str, label: str) -> None:
    """Blocks, re-checking ``url``, until whatever's running there is
    actually stopped -- used for the "restart both" path so we don't try to
    bind a port that's still in use."""
    while is_reachable(url):
        input(
            f"Still detecting the {label} running. Stop it (Ctrl+C in its "
            f"terminal), then press Enter to check again..."
        )


def run_dev_environment(backend_root: Path, frontend_root: Path, start_backend: bool, start_frontend: bool) -> None:
    """Starts whichever of backend/frontend is requested, waits for both to
    be reachable (the other one is assumed already up if not requested here),
    then blocks -- streaming their output -- until Ctrl+C, at which point it
    stops only the process(es) it started."""
    processes: list[tuple[str, "subprocess.Popen[str]"]] = []

    try:
        if start_backend:
            processes.append(("backend", _start_process(BACKEND_COMMAND, backend_root, "backend", env=_subprocess_env(backend_root))))

        if start_frontend:
            processes.append(("frontend", _start_process(FRONTEND_COMMAND, frontend_root, "frontend")))

        if start_backend and not _wait_until_ready(BACKEND_URL, "backend"):
            print(f"Backend did not respond at {BACKEND_URL} within {READY_TIMEOUT_SECONDS}s.")
            return

        if start_frontend and not _wait_until_ready(FRONTEND_URL, "frontend"):
            print(f"Frontend did not respond at {FRONTEND_URL} within {READY_TIMEOUT_SECONDS}s.")
            return

        print("\nEnvironment ready. In another terminal, run `tapit-ai test journeys`.")
        print("Press Ctrl+C here to stop what this command started.\n")

        while True:
            time.sleep(1)

            for label, process in processes:
                exit_code = process.poll()

                if exit_code is not None:
                    print(f"\n{label} exited unexpectedly (code {exit_code}).")
                    return

    except KeyboardInterrupt:
        print("\nStopping...")

    except RuntimeError as e:
        print(f"Could not start the environment: {e}")

    finally:
        for label, process in processes:
            _stop_process(process, label)
