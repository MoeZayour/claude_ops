Execute Python code in Odoo shell context.

## Arguments
$ARGUMENTS = Python code to execute

## Instructions

1. Take the Python code from $ARGUMENTS

2. Execute in Odoo shell:
```bash
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
$ARGUMENTS
PYTHON
```

3. Filter out Odoo startup messages and show only relevant output

## Available in Shell
- `env` - Odoo environment with access to all models
- `self` - Current user record
- `env['model.name']` - Access any model
- `env.ref('xml_id')` - Get record by XML ID

## Examples
```python
# Count records
print(env['ops.branch'].search_count([]))

# List branches
for b in env['ops.branch'].search([]):
    print(f"{b.code}: {b.name}")

# Check user
print(env.user.name)
```
