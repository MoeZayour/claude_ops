# OPS Report Redesign — Execution Strategy

## Folder Contents

| File | What | Agent Needed |
|------|------|-------------|
| `00_MANDATORY_RULES.md` | wkhtmltopdf compatibility rules — READ FIRST | All agents |
| `00_EXECUTION_STRATEGY.md` | This file — parallel execution plan | Human reference |
| `WAVE1_TRANSACTION_LEDGERS.md` | Cash Book, Day Book, Bank Book, Partner Ledger | Agent 1 |
| `WAVE2_AGING_REPORTS.md` | Aged Receivables, Aged Payables | Agent 2 |
| `WAVE3_FINANCIAL_STATEMENTS.md` | P&L, Balance Sheet, Trial Balance | Agent 3 |
| `WAVE4_REGISTER_REPORTS.md` | Asset Register, PDC Registry, PDC Maturity | Agent 4 |
| `WAVE5_ANALYTICAL_REPORTS.md` | Budget vs Actual, BU Profitability, Branch P&L | Agent 5 |
| `WAVE6_ADVANCED_STATEMENTS.md` | Cash Flow, Consolidated P&L | Agent 6 |
| `WAVE_FINAL_INTEGRATION.md` | Merge all, update manifest, full test | Final agent |

---

## Prerequisites (Must Be Done BEFORE Any Wave)

The GL Round 2 prompt must have completed successfully. It creates:
- `/ops_matrix_accounting/static/src/img/ops_badge_footer.png`
- Company fields: `ops_report_primary_color`, `ops_report_text_on_primary`, `ops_report_body_text_color`
- Helper methods: `_get_report_primary_light()`, `_get_report_primary_dark()`
- Paperformat records: `paperformat_ops_portrait`, `paperformat_ops_landscape`

If these don't exist yet, Wave 1 must create them. All other waves use fallbacks (see Rule 10 in mandatory rules).

---

## Parallel Execution Plan

### Round 1 — Sequential (Wave 1 FIRST)
```
Wave 1: Transaction Ledgers
├── Creates shared patterns other waves reference
├── Validates mandatory rules work in practice
└── Estimated: 5 hours
```

### Round 2 — Parallel (3 agents simultaneously)
```
Wave 2: Aging Reports        ← Agent A (2.5 hours)
Wave 3: Financial Statements ← Agent B (4 hours)
Wave 4: Register Reports     ← Agent C (3 hours)
```

### Round 3 — Parallel (2 agents simultaneously)
```
Wave 5: Analytical Reports   ← Agent D (4 hours)
Wave 6: Advanced Statements  ← Agent E (3.5 hours)
```

### Round 4 — Sequential (Integration)
```
Wave Final: Merge + Manifest + Test ← Single agent (1.5 hours)
```

### Round 5 — Future
```
Wave 7: Excel variants for all reports ← After all PDFs verified
```

**Total calendar time with parallelization: ~3 rounds ≈ 14 hours**
**Without parallelization: ~22 hours sequential**

---

## Critical Rules for Parallel Execution

### Rule 1: NO MANIFEST EDITS
Each wave creates Python files, XML templates, and security rules but does **NOT** edit:
- `__manifest__.py`
- `models/__init__.py`
- `wizard/__init__.py`
- `report/__init__.py`

The integration prompt handles all manifest/init updates.

### Rule 2: NO SHARED FILE EDITS
Each wave ONLY touches files it creates. Never edit:
- `ops_general_ledger_*` files (GL owns these)
- Another wave's report files
- `ops_internal_report.css` (dead — all CSS is inline now)

### Rule 3: GIT BRANCH PER WAVE
```bash
# Before starting each wave:
cd /opt/gemini_odoo19
git checkout main
git pull origin main
git checkout -b wave-N-description

# After wave completes:
git add -A
git commit -m "feat(accounting): Wave N - description"
git push origin wave-N-description
```

Integration prompt merges all branches into main.

### Rule 4: EVERY AGENT READS MANDATORY RULES FIRST
Before executing any wave prompt, the agent MUST read `00_MANDATORY_RULES.md`. 
Instruction to prepend to every wave:

```
BEFORE executing this prompt, read the file 00_MANDATORY_RULES.md in this folder.
Those rules override any conflicting patterns in this prompt.
```

---

## File Naming Convention

Each wave creates files following this pattern:

```
report/
├── ops_cash_book_report.py          ← Python data layer
├── ops_cash_book_template.xml       ← QWeb template
├── ops_day_book_report.py
├── ops_day_book_template.xml
└── ...

wizard/
├── ops_cash_book_wizard.py          ← Only if wizard needs changes
└── ...

data/
├── ops_report_paperformat.xml       ← Only Wave 1 creates this
└── ...
```

Each wave's files are prefixed with the report name — no collisions between waves.

---

## How to Launch an Agent

For each wave, open a Claude Code terminal and run:

```bash
# Step 1: Read mandatory rules
cat /opt/gemini_odoo19/claude_files/wave_prompts/00_MANDATORY_RULES.md

# Step 2: Read wave prompt
cat /opt/gemini_odoo19/claude_files/wave_prompts/WAVE{N}_{NAME}.md

# Step 3: Execute
# Agent reads both files and begins autonomous execution
```

Or paste the mandatory rules + wave prompt as a single input.

---

## Verification After All Waves

After integration, verify:
1. Module installs: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init`
2. No errors in logs: `docker logs gemini_odoo19 --tail 100 | grep -i error`
3. Each report generates PDF without errors
4. Footer appears on every page of every report
5. Colors render correctly (no CSS loading failures)
6. UTF-8 characters display properly (no mojibake)
