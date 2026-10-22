"""App settings, read from the environment and .env files (see .env.example in the repo root)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Real environment variables (e.g. from systemd) take precedence over both files.
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR.parent / ".env")  # repo root .env (local development)
load_dotenv(BACKEND_DIR / ".env")  # backend/.env (the original server setup)

APP_VERSION = "0.1.0"
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env in the repo root and fill it in.")
