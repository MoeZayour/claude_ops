#!/bin/bash
# Phase 3D Reporting Audit Execution Wrapper

docker exec gemini_odoo19 bash -c "cat > /tmp/audit_runner.py << 'PYEOF'
import sys
import os

# Import the audit script functions
sys.path.insert(0, '/mnt/extra-addons/scripts')

# Execute in current environment
exec(open('/mnt/extra-addons/scripts/phase3d_reporting_audit.py').read())
PYEOF

odoo shell -d mz-db --no-http < /tmp/audit_runner.py
"
