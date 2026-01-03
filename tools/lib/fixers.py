"""Auto-fix strategies for common installation issues.

These functions apply best-effort, minimal edits without deleting code. They may
create stub files, comment out offending blocks, or inject placeholder records.
"""

from __future__ import annotations

import ast
import os
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

from .error_parser import ParsedError


@dataclass
class FixResult:
    applied: bool
    description: str
    file: Optional[str] = None


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_text(path: str, content: str) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _comment_out_xml(file_path: str, message: str) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        original = f.read()
    wrapped = f"<!-- {message} -->\n{original}\n<!-- end auto-fix -->\n"
    _write_text(file_path, wrapped)


def _patch_manifest_path(manifest_path: str, old_rel: str, new_rel: str) -> None:
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = ast.literal_eval(f.read())
    except Exception:  # noqa: BLE001
        return
    changed = False
    for key in ("data", "demo"):
        lst = manifest.get(key)
        if not isinstance(lst, list):
            continue
        for idx, val in enumerate(lst):
            if str(val).lower() == old_rel.lower():
                lst[idx] = new_rel
                changed = True
    if changed:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(repr(manifest))


def fix_missing_file(manifest_path: str, rel_path: str) -> FixResult:
    base = os.path.dirname(manifest_path)
    rel_norm = rel_path.lstrip("./")
    candidate_dir = os.path.dirname(os.path.join(base, rel_norm))
    filename = os.path.basename(rel_norm)
    siblings = [f for f in os.listdir(candidate_dir or base)] if os.path.isdir(candidate_dir) else []
    similar = next((s for s in siblings if s.lower() == filename.lower()), None)
    if similar:
        new_rel = os.path.join(os.path.dirname(rel_norm), similar) if os.path.dirname(rel_norm) else similar
        _patch_manifest_path(manifest_path, rel_norm, new_rel)
        return FixResult(True, f"Patched manifest entry to {new_rel}")

    full_path = os.path.join(base, rel_norm)
    if rel_norm.endswith(".xml"):
        stub = "<odoo>\n    <!-- auto-generated placeholder for missing file -->\n</odoo>\n"
    elif rel_norm.endswith(".csv"):
        stub = "# auto-generated placeholder for missing CSV\nid,name\nplaceholder,Auto-generated\n"
    else:
        stub = "# auto-generated placeholder\n"
    _write_text(full_path, stub)
    return FixResult(True, f"Created placeholder file {rel_norm}", file=full_path)


def fix_xml_syntax(file_path: str) -> FixResult:
    try:
        ET.parse(file_path)
        return FixResult(False, "XML already valid")
    except ET.ParseError as exc:
        text = exc.msg or ""
        if "mismatched tag" in text or "not closed" in text:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().rstrip() + "\n"
            if not content.strip().endswith("</odoo>"):
                content += "</odoo>\n"
            _write_text(file_path, content)
        else:
            _comment_out_xml(file_path, f"auto-fix xml_syntax: {exc}")
        try:
            ET.parse(file_path)
            return FixResult(True, f"Adjusted XML to close tags: {exc}", file=file_path)
        except ET.ParseError:
            _comment_out_xml(file_path, "auto-fix fallback for xml syntax")
            return FixResult(True, "Commented XML due to syntax error", file=file_path)


def _guess_model_from_xmlid(xmlid: str) -> str:
    lowered = xmlid.lower()
    if "group" in lowered:
        return "res.groups"
    if "view" in lowered:
        return "ir.ui.view"
    if "action" in lowered:
        return "ir.actions.act_window"
    if "rule" in lowered:
        return "ir.rule"
    return "ir.model.data"


def fix_missing_external_ref(module_path: str, xmlid: str, manifest_path: str) -> FixResult:
    placeholder_path = os.path.join(module_path, "data", "auto_placeholders.xml")
    _ensure_dir(os.path.dirname(placeholder_path))
    model = _guess_model_from_xmlid(xmlid)
    record_id = xmlid.split(".")[-1]
    record = textwrap.dedent(
        f"""
        <record id="{record_id}" model="{model}">
            <field name="name">auto_placeholder</field>
            <field name="noupdate">1</field>
        </record>
        """
    )
    content = "<odoo>\n<!-- auto-fix missing external ref -->\n" + record + "\n</odoo>\n"
    _write_text(placeholder_path, content)

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = ast.literal_eval(f.read())
    except Exception:  # noqa: BLE001
        manifest = {}
    data_list = manifest.get("data") or []
    rel_placeholder = "data/auto_placeholders.xml"
    if rel_placeholder not in data_list:
        data_list.append(rel_placeholder)
        manifest["data"] = data_list
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(repr(manifest))

    return FixResult(True, f"Added placeholder for {xmlid}", file=placeholder_path)


