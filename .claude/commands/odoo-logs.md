View Odoo container logs with optional filtering.

## Arguments
$ARGUMENTS = [lines] [filter] (both optional)
- lines: Number of lines (default: 50)
- filter: Keyword to grep (e.g., "error", "warning", "ops_matrix")

## Instructions

1. Parse arguments from $ARGUMENTS:
   - If one number provided: use as line count
   - If one word provided: use as filter with default 50 lines
   - If both provided: first is lines, second is filter

2. Execute appropriate command:

Basic (no filter):
```bash
docker logs gemini_odoo19 --tail 50 2>&1
```

With filter:
```bash
docker logs gemini_odoo19 --tail 100 2>&1 | grep -i "error"
```

3. Present logs in readable format

## Common Filters
- `error` - Show errors only
- `warning` - Show warnings
- `ops_matrix` - OPS module activity
- `loading` - Module loading progress
- `traceback` - Python exceptions
