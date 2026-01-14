#!/bin/bash
echo "=============================================="
echo "FINAL VERIFICATION - OPS MODULES ON ODOO 19"
echo "=============================================="
echo ""

# Check database status
echo "1. Database Module Status:"
echo "-------------------------------------------"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t -c "
SELECT 
    '   ' || name || ': ' || 
    CASE 
        WHEN state = 'installed' THEN '✅ INSTALLED'
        ELSE '❌ ' || UPPER(state)
    END as status
FROM ir_module_module 
WHERE name LIKE 'ops_matrix%' 
ORDER BY name;" | grep -v "^$"

echo ""
echo "2. Module Dependencies:"
echo "-------------------------------------------"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t -c "
SELECT DISTINCT
    '   ' || m.name || ' requires: ' || COALESCE(d.name, 'base')
FROM ir_module_module m
LEFT JOIN ir_module_module_dependency md ON md.module_id = m.id
LEFT JOIN ir_module_module d ON d.name = md.name
WHERE m.name LIKE 'ops_matrix%'
ORDER BY m.name, d.name;" | grep -v "^$" | head -20

echo ""
echo "3. Installed Models Count:"
echo "-------------------------------------------"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t -c "
SELECT 
    '   ' || split_part(model, '.', 1) || '.' || split_part(model, '.', 2) || 
    ' models: ' || COUNT(*)::text
FROM ir_model
WHERE model LIKE 'ops.%'
GROUP BY split_part(model, '.', 1), split_part(model, '.', 2)
ORDER BY 1;" | grep -v "^$"

echo ""
echo "4. Installed Views Count:"
echo "-------------------------------------------"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t -c "
SELECT 
    '   Total OPS views: ' || COUNT(*)::text
FROM ir_ui_view
WHERE name LIKE 'ops.%' OR model LIKE 'ops.%';" | grep -v "^$"

echo ""
echo "5. Installed Menu Items:"
echo "-------------------------------------------"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t -c "
SELECT 
    '   Total OPS menu items: ' || COUNT(*)::text
FROM ir_ui_menu
WHERE name LIKE '%OPS%' OR name LIKE '%Matrix%';" | grep -v "^$"

echo ""
echo "6. Cron Jobs:"
echo "-------------------------------------------"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t -c "
SELECT 
    '   ' || name || ' [' || 
    CASE WHEN active THEN 'ACTIVE' ELSE 'inactive' END || ']'
FROM ir_cron
WHERE name LIKE '%OPS:%'
ORDER BY name;" | grep -v "^$"

echo ""
echo "=============================================="
echo "VERIFICATION COMPLETE"
echo "=============================================="
