"""Git helper that safely commits auto-fixes when present."""

from __future__ import annotations

import subprocess
from typing import Optional


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def safe_commit(module: str, description: str) -> Optional[str]:
    status = _run(["git", "status", "--porcelain"])
    if not status.stdout.strip():
        return "No changes to commit"

    _run(["git", "add", "-A"])
    msg = f"fix({module}): Auto-fix for {description}"
    result = _run(["git", "commit", "-m", msg])
    if result.returncode != 0:
        return f"Commit failed: {result.stderr.strip()}"
    return msg
