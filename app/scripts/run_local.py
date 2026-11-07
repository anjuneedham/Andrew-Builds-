#!/usr/bin/env python3
"""Run Outreach Desk on your own computer.   python scripts/run_local.py [--port 8080]
Settings come from .env.local (git-ignored): DATABASE_URL (a postgresql:// URL) and OWNER_SETUP_TOKEN (20+ characters, first-time setup only)."""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import envfile  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--env-file", default=str(ROOT / ".env.local"))
    a = ap.parse_args()
    envfile.load(a.env_file, os.environ)
    if not os.environ.get("DATABASE_URL", "").startswith(("postgres://", "postgresql://")):
        sys.exit("DATABASE_URL is missing. Copy .env.example to .env.local and paste a postgresql:// URL (a free Neon database works).")
    from dashboard import app
    print(f"Outreach Desk on http://127.0.0.1:{a.port}  (Ctrl+C to stop)")
    app.serve(port=a.port)


if __name__ == "__main__":
    main()
