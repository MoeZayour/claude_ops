"""CLI entrypoint for the Odoo Module Installation Validator.

Phases executed in order:
1. Discovery
2. Validation
3. Dependency ordering
4. Install & retry with auto-fixes
5. Reporting
6. Git auto-commit per successful module
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from lib import (
    InstallManager,
    ReportWriter,
    build_dependency_graph,
    discover_addons,
    validate_module,
)


DEFAULTS = {
    "addons_path": os.getenv(
        "ADDONS_PATH",
        "/opt/gemini_odoo19/addons,/mnt/extra-addons,/mnt/extra-addons/oca_reporting_engine,/usr/lib/python3/dist-packages/odoo/addons",
    ),
    "db": os.getenv("DB_NAME", "mz-db"),
    "config": os.getenv("ODOO_CONF", "/etc/odoo/odoo.conf"),
    "container": os.getenv("CONTAINER", "gemini_odoo19"),
    "max_retries": int(os.getenv("MAX_RETRIES", "5")),
    "report_dir": os.getenv("REPORT_DIR", "reports"),
}


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Odoo Module Installation Validator")
    parser.add_argument("--addons-path", default=DEFAULTS["addons_path"], help="Comma-separated addons paths")
    parser.add_argument("--db", default=DEFAULTS["db"])
    parser.add_argument("--config", default=DEFAULTS["config"])
    parser.add_argument("--container", default=DEFAULTS["container"])
    parser.add_argument("--max-retries", type=int, default=DEFAULTS["max_retries"])
    parser.add_argument("--report-dir", default=DEFAULTS["report_dir"])
    parser.add_argument("--modules", help="CSV list to limit scope", default=None)
    parser.add_argument("--skip-install", action="store_true", help="Run validation only")
    parser.add_argument("--log-file", default="reports/installation_log.txt")
    parser.add_argument("--disable-tests", action="store_true", default=True)
    parser.add_argument("--verbosity", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    modules_filter = args.modules.split(",") if args.modules else None

    modules_index = discover_addons(args.addons_path, modules_filter)

    validation_results = {name: validate_module(mod, modules_index) for name, mod in modules_index.items()}
    any_errors = [res for res in validation_results.values() if not res.ok]
    if any_errors and args.skip_install:
        for res in any_errors:
            for issue in res.issues:
                print(f"[VALIDATION] {issue.module}: {issue.message}")
        return 1

    graph = build_dependency_graph(modules_index)
    order, cycles = graph.topo_sort()
    if cycles:
        print(f"[WARN] Detected circular dependencies: {cycles}")
        blocked = set().union(*cycles)
        order = [m for m in order if m not in blocked]

    report_writer = ReportWriter(args.report_dir, log_file=args.log_file)
    manager = InstallManager(
        db=args.db,
        config=args.config,
        container=args.container,
        max_retries=args.max_retries,
        disable_tests=args.disable_tests,
        report_writer=report_writer,
    )

    attempts_log: List = []
    for module_name in order:
        module = modules_index[module_name]
        outcome = manager.attempt_install(module, modules_index) if not args.skip_install else None
        if outcome:
            attempts_log.extend(outcome.attempts)

    report_writer.write_summary(attempts_log, order)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
