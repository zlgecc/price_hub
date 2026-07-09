"""Vercel serverless entrypoint for the FastAPI application."""

import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[1] / "server"
sys.path.insert(0, str(SERVER_ROOT))

from app.main import app  # noqa: F401
