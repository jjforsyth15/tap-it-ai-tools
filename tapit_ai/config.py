import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

backend_path = os.getenv("TAP_IT_BACKEND_PATH")
frontend_path = os.getenv("TAP_IT_FRONTEND_PATH")

BACKEND_ROOT = Path(backend_path)
FRONTEND_ROOT = Path(frontend_path)

BACKEND_SCHEMA_DIR = BACKEND_ROOT / "app" / "schemas"
FRONTEND_TYPES_DIR = FRONTEND_ROOT / "src" / "types"
