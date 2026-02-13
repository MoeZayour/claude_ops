"""
Pre-migration script for ops_matrix_core 19.0.1.0

Fixes data integrity issues before foreign key constraints are applied during upgrade.
This ensures clean upgrade without foreign key violations.
"""

def migrate(cr, version):
    """
    Fix orphaned branch references in sale_order and purchase_order tables.
    
    Issue: Records may reference ops_branch_id values that no longer exist,
    causing foreign key constraint violations during upgrade.
    
    Solution: Set orphaned references to NULL, allowing the system to assign
    valid branches through normal business logic after upgrade.
    """
    # Check if ops_branch table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'ops_branch'
        )
    """)
    branch_table_exists = cr.fetchone()[0]
    
    if not branch_table_exists:
        # If ops_branch doesn't exist yet, no cleanup needed
        return
    
    # Get valid branch IDs
    cr.execute("SELECT id FROM ops_branch")
    valid_branch_ids = {row[0] for row in cr.fetchall()}
    
    if not valid_branch_ids:
        # No branches exist, nullify all references
        print("Pre-migration: No branches found, nullifying all branch references")
        
        # Clean sale_order
        cr.execute("""
            UPDATE sale_order 
            SET ops_branch_id = NULL 
            WHERE ops_branch_id IS NOT NULL
        """)
        affected = cr.rowcount
        if affected > 0:
            print(f"Pre-migration: Nullified {affected} sale_order.ops_branch_id references")
        
        # Clean purchase_order
        cr.execute("""
            UPDATE purchase_order 
            SET ops_branch_id = NULL 
            WHERE ops_branch_id IS NOT NULL
        """)
        affected = cr.rowcount
        if affected > 0:
            print(f"Pre-migration: Nullified {affected} purchase_order.ops_branch_id references")
    
    else:
        # Clean orphaned references in sale_order
        cr.execute("""
            SELECT COUNT(*) 
            FROM sale_order 
            WHERE ops_branch_id IS NOT NULL 
            AND ops_branch_id NOT IN %s
        """, (tuple(valid_branch_ids),))
        orphaned_sales = cr.fetchone()[0]
        
        if orphaned_sales > 0:
            print(f"Pre-migration: Found {orphaned_sales} orphaned sale_order.ops_branch_id references")
            cr.execute("""
                UPDATE sale_order 
                SET ops_branch_id = NULL 
                WHERE ops_branch_id IS NOT NULL 
                AND ops_branch_id NOT IN %s
            """, (tuple(valid_branch_ids),))
            print(f"Pre-migration: Fixed {cr.rowcount} orphaned sale_order.ops_branch_id references")
        
        # Clean orphaned references in purchase_order  
        cr.execute("""
            SELECT COUNT(*) 
            FROM purchase_order 
            WHERE ops_branch_id IS NOT NULL 
            AND ops_branch_id NOT IN %s
        """, (tuple(valid_branch_ids),))
        orphaned_purchases = cr.fetchone()[0]
        
        if orphaned_purchases > 0:
            print(f"Pre-migration: Found {orphaned_purchases} orphaned purchase_order.ops_branch_id references")
            cr.execute("""
                UPDATE purchase_order 
                SET ops_branch_id = NULL 
                WHERE ops_branch_id IS NOT NULL 
                AND ops_branch_id NOT IN %s
            """, (tuple(valid_branch_ids),))
            print(f"Pre-migration: Fixed {cr.rowcount} orphaned purchase_order.ops_branch_id references")
    
    print("Pre-migration: Data integrity checks completed successfully")
