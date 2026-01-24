Check the installation status of all OPS Matrix modules.

## Instructions

1. Query module states via Odoo shell:
```bash
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
modules = env['ir.module.module'].search([('name', 'like', 'ops_matrix%')])
print("\n{:<35} {:<15} {}".format("MODULE", "STATE", "VERSION"))
print("-" * 65)
for m in modules.sorted('name'):
    print("{:<35} {:<15} {}".format(m.name, m.state, m.latest_version or '-'))
PYTHON
```

2. Show filesystem versions from manifests:
```bash
for f in /opt/gemini_odoo19/addons/ops_matrix_*/__manifest__.py; do
    module=$(basename $(dirname $f))
    version=$(grep -o "'version'.*" $f | cut -d"'" -f3)
    echo "$module: $version"
done
```

3. Present comparison showing any version mismatches between database and filesystem.

## Module States Reference
- `installed` - Active and working
- `uninstalled` - Removed but record exists
- `to upgrade` - Pending upgrade on restart
- `to install` - Pending installation
- `uninstallable` - Missing dependencies
