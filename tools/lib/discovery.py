"""Module discovery utilities for Odoo addons.

Phase 1: Walk an addons path and collect manifest metadata safely using
``ast.literal_eval`` to avoid arbitrary execution.
"""

from __future__ import annotations

import ast
import json
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Union


@dataclass
class ModuleInfo:
    # ``name`` is the technical module name (directory name)
    name: str
    path: str
    manifest_path: str
    version: Optional[str]
    display_name: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    data_files: List[str] = field(default_factory=list)
    demo_files: List[str] = field(default_factory=list)
    external_dependencies: Dict[str, List[str]] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, sort_keys=True)


def _safe_read_manifest(manifest_path: str) -> Dict:
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        manifest = ast.literal_eval(content)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid manifest syntax at {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"Manifest {manifest_path} is not a dict")
    return manifest


def _normalize_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(v) for v in value]
    return []


def discover_addons(
    addons_paths: Union[str, Sequence[str]], modules_filter: Optional[List[str]] = None
) -> Dict[str, ModuleInfo]:
    """Discover Odoo addons by locating ``__manifest__.py`` files across one or more paths.

    Args:
        addons_paths: Base directories where addons live (single path or list/CSV string).
        modules_filter: Optional list of module names to restrict discovery.

    Returns:
        Dict of module name to :class:`ModuleInfo`.
    """

    paths: List[str]
    if isinstance(addons_paths, str):
        paths = [p.strip() for p in addons_paths.split(",") if p.strip()]
    else:
        paths = list(addons_paths)

    modules: Dict[str, ModuleInfo] = {}
    for base in paths:
        if not base:
            continue
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            if "__manifest__.py" not in files:
                continue
            manifest_path = os.path.join(root, "__manifest__.py")
            technical_name = os.path.basename(root)
            try:
                manifest = _safe_read_manifest(manifest_path)
            except Exception:
                # Record as broken with minimal info; validation phase will elaborate.
                if technical_name not in modules:
                    modules[technical_name] = ModuleInfo(
                        name=technical_name,
                        path=root,
                        manifest_path=manifest_path,
                        version=None,
                        display_name=None,
                    )
                continue

            display_name = manifest.get("name")
            module_key = technical_name

            if modules_filter and (module_key not in modules_filter and display_name not in modules_filter):
                continue

            if module_key in modules:
                # Keep first discovered occurrence; assume first path order precedence.
                continue

            module = ModuleInfo(
                name=module_key,
                path=root,
                manifest_path=manifest_path,
                version=manifest.get("version"),
                display_name=display_name,
                dependencies=_normalize_list(manifest.get("depends")),
                data_files=_normalize_list(manifest.get("data")),
                demo_files=_normalize_list(manifest.get("demo")),
                external_dependencies={
                    key: _normalize_list(val)
                    for key, val in (manifest.get("external_dependencies") or {}).items()
                },
            )
            modules[module_key] = module

    return modules
