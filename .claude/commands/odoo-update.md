Update one or more Odoo modules.

## Arguments
$ARGUMENTS = module name(s), comma-separated for multiple

## Instructions

1. Parse module name(s) from $ARGUMENTS
   - Single: `ops_matrix_core`
   - Multiple: `ops_matrix_core,ops_matrix_accounting`

2. If no argument provided, ask which module to update

3. Run the update:
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u $ARGUMENTS --stop-after-init --no-http
```

4. Check output for errors and report result

## Common Modules
- `ops_matrix_core` - Core framework
- `ops_matrix_accounting` - Accounting features
- `ops_matrix_asset_management` - Asset tracking

## Error Patterns
- `ParseError` - XML syntax error
- `KeyError` / `AttributeError` - Python code issue
- `FOREIGN KEY` - Database constraint violation
- `Access Denied` - Permission issue
