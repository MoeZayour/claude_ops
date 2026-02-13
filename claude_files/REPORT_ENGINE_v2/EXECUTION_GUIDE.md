# OPS Report Engine v2 — Execution Guide
# ==========================================
# Total: 6 phases, run sequentially via Claude Code CLI
# Each phase is a standalone prompt file in this directory.

## Quick Start

```bash
cd /opt/gemini_odoo19/claude_files/REPORT_ENGINE_v2

# Phase 0: Archive old code (~5 min)
claude -p "$(cat PHASE_0_ARCHIVE.md)"

# Phase 1: Data contracts + bridge parser (~15 min)
claude -p "$(cat PHASE_1_CONTRACTS.md)"

# Phase 2: QWeb templates + report actions (~20 min)
claude -p "$(cat PHASE_2_TEMPLATES.md)"

# Phase 3: Financial wizards - GL, TB, P&L, BS, CF, Aged, Partner (~45 min)
claude -p "$(cat PHASE_3_FINANCIAL_WIZARDS.md)"

# Phase 4: Refactor remaining wizards - Daily, Treasury, Assets, Inventory, Budget (~30 min)
claude -p "$(cat PHASE_4_REMAINING_WIZARDS.md)"

# Phase 5: Excel renderer, controller, menus, manifest, test (~30 min)
claude -p "$(cat PHASE_5_FINALIZE.md)"
```

## Between Phases

After each phase, verify output before proceeding:
- Phase 0: `ls _archived_reports/v1/report/ | wc -l` should be ~21
- Phase 1: `python3 -c "from report.ops_report_contracts import *"` should work
- Phase 2: `grep 'template id=' report/ops_report_*.xml | wc -l` should be 30+
- Phase 3: `ls wizard/ops_*_wizard.py | wc -l` should be 14+
- Phase 4: `grep '_get_report_data' wizard/ops_*.py | wc -l` should match wizard count
- Phase 5: Module loads without errors

## Architecture Summary

```
29 Reports → 3 Shapes → 1 Pipeline

Shape A (Lines):     GL, Partner Ledger, SOA, Cash/Day/Bank Book
Shape B (Hierarchy): P&L, BS, CF, Budget, Consolidation (4)
Shape C (Matrix):    TB, Aged, Assets (5), Inventory (4), Treasury (3)

Pipeline: Wizard → Data Contract → Bridge Parser → QWeb Template → PDF/Excel/HTML
```

## Files in This Directory

| File | Purpose |
|------|---------|
| REPORT_ENGINE_REWRITE_MASTER.md | Full architecture specification |
| PHASE_0_ARCHIVE.md | Archive old code |
| PHASE_1_CONTRACTS.md | Data contracts + bridge parser |
| PHASE_2_TEMPLATES.md | QWeb templates + report actions |
| PHASE_3_FINANCIAL_WIZARDS.md | Core financial wizards |
| PHASE_4_REMAINING_WIZARDS.md | Remaining wizard refactoring |
| PHASE_5_FINALIZE.md | Excel, controller, menus, testing |
| EXECUTION_GUIDE.md | This file |

## Detailed Prompts

The files in this directory are concise summaries optimized for VPS storage.
Full detailed prompts with complete code examples are available as downloadable
files from the Claude Chat conversation where this spec was created.
These detailed versions include:
- Complete dataclass definitions with all fields
- Full bridge parser code
- Detailed template XML structures
- Complete wizard implementation patterns
- Full ACL entry patterns
- Comprehensive verification commands
