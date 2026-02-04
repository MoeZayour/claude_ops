# OPS Accounting Development Skill

**Skill Name**: `ops-accounting`  
**Command**: `/ops-accounting`  
**Description**: OPS Matrix Accounting module development with OM patterns adoption

---

## Skill Purpose

This skill guides Claude Code through OPS Matrix Accounting module development, ensuring:
- Consistent code patterns aligned with OPS Framework architecture
- Proper adoption of OM Account Accountant patterns where applicable
- Branch isolation and governance integration
- Zero-trust security implementation

---

## Context Files (Always Load)

When this skill is invoked, Claude Code should read:

```
/opt/gemini_odoo19/claude_files/OPS_ACCOUNTING_TODO.md
/opt/gemini_odoo19/claude_files/OPS_FRAMEWORK_FEATURES_MASTER.md
```

---

## Module Location

```
/opt/gemini_odoo19/addons/ops_matrix_accounting/
```

---

## Code Patterns to Follow

### 1. Model Creation Pattern
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsModelName(models.Model):
    _name = 'ops.model.name'
    _description = 'Human Readable Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    # Company (always required)
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        required=True, 
        default=lambda self: self.env.company
    )
    
    # Matrix Dimensions (use mixin when applicable)
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=True,
        tracking=True,
        index=True
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        tracking=True,
        index=True
    )
    
    # State Machine (standard pattern)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)
    
    # Audit Fields
    name = fields.Char(string='Reference', required=True, copy=False,
                       default=lambda self: _('New'), readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.model.name') or _('New')
        return super().create(vals_list)
```

### 2. Journal Entry Creation Pattern
```python
def _create_journal_entry(self, journal, date, lines, ref=None, auto_post=True):
    """
    Standard JE creation for OPS Accounting.
    
    Args:
        journal: account.journal record
        date: Entry date
        lines: List of dicts with keys: account_id, debit, credit, partner_id, name
        ref: Reference string
        auto_post: Whether to post immediately
    
    Returns:
        account.move record
    """
    self.ensure_one()
    
    move_vals = {
        'date': date,
        'journal_id': journal.id,
        'ref': ref or self.name,
        'ops_branch_id': self.ops_branch_id.id,
        'ops_business_unit_id': self.ops_business_unit_id.id,
        'line_ids': [(0, 0, line) for line in lines],
    }
    
    move = self.env['account.move'].create(move_vals)
    
    if auto_post:
        move.action_post()
    
    return move
```

### 3. Record Rule Pattern
```xml
<!-- Branch Isolation Rule -->
<record id="rule_MODEL_branch_isolation" model="ir.rule">
    <field name="name">OPS MODEL: Branch Isolation</field>
    <field name="model_id" ref="model_ops_model_name"/>
    <field name="domain_force">[
        '|',
        ('ops_branch_id', '=', False),
        ('ops_branch_id', 'in', user.ops_branch_ids.ids)
    ]</field>
    <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### 4. Wizard Pattern
```python
class OpsWizardName(models.TransientModel):
    _name = 'ops.wizard.name'
    _description = 'Wizard Description'
    
    # Inherit from base if reporting wizard
    # _inherit = 'ops.base.report.wizard'
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )
    
    ops_branch_ids = fields.Many2many(
        'ops.branch',
        string='Branches',
        help='Leave empty for all branches'
    )
    
    def action_execute(self):
        self.ensure_one()
        # Implementation
        pass
```

### 5. Security CSV Pattern
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ops_model_user,ops.model.user,model_ops_model_name,ops_matrix_core.group_ops_user,1,0,0,0
access_ops_model_manager,ops.model.manager,model_ops_model_name,ops_matrix_core.group_ops_manager,1,1,1,0
access_ops_model_admin,ops.model.admin,model_ops_model_name,ops_matrix_core.group_ops_admin_power,1,1,1,1
access_ops_model_system,ops.model.system,model_ops_model_name,base.group_system,1,1,1,1
```

---

## OM Pattern Adoption Rules

When adopting code from OM modules:

### DO:
- ✅ Copy the business logic pattern
- ✅ Add `ops_branch_id` and `ops_business_unit_id` fields
- ✅ Add tracking=True to key fields
- ✅ Add proper indexes (index=True)
- ✅ Use OPS security groups instead of OM groups
- ✅ Add approval workflow hooks where governance applies

### DON'T:
- ❌ Copy OM's XML IDs verbatim (rename to ops_*)
- ❌ Copy OM's menu structure (integrate into OPS menus)
- ❌ Use OM's security groups
- ❌ Skip branch filtering in queries

### Specific OM → OPS Mappings

| OM Model | OPS Model | Notes |
|----------|-----------|-------|
| `account.fiscal.year` | `ops.fiscal.period` | Add soft/hard lock |
| `account.recurring.template` | `ops.recurring.template` | Add approval |
| `recurring.payment` | `ops.recurring.entry` | Expand to JE |
| `followup.followup` | `ops.followup` | Add branch |
| `followup.line` | `ops.followup.line` | Add approval override |
| `account.financial.report` | `ops.financial.report.config` | Add branch filter |

---

## Testing Commands

After making changes:

```bash
# Restart Odoo to load changes
/odoo-restart

# Update the module
/odoo-update ops_matrix_accounting

# Check logs for errors
/odoo-logs --tail 100

# Test in shell
/odoo-shell
```

---

## Git Commit Convention

Use `/ops-commit` with these prefixes:

- `[ACCT-FIX]` - Bug fixes in accounting module
- `[ACCT-FEAT]` - New features
- `[ACCT-SEC]` - Security changes
- `[ACCT-PERF]` - Performance improvements
- `[ACCT-REFACTOR]` - Code refactoring
- `[ACCT-DOC]` - Documentation

Example:
```
[ACCT-FEAT] PDC: Add journal entry creation on deposit/clear/bounce

- Added deposit_move_id, clearance_move_id, bounce_move_id fields
- Implemented action_deposit() with JE creation
- Implemented action_clear() with bank transfer JE
- Implemented action_bounce() with reversal JE
- Added PDC clearing account configuration

Refs: Phase 1.1 in OPS_ACCOUNTING_TODO.md
```

---

## Checklist Before Committing

- [ ] Model has `company_id` field
- [ ] Model has `ops_branch_id` if applicable
- [ ] Security CSV has all 4 permission levels (user/manager/admin/system)
- [ ] Record rules created for branch isolation
- [ ] Views added to `__manifest__.py`
- [ ] Sequence created if model has auto-generated name
- [ ] Tracking enabled on key fields
- [ ] Index added to frequently filtered fields
- [ ] Tests updated/created

---

## Quick Reference: Key Files

| Purpose | File Path |
|---------|-----------|
| Module manifest | `__manifest__.py` |
| Model imports | `models/__init__.py` |
| Wizard imports | `wizard/__init__.py` |
| Security ACL | `security/ir.model.access.csv` |
| Security Rules | `security/ops_accounting_rules.xml` |
| Main menus | `views/accounting_menus.xml` |
| PDC model | `models/ops_pdc.py` |
| Budget model | `models/ops_budget.py` |
| Asset model | `models/ops_asset.py` |
| Account Move ext | `models/account_move.py` |

---

## Subcommands

### `/ops-accounting status`
Show current phase progress from TODO file

### `/ops-accounting phase1`
Focus on Phase 1 critical fixes

### `/ops-accounting phase2`
Focus on Phase 2 core features

### `/ops-accounting validate`
Run validation checks:
- All models have security entries
- All views registered in manifest
- No Python syntax errors
- Record rules exist for branch isolation

### `/ops-accounting adopt <om_module>`
Guide through adopting specific OM module pattern:
- `/ops-accounting adopt fiscal_year`
- `/ops-accounting adopt recurring`
- `/ops-accounting adopt followup`
- `/ops-accounting adopt daily_reports`

---

## Example Usage

```
User: /ops-accounting phase1

Claude Code: Loading Phase 1 context from OPS_ACCOUNTING_TODO.md...

Phase 1: Critical Fixes
━━━━━━━━━━━━━━━━━━━━━━━
□ 1.1 PDC Journal Entry Integration
□ 1.2 Branch Isolation Record Rules  
□ 1.3 Budget Warning UI Display
□ 1.4 Budget Committed Amount SQL Optimization

Which task would you like to work on?
```

```
User: Let's do 1.1 PDC Journal Entry Integration

Claude Code: Opening /opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_pdc.py...

I'll implement the following changes:
1. Add journal_id, deposit_move_id, clearance_move_id, bounce_move_id fields
2. Add company setting for PDC clearing account
3. Implement action_deposit() with JE creation
4. Implement action_clear() with JE creation
5. Implement action_bounce() with reversal JE

Shall I proceed with the implementation?
```