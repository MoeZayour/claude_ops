"""Reporting utilities for installation attempts and summaries."""

from __future__ import annotations

import datetime as dt
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AttemptLog:
    module: str
    attempt: int
    command: str
    result: str
    fix: str
    success: bool
    timestamp: dt.datetime = field(default_factory=dt.datetime.utcnow)


class ReportWriter:
    def __init__(self, report_dir: str, log_file: Optional[str] = None) -> None:
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        self.log_file = log_file or os.path.join(report_dir, "installation_log.txt")
        self.summary_file = os.path.join(report_dir, "installation_report.md")

    def append_log(self, entry: AttemptLog) -> None:
        line = (
            f"[{entry.timestamp.isoformat()}] module={entry.module} attempt={entry.attempt} "
            f"success={entry.success} cmd={entry.command} result={entry.result} fix={entry.fix}\n"
        )
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def write_summary(
        self,
        attempts: List[AttemptLog],
        dependency_order: List[str],
    ) -> None:
        successes = [a for a in attempts if a.success]
        failures = [a for a in attempts if not a.success]
        retries_by_module: Dict[str, int] = {}
        for entry in attempts:
            retries_by_module[entry.module] = max(retries_by_module.get(entry.module, 0), entry.attempt)

        errors = Counter([a.result for a in attempts if not a.success])
        most_common_error = errors.most_common(1)[0][0] if errors else "n/a"

        lines = [
            "# Installation Report",
            "",
            f"Generated: {dt.datetime.utcnow().isoformat()} UTC",
            f"Total attempts: {len(attempts)}",
            f"Successful modules: {len(set(a.module for a in successes))}",
            f"Failed modules: {len(set(a.module for a in failures))}",
            f"Most common error: {most_common_error}",
            "",
            "## Dependency order",
            "",
            " -> ".join(dependency_order) or "(none)",
            "",
            "## Attempts",
        ]

        for entry in attempts:
            lines.append(
                f"- {entry.module} attempt {entry.attempt}: {'✅' if entry.success else '❌'} "
                f"{entry.result}; fix={entry.fix}"
            )

        lines.append("")
        lines.append("## Retries per module")
        for mod, retry in retries_by_module.items():
            lines.append(f"- {mod}: {retry} attempts")

        with open(self.summary_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
