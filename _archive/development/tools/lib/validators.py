"""Validation helpers for Odoo addon manifests and resources."""

from __future__ import annotations

import ast
import csv
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .discovery import ModuleInfo


# Dependencies in this allowlist are considered "provided by core/other layers"
# and should not block custom-module validation when they are absent from the
# scanned addons paths (scope is custom modules only).
_ALLOWED_EXTERNAL_DEPS: Set[str] = {
    "base",
    "web",
    "mail",
    "uom",
    "account",
    "sale",
    "purchase",
    "stock",
    "hr",
    "analytic",
    "queue_job",
    "spreadsheet_dashboard",
    "base_external_dbsource",
    "sql_request_abstract",
    "sql_export",
    "report_xlsx",
    "web_editor",
    "bi_view_editor",
}


@dataclass
class ValidationIssue:
    module: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    level: str = "error"
    category: str = "generic"


@dataclass
class ValidationResult:
    module: str
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.level == "error" for issue in self.issues)


class DependencyGraph:
    def __init__(self) -> None:
        # edges: prerequisite -> set(dependents)
        self.edges: Dict[str, Set[str]] = defaultdict(set)

    def add_module(self, name: str) -> None:
        self.edges.setdefault(name, set())

    def add_dependency(self, prerequisite: str, dependent: str) -> None:
        # dependent depends on prerequisite, so prerequisite precedes dependent
        self.edges.setdefault(prerequisite, set()).add(dependent)
        self.edges.setdefault(dependent, set())

    def topo_sort(self) -> Tuple[List[str], List[Set[str]]]:
        indegree: Dict[str, int] = {node: 0 for node in self.edges}
        for prereq, dependents in self.edges.items():
            for dep in dependents:
                indegree[dep] = indegree.get(dep, 0) + 1
                indegree.setdefault(prereq, 0)

        queue = deque([n for n, deg in indegree.items() if deg == 0])
        ordered: List[str] = []
        while queue:
            node = queue.popleft()
            ordered.append(node)
            for dep in self.edges.get(node, set()):
                indegree[dep] -= 1
                if indegree[dep] == 0:
                    queue.append(dep)

        if len(ordered) == len(indegree):
            return ordered, []

        remaining = {n for n, deg in indegree.items() if deg > 0}
        cycles: List[Set[str]] = []
        visited: Set[str] = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            path.append(node)
            for dep in self.edges.get(node, set()):
                if dep in remaining:
                    if dep not in visited:
                        dfs(dep, path)
                    elif dep in path:
                        cycle = set(path[path.index(dep) :])
                        if cycle not in cycles:
                            cycles.append(cycle)
            path.pop()

        for node in remaining:
            if node not in visited:
                dfs(node, [])

        return ordered, cycles


def _validate_manifest_syntax(module: ModuleInfo, issues: List[ValidationIssue]) -> Optional[dict]:
    try:
        with open(module.manifest_path, "r", encoding="utf-8") as f:
            manifest = ast.literal_eval(f.read())
        if not isinstance(manifest, dict):
            raise ValueError("Manifest must be a dict")
        return manifest
    except Exception as exc:  # noqa: BLE001
        issues.append(
            ValidationIssue(
                module=module.name,
                message=f"Manifest syntax error: {exc}",
                file=module.manifest_path,
                category="manifest",
            )
        )
        return None


def _validate_file_exists(base: str, rel_path: str) -> Optional[str]:
    candidate = os.path.join(base, rel_path)
    return candidate if os.path.isfile(candidate) else None


def _validate_xml(file_path: str, issues: List[ValidationIssue], module: ModuleInfo) -> None:
    try:
        ET.parse(file_path)
    except ET.ParseError as exc:
        issues.append(
            ValidationIssue(
                module=module.name,
                message=f"XML syntax error: {exc}",
                file=file_path,
                category="xml",
                level="error",
            )
        )


def _validate_csv(file_path: str, issues: List[ValidationIssue], module: ModuleInfo) -> None:
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample or "col1,col2")
            reader = csv.reader(f, dialect)
            for _row in reader:
                break
    except Exception as exc:  # noqa: BLE001
        issues.append(
            ValidationIssue(
                module=module.name,
                message=f"CSV read error: {exc}",
                file=file_path,
                category="csv",
            )
        )


def validate_module(module: ModuleInfo, modules_index: Dict[str, ModuleInfo]) -> ValidationResult:
    issues: List[ValidationIssue] = []
    manifest = _validate_manifest_syntax(module, issues)

    if manifest:
        for rel in (manifest.get("data") or []) + (manifest.get("demo") or []):
            full_path = _validate_file_exists(module.path, rel)
            if not full_path:
                issues.append(
                    ValidationIssue(
                        module=module.name,
                        message=f"Missing data file: {rel}",
                        file=os.path.join(module.path, rel),
                        category="missing_file",
                    )
                )
                continue
            if rel.endswith(".xml"):
                _validate_xml(full_path, issues, module)
            elif rel.endswith(".csv"):
                _validate_csv(full_path, issues, module)

        for dep in manifest.get("depends", []) or []:
            if dep in _ALLOWED_EXTERNAL_DEPS:
                continue
            if dep not in modules_index:
                issues.append(
                    ValidationIssue(
                        module=module.name,
                        message=f"Dependency not found: {dep}",
                        category="dependency",
                    )
                )

    return ValidationResult(module=module.name, issues=issues)


def build_dependency_graph(modules: Dict[str, ModuleInfo]) -> DependencyGraph:
    graph = DependencyGraph()
    for name, module in modules.items():
        graph.add_module(name)
        for dep in module.dependencies:
            graph.add_dependency(dep, name)
    return graph


def detect_circular_dependencies(graph: DependencyGraph) -> List[Set[str]]:
    _ordered, cycles = graph.topo_sort()
    return cycles