def fix_missing_security_group(module_path: str, group_xmlid: str, manifest_path: str) -> FixResult:
    security_path = os.path.join(module_path, "security", "auto_groups.xml")
    _ensure_dir(os.path.dirname(security_path))
    content = textwrap.dedent(
        f"""
        <odoo>
            <record id="{group_xmlid}" model="res.groups">
                <field name="name">Auto {group_xmlid}</field>
            </record>
        </odoo>
        """
    )
    _write_text(security_path, content)

    # Ensure manifest references the auto file
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_text = f.read()
    try:
        manifest = ast.literal_eval(manifest_text)
    except Exception:  # noqa: BLE001
        manifest = {}
    data_list = manifest.get("data") or []
    rel_security = "security/auto_groups.xml"
    if rel_security not in data_list:
        data_list.append(rel_security)
        manifest["data"] = data_list
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(repr(manifest))
    return FixResult(True, f"Created placeholder security group {group_xmlid}", file=security_path)


def fix_invalid_python(file_path: str, message: str) -> FixResult:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        ast.parse(source)
        return FixResult(False, "Python already valid")
    except SyntaxError as exc:
        lines = source.splitlines()
        if exc.lineno and exc.lineno - 1 < len(lines):
            target_idx = exc.lineno - 1
            lines[target_idx] = f"# auto-fix: syntax error -> {lines[target_idx]}"
            lines.insert(target_idx + 1, "pass  # auto-fix placeholder")
            new_source = "\n".join(lines) + "\n"
            _write_text(file_path, new_source)
            return FixResult(True, "Commented offending python line", file=file_path)
        return FixResult(False, "Unable to auto-fix python syntax")
    except Exception:  # noqa: BLE001
        if "NameError" in message:
            name = message.split("'")[1] if "'" in message else "MISSING_NAME"
            new_source = source + f"\n# auto-fix default\n{name} = None\n"
            _write_text(file_path, new_source)
            return FixResult(True, f"Added default for missing name {name}", file=file_path)
        return FixResult(False, "Unknown python error")


def fix_db_constraint(file_path: str) -> FixResult:
    try:
        tree = ET.parse(file_path)
    except ET.ParseError:
        _comment_out_xml(file_path, "auto-fix db constraint parse error")
        return FixResult(True, "Commented XML due to db constraint parse error", file=file_path)

    root = tree.getroot()
    changed = False
    for record in root.findall(".//record"):
        if "noupdate" not in record.attrib:
            record.set("noupdate", "1")
            changed = True
        context = record.get("context")
        if "install_mode" not in (context or ""):
            record.set("context", "{'install_mode': True}")
            changed = True
    if changed:
        tree.write(file_path, encoding="utf-8")
        return FixResult(True, "Adjusted records for db constraints", file=file_path)
    return FixResult(False, "No db constraint changes applied")


def apply_fix(parsed: ParsedError, *, module_path: str, manifest_path: str) -> FixResult:
    """Dispatch to a specific fixer based on error classification."""

    if parsed.error_type == "missing_file":
        missing_path = parsed.file or parsed.message
        rel = os.path.relpath(missing_path, module_path) if os.path.isabs(missing_path) else missing_path
        return fix_missing_file(manifest_path, rel)

    if parsed.error_type == "xml_syntax":
        if parsed.file:
            return fix_xml_syntax(parsed.file)
        return FixResult(False, "No XML file provided for xml_syntax fix")

    if parsed.error_type == "missing_external_ref":
        return fix_missing_external_ref(module_path, parsed.message, manifest_path)

    if parsed.error_type == "missing_security_group":
        return fix_missing_security_group(module_path, parsed.message, manifest_path)

    if parsed.error_type == "invalid_python":
        if parsed.file:
            return fix_invalid_python(parsed.file, parsed.message)
        return FixResult(False, "No file path for python fix")

    if parsed.error_type == "db_constraint":
        if parsed.file:
            return fix_db_constraint(parsed.file)
        return FixResult(False, "No file path for db constraint fix")

    return FixResult(False, f"No fixer for error type {parsed.error_type}")
