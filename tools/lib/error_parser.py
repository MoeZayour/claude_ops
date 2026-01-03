"""Parse installer and docker logs to classify common Odoo install failures."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedError:
    error_type: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None


ERROR_PATTERNS = [
    ("missing_file", re.compile(r"No such file or directory: '([^']+)'")),
    ("missing_file", re.compile(r"could not open file:\s+([\w./-]+)")),
    ("xml_syntax", re.compile(r"XMLSyntaxError: .*?line (\d+), column (\d+)")),
    ("xml_syntax", re.compile(r"ParseError: .*?line (\d+)")),
    (
        "missing_external_ref",
        re.compile(r"External ID not found in the system: '([^']+)'"),
    ),
    (
        "missing_security_group",
        re.compile(r"Security group '(.*?)' not found"),
    ),
    (
        "invalid_python",
        re.compile(r"SyntaxError: (.*?)(?:\n|$)|NameError: name '([^']+)' is not defined"),
    ),
    (
        "db_constraint",
        re.compile(r"psycopg2\.(?:IntegrityError|OperationalError): (.*)"),
    ),
]


FILE_LINE_PATTERN = re.compile(r"File \"([^\"]+)\", line (\d+)")


def parse_error(log_output: str) -> ParsedError:
    """Classify an error from log text into a structured representation."""

    file_path = None
    line = None
    file_line_match = FILE_LINE_PATTERN.search(log_output)
    if file_line_match:
        file_path = file_line_match.group(1)
        line = int(file_line_match.group(2))

    for error_type, pattern in ERROR_PATTERNS:
        match = pattern.search(log_output)
        if not match:
            continue
        if error_type == "missing_file":
            file_path = file_path or match.group(1)
        elif error_type == "xml_syntax":
            line = line or (int(match.group(1)) if match.group(1) else None)
        elif error_type == "invalid_python":
            if match.group(2):
                return ParsedError(
                    error_type=error_type,
                    message=f"NameError: {match.group(2)}",
                    file=file_path,
                    line=line,
                )
        detail_msg = match.group(1) if match.groups() else match.group(0)
        return ParsedError(
            error_type=error_type,
            message=detail_msg,
            file=file_path,
            line=line,
        )

    tail = log_output.splitlines()[-1] if log_output else ""
    return ParsedError(error_type="unknown", message=tail, file=file_path, line=line)
