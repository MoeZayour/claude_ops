-- OPS Framework - Fix Duplicate Menus (OPTIONAL)
-- Run this if you want to clean up duplicate menu entries
-- This is cosmetic only - all functionality works without this

-- 1. Deactivate duplicate Asset Categories menu (keep ID 417, deactivate 407)
UPDATE ir_ui_menu 
SET active = false 
WHERE id = 407 
  AND (name->>'en_US') = 'Asset Categories';

-- 2. Deactivate duplicate Assets menu (keep ID 404, deactivate 416)
UPDATE ir_ui_menu 
SET active = false 
WHERE id = 416 
  AND (name->>'en_US') = 'Assets';

-- 3. Menu ID 573 (Excel Export) is already inactive - no action needed

-- Verify the changes
SELECT 
    m.name->>'en_US' as menu_name,
    m.id as menu_id,
    m.active,
    a.name->>'en_US' as action_name
FROM ir_ui_menu m
LEFT JOIN ir_act_window a ON m.action = ('ir.actions.act_window,' || a.id)
WHERE (m.name->>'en_US') IN ('Excel Export', 'Asset Categories', 'Assets')
  AND m.id IN (573, 574, 407, 417, 404, 416)
ORDER BY m.name->>'en_US', m.id;
