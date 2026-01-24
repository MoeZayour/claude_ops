Analyze an Odoo model to understand its structure, fields, and relationships.

## Arguments
$ARGUMENTS = model name (e.g., "ops.branch", "account.move")

## Instructions

1. Parse the model name from $ARGUMENTS

2. Find the model definition:
```bash
grep -r "_name = '$ARGUMENTS'" /opt/gemini_odoo19/addons/ops_matrix_*/models/
```

3. Read the model file and extract:
   - All fields (name, type, attributes)
   - Computed fields and their dependencies
   - Constraints (_sql_constraints, @api.constrains)
   - Related models (Many2one, One2many, Many2many)
   - Key methods (@api.depends, @api.onchange, action_*)

4. Present a structured summary:

```
Model: <model_name>
Table: <table_name>
Inherits: <inherited_models>

Fields:
  - name (Char, required)
  - code (Char, required, unique)
  - company_id (Many2one -> res.company)
  ...

Relationships:
  - company_id -> res.company (Many2one)
  - line_ids <- child.model (One2many)

Key Methods:
  - action_confirm(): Confirms the record
  - _compute_total(): Computes total field
```
