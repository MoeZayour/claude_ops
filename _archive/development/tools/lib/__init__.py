"""Utility library for the Odoo Module Installation Validator.

This package aggregates helpers for discovery, validation, error parsing,
auto-fix strategies, installation orchestration, git automation, and reporting.
All modules are intentionally stdlib-only to remain portable inside the Odoo
deployment environment.
"""

from .discovery import ModuleInfo, discover_addons
from .validators import (
    ValidationIssue,
    ValidationResult,
    DependencyGraph,
    build_dependency_graph,
    detect_circular_dependencies,
    validate_module,
)
from .error_parser import ParsedError, parse_error
from .fixers import FixResult, apply_fix
from .installer import InstallationOutcome, InstallAttempt, InstallManager
from .git_helper import safe_commit
from .reporting import ReportWriter

__all__ = [
    "ModuleInfo",
    "discover_addons",
    "ValidationIssue",
    "ValidationResult",
    "DependencyGraph",
    "build_dependency_graph",
    "detect_circular_dependencies",
    "validate_module",
    "ParsedError",
    "parse_error",
    "FixResult",
    "apply_fix",
    "InstallationOutcome",
    "InstallAttempt",
    "InstallManager",
    "safe_commit",
    "ReportWriter",
]
