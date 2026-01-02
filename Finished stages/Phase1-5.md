Phase 1: The User Matrix (Who sees what?)Goal: Link Users to Branches and Business Units so the system knows their "Context".Prompt for Cline:textCopy code[data-radix-scroll-area-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-scroll-area-viewport]::-webkit-scrollbar{display:none}@workspace We are moving to Phase 1: User Matrix.
I need to link Users to the Matrix structure we built.

1.  **Extend `res.users`:**
    *   Add `ops_allowed_branch_ids` (Many2many to `ops.branch`).
    *   Add `ops_default_branch_id` (Many2one to `ops.branch`).
    *   Add `ops_allowed_business_unit_ids` (Many2many to `ops.business.unit`).
    *   Add `ops_default_business_unit_id` (Many2one to `ops.business.unit`).

2.  **Constraints & Logic:**
    *   Add a Python constraint: The `ops_default_branch_id` MUST be present in `ops_allowed_branch_ids`. Same logic for Business Units.
    *   Onchange: If a user selects a Default, automatically add it to the Allowed list if missing.

3.  **UI:**
    *   Add a new tab "Matrix Permissions" in the User Form View to display these fields.

4.  **Tech Stack:** Odoo 19. Use `Command` for x2many operations if needed.✅ Verification Step:
Go to Settings > Users. Open "Admin".
Check for the "Matrix Permissions" tab.
Try to set a "Default Branch" that is not in the "Allowed" list. Result: The system should either auto-add it (Onchange) or block you (Constraint).
Phase 2: Data Integrity (Silos & Stewardship)Goal: Ensure Products and Partners are governed by the Matrix before we start selling.Prompt for Cline:textCopy code[data-radix-scroll-area-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-scroll-area-viewport]::-webkit-scrollbar{display:none}@workspace 

Phase 2: Data Integrity (Product & Partner).

1.  **Product Silo (`product.template`):**
    *   Add `business_unit_id` (Many2one).
    *   **Search Logic:** If a user searches for products, they should ONLY see products where `business_unit_id` matches their `user.ops_allowed_business_unit_ids` OR is not set (Global). Use a Record Rule for this.

2.  **Partner Stewardship (`res.partner`):**
    *   Add `ops_state` selection field: `[('draft', 'Draft'), ('approved', 'Approved')]`. Default is 'draft'.
    *   **Logic:** Only users in a specific group (create a dummy XML group `group_ops_steward` for now) can move it to 'Approved'.
    *   **Constraint:** Prevent using 'Draft' partners in confirmed Sales Orders (we will enforce this in Phase 3, just add the field now).

3.  **Pricing Matrix (`product.pricelist`):**
    *   Add `ops_branch_id` and `ops_business_unit_id`.
    *   **Rule:** Users only see Pricelists matching their Allowed Matrix.

4.  **Tech Stack:** Odoo 19. Remember to add access rights in CSV.✅ Verification Step:
Product: Set a Product to "Business Unit A". Log in as a user who only has access to "Business Unit B". Result: The product should disappear from the list.
Partner: Create a new customer. Check if the state is "Draft".
Phase 3: Sales Transaction MatrixGoal: The core requirement. Injecting the Matrix into the Sales Order.Prompt for Cline:textCopy code[data-radix-scroll-area-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-scroll-area-viewport]::-webkit-scrollbar{display:none}@workspace Phase 3: Sales Transactions.

1.  **Extend `sale.order`:**
    *   Add `ops_branch_id` (Many2one, Required).
    *   Add `ops_business_unit_id` (Many2one, Required).
    *   **Defaults:** These must auto-populate from the current user's `ops_default_branch_id` and `ops_default_business_unit_id`.
    *   **Read-Only:** These fields should be Read-Only for normal salespersons (allow edit only for Managers).

2.  **Partner Validation:**
    *   Override `action_confirm`. Raise a `ValidationError` if the Customer (`partner_id`) is in 'draft' state. Message: "Customer must be Approved by Stewardship team before confirming order."

3.  **Credit Firewall:**
    *   In `action_confirm`, calculate the total due amount of the partner (across all companies/units).
    *   If `total_due + current_order_amount > credit_limit`, block confirmation.

4.  **Tech Stack:** Odoo 19. Use `super()` for overrides.✅ Verification Step:
Create a Quote. Result: Branch/Unit are auto-filled.
Try to Confirm a Quote for a "Draft" partner. Result: Error message appears.
Set a Credit Limit of 100onapartner.Createanorderfor100 on a partner. Create an order for 100onapartner.Createanorderfor200. Result: Error message blocks confirmation.
Phase 4: The Excel Import Wizard (Complex)Goal: Bulk import of lines with strict validation.Prompt for Cline:textCopy code[data-radix-scroll-area-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-scroll-area-viewport]::-webkit-scrollbar{display:none}@workspace Phase 4: Excel Import Wizard.

I need a TransientModel wizard to import SO Lines from Excel.
**Location:** Add a button "Import Lines" in the `sale.order` form header.

**Logic:**
1.  **Input:** Binary field for .xlsx file. Columns: "Section", "Part Number", "Quantity".
2.  **Validation (All-or-Nothing):**
    *   Parse the file using `pandas` or `openpyxl`.
    *   Loop through ALL rows first. Check if "Part Number" exists in the system.
    *   **If ANY part is missing:** Do NOT create any lines. Return a Wizard view listing *every* missing part number (e.g., "Row 4: PN-123 not found").
3.  **Execution:**
    *   If validation passes, create `sale.order.line` records.
    *   Handle "Section" rows (display_type='line_section').
    *   Auto-fetch price from the Order's Pricelist.

4.  **Tech Stack:** Odoo 19. Use `Command.create` for adding lines to the SO.✅ Verification Step:
Create an Excel file with 3 items. Make the 2nd item a fake Part Number.
Run the wizard. Result: It should stop and tell you exactly which part is wrong. It should not add the valid items.
Fix the Excel. Run again. Result: All lines added to the SO.
Phase 5: The Governance Engine (Rules)Goal: Dynamic approval rules based on margin/discount.Prompt for Cline:textCopy code[data-radix-scroll-area-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-scroll-area-viewport]::-webkit-scrollbar{display:none}@workspace Phase 5: Governance Engine.

1.  **New Model `ops.governance.rule`:**
    *   Fields: `name`, `min_margin_percent`, `max_discount_percent`, `active`.
    *   Scope: Apply globally or per Business Unit.

2.  **Sales Integration:**
    *   Add a state `to_approve` to `sale.order` (if not already there, otherwise use Odoo standard).
    *   Override `action_confirm`.
    *   Check the order lines against active Governance Rules.
    *   **Logic:**
        *   If `margin < rule.min_margin`: Move to `to_approve`.
        *   If `discount > rule.max_discount`: Move to `to_approve`.
        *   Else: Proceed to `sale` (Confirmed).

3.  **Tech Stack:** Odoo 19. Ensure margin calculation handles division by zero.✅ Verification Step:
Create a Rule: Max Discount 10%.
Create an Order with 15% discount. Click Confirm.
Result: Order state should be "To Approve" (or similar), not "Sales Order".