"""Installer and retry manager for Odoo modules."""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from .discovery import ModuleInfo
from .error_parser import ParsedError, parse_error
from .fixers import FixResult, apply_fix
from .git_helper import safe_commit
from .reporting import AttemptLog, ReportWriter
from .validators import ValidationResult, validate_module


@dataclass
class InstallAttempt:
    module: str
    attempt: int
    success: bool
    result: str
    fix: str
    command: str


@dataclass
class InstallationOutcome:
    module: str
    success: bool
    attempts: List[InstallAttempt]


class InstallManager:
    def __init__(
        self,
        *,
        db: str,
        config: str,
        container: str,
        max_retries: int,
        disable_tests: bool,
        report_writer: ReportWriter,
    ) -> None:
        self.db = db
        self.config = config
        self.container = container
        self.max_retries = max_retries
        self.disable_tests = disable_tests
        self.report_writer = report_writer

    def _run_docker_install(self, module: ModuleInfo) -> subprocess.CompletedProcess:
        cmd = [
            "docker",
            "exec",
            self.container,
            "odoo",
            "-c",
            self.config,
            "-d",
            self.db,
            "-i",
            module.name,
            "--stop-after-init",
        ]
        if self.disable_tests:
            cmd.append("--test-enable=0")
        return subprocess.run(cmd, capture_output=True, text=True)

    def _collect_docker_logs(self) -> str:
        proc = subprocess.run(
            ["docker", "logs", "--tail", "200", self.container],
            capture_output=True,
            text=True,
        )
        return proc.stdout + "\n" + proc.stderr

    def attempt_install(
        self,
        module: ModuleInfo,
        modules_index: Dict[str, ModuleInfo],
    ) -> InstallationOutcome:
        attempts: List[InstallAttempt] = []
        any_fix_applied = False
        last_error_desc: Optional[str] = None

        for attempt in range(1, self.max_retries + 1):
            validation: ValidationResult = validate_module(module, modules_index)
            if not validation.ok:
                issues = "; ".join(i.message for i in validation.issues)
                attempts.append(
                    InstallAttempt(
                        module=module.name,
                        attempt=attempt,
                        success=False,
                        result=issues,
                        fix="validation-only",
                        command="validation",
                    )
                )
                break

            proc = self._run_docker_install(module)
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            logs = stdout + "\n" + stderr + "\n" + self._collect_docker_logs()

            if proc.returncode == 0:
                attempt_rec = InstallAttempt(
                    module=module.name,
                    attempt=attempt,
                    success=True,
                    result="installed",
                    fix="none",
                    command="docker exec",
                )
                attempts.append(attempt_rec)
                self.report_writer.append_log(
                    AttemptLog(
                        module=module.name,
                        attempt=attempt,
                        command="docker exec",
                        result="installed",
                        fix="none",
                        success=True,
                    )
                )
                if any_fix_applied and last_error_desc:
                    safe_commit(module.name, last_error_desc)
                return InstallationOutcome(module=module.name, success=True, attempts=attempts)

            parsed: ParsedError = parse_error(logs)
            fix_result: FixResult = apply_fix(
                parsed,
                module_path=module.path,
                manifest_path=module.manifest_path,
            )
            if fix_result.applied:
                any_fix_applied = True
                last_error_desc = parsed.message

            attempts.append(
                InstallAttempt(
                    module=module.name,
                    attempt=attempt,
                    success=False,
                    result=parsed.message,
                    fix=fix_result.description,
                    command="docker exec",
                )
            )
            self.report_writer.append_log(
                AttemptLog(
                    module=module.name,
                    attempt=attempt,
                    command="docker exec",
                    result=parsed.message,
                    fix=fix_result.description,
                    success=False,
                )
            )

            if fix_result.applied:
                # Do not commit yet; commit after successful install
                pass

            if attempt < self.max_retries:
                time.sleep(2)

        return InstallationOutcome(module=module.name, success=False, attempts=attempts)
