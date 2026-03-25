#!/usr/bin/env python3
"""
RIO Protocol — Run All Services

Starts the RIO Audit Dashboard (which includes the Governance API,
Approval API, and Admin UI) on a single uvicorn process.

Usage:
    python scripts/run_all.py
    python scripts/run_all.py --host 0.0.0.0 --port 8050
    python scripts/run_all.py --reload   # development mode with auto-reload

Environment variables (override via .env or CLI flags):
    RIO_DASHBOARD_HOST  — bind address  (default: 0.0.0.0)
    RIO_DASHBOARD_PORT  — bind port     (default: 8050)
    RIO_LOG_LEVEL       — log level     (default: INFO)
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so imports resolve
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Load .env if present
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # python-dotenv is optional at startup

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log_level = os.environ.get("RIO_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("rio.run")


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def preflight() -> bool:
    """Verify that the system has been initialized."""
    checks = [
        (PROJECT_ROOT / "runtime" / "keys" / "private_key.pem", "Cryptographic keys"),
        (PROJECT_ROOT / "runtime" / "data" / "users.json", "User registry"),
        (PROJECT_ROOT / "runtime" / "policy" / "policy_rules.json", "Policy rules"),
        (PROJECT_ROOT / "runtime" / "policy" / "risk_rules.json", "Risk rules"),
    ]
    all_ok = True
    for path, label in checks:
        if not path.exists():
            logger.error("Missing: %s (%s)", path.relative_to(PROJECT_ROOT), label)
            all_ok = False

    if not all_ok:
        logger.error("")
        logger.error("System not initialized. Run first:")
        logger.error("  python scripts/init_rio.py")
        logger.error("")
    return all_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and start the server."""
    parser = argparse.ArgumentParser(description="Start the RIO Protocol server")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("RIO_DASHBOARD_HOST", "0.0.0.0"),
        help="Bind address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("RIO_DASHBOARD_PORT", "8050")),
        help="Bind port (default: 8050)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=False,
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )
    args = parser.parse_args()

    # Pre-flight
    if not preflight():
        sys.exit(1)

    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║              RIO Protocol — Starting Server             ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info("  Dashboard + API:  http://%s:%d", args.host, args.port)
    logger.info("  API docs:         http://%s:%d/docs", args.host, args.port)
    logger.info("  Admin — Policies: http://%s:%d/admin/policies", args.host, args.port)
    logger.info("  Admin — Risk:     http://%s:%d/admin/risk-models", args.host, args.port)
    logger.info("  Mode:             %s", os.environ.get("RIO_MODE", "simulated"))
    logger.info("  Reload:           %s", "enabled" if args.reload else "disabled")
    logger.info("")
    logger.info("Press Ctrl+C to stop.")
    logger.info("")

    try:
        import uvicorn
    except ImportError:
        logger.error("uvicorn not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    uvicorn.run(
        "dashboard.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=log_level.lower(),
    )


if __name__ == "__main__":
    main()
