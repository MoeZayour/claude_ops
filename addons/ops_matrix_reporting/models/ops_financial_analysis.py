from odoo import models, fields, api


class OpsFinancialAnalysis(models.Model):
    """
    Financial Analysis Report - Read-Only SQL View
    
    This model represents a PostgreSQL materialized view that provides
    high-performance financial analytics with Branch and Business Unit dimensions.
    
    The view joins account_move_line with account_move to provide:
    - Date of journal entry
    - Account information
    - Branch and Business Unit dimensions (from move)
    - Debit/Credit amounts and balance
    - Move status and type
    
    CRITICAL: This model is read-only (_auto=False) and backed by a PostgreSQL view.
    Only posted journal entries from actual invoices/bills are included.
    """
    
    _name = 'ops.financial.analysis'
    _description = 'Financial Analysis by Branch and Business Unit'
    _auto = False  # Don't auto-create table
    _rec_name = 'id'
    _order = 'date DESC'
    
    # ========================================================================
    # FIELDS - Mirror the View Columns
    # ========================================================================
    id = fields.Id(readonly=True)
    
    date = fields.Date(
        string='Entry Date',
        readonly=True,
        help='The accounting date of the journal entry, which determines the fiscal period for reporting. '
             'This is distinct from the transaction date and is used for period-end closing and financial statements. '
             'Use Case: Filter by date range to generate monthly/quarterly/annual financial reports and P&L statements. '
             'Example: "2025-01-01 to 2025-01-31" for January financial results. '
             'Important: Only posted entries (state=posted) are included - draft entries are excluded from this analysis. '
             'Note: This is the move date (account.move.date), not the line date - all lines in a move share the same date. '
             'Related: Combine with ops_branch_id and ops_business_unit_id for multi-dimensional financial analysis.'
    )
    
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        help='The parent journal entry (account move) that contains this line item. '
             'Used to trace back to the source document (invoice, bill, payment, etc.) and view full transaction context. '
             'Use Case: Click to view complete journal entry details including all debit/credit lines and original document reference. '
             'Example: "INV/2025/0001" for customer invoice or "BILL/2025/0001" for vendor bill. '
             'Important: Each move can have multiple lines (debits and credits must balance). '
             'Navigation: From analysis view → move_id → view original invoice/bill with payment status and customer/vendor details. '
             'Related: move_type indicates whether this is a customer invoice, vendor bill, credit note, etc.'
    )
    
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
        help='The General Ledger (GL) account to which this financial transaction is posted. '
             'Accounts are organized in a chart of accounts with categories like Assets, Liabilities, Equity, Revenue, Expenses. '
             'Use Case: Group by account_id to generate trial balance, balance sheet, and income statement reports. '
             'Example: "101000 - Cash" for cash accounts, "400000 - Product Sales" for revenue, "600000 - COGS" for expenses. '
             'Important: Account type determines where it appears in financial statements (BS vs P&L). '
             'Analysis: Use get_account_analysis() to see account balances broken down by branch and BU dimensions. '
             'Related: Filter by account.account_type (asset_receivable, liability_payable, expense, income) for specific report types.'
    )
    
    ops_branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        readonly=True,
        help='The operational branch (location/store) to which this financial transaction is attributed for P&L reporting. '
             'This dimension enables branch-level financial statements including income statements and balance sheets. '
             'Use Case: Generate separate P&L statements per branch to evaluate location profitability and cost centers. '
             'Example: "Branch A: $100K revenue, $80K expenses = $20K profit vs Branch B: $90K revenue, $85K expenses = $5K profit". '
             'Important: Inherited from the parent move (invoice/bill level), not line level - all lines share the branch. '
             'Analysis: Use get_summary_by_branch() for aggregated debits, credits, and net balance per branch. '
             'Security: Users only see financial data from branches they have access to via security rules.'
    )
    
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        readonly=True,
        help='The business unit (product line/division) to which this financial transaction is attributed for divisional P&L. '
             'This dimension enables BU-level financial statements to track divisional profitability independently. '
             'Use Case: Generate separate P&L per BU to evaluate which product lines are profitable and which need strategic changes. '
             'Example: "Electronics BU: $200K revenue, $120K COGS, $50K OpEx = $30K profit. Clothing BU: $150K revenue, $100K COGS, $60K OpEx = -$10K loss". '
             'Important: Combined with ops_branch_id, enables full matrix reporting (Branch × BU P&L grid). '
             'Analysis: Use get_account_analysis() for account-level detail by both branch and BU simultaneously. '
             'Note: Inherited from parent move level for consistency across all lines in the transaction.'
    )
    
    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
    ], string='Move Type', readonly=True,
       help='The transaction type that originated this journal entry, indicating whether it increases or decreases revenue/expenses. '
            'out_invoice: Customer Invoice (increases A/R and revenue). '
            'out_refund: Customer Credit Note (decreases A/R and revenue, issued for returns/corrections). '
            'in_invoice: Vendor Bill (increases A/P and expenses/COGS). '
            'in_refund: Vendor Credit Note (decreases A/P and expenses, received for returns/corrections). '
            'Use Case: Filter by move_type to separate sales analysis (out_*) from procurement analysis (in_*). '
            'Example: "Sum all out_invoice for total revenue, sum all in_invoice for total expenses". '
            'Important: Only these 4 transaction types are included - journal entries, payments, and manual moves are excluded. '
            'Analysis: Use get_receivables_payables_by_dimension() to analyze A/R (out_invoice) and A/P (in_invoice) by branch/BU.')
    
    debit = fields.Float(
        string='Debit',
        readonly=True,
        help='The debit amount for this journal entry line in the company currency. '
             'In double-entry accounting, debits increase Assets and Expenses, decrease Liabilities and Equity. '
             'Use Case: Sum debits by account to see total increases to asset/expense accounts during a period. '
             'Example: "Cash account debits of $50K = cash received from customers". '
             'Important: Debit and Credit always balance in a journal entry - total debits must equal total credits. '
             'Analysis: Debit - Credit = Balance. Positive balance indicates net debit position. '
             'Warning: Currency is always company currency - multi-currency transactions are converted at entry date rate.'
    )
    
    credit = fields.Float(
        string='Credit',
        readonly=True,
        help='The credit amount for this journal entry line in the company currency. '
             'In double-entry accounting, credits increase Liabilities, Equity, and Revenue, decrease Assets. '
             'Use Case: Sum credits by account to see total increases to liability/revenue accounts during a period. '
             'Example: "Sales revenue account credits of $100K = total sales revenue earned". '
             'Important: Every transaction has offsetting debits and credits - they must always balance (sum to zero). '
             'Analysis: Credit - Debit = negative Balance. Net credit position appears as negative balance. '
             'Related: For P&L analysis, revenue accounts show credits (good), expense accounts show debits (costs).'
    )
    
    balance = fields.Float(
        string='Balance',
        readonly=True,
        help='The net balance of this journal entry line, calculated as (debit - credit). '
             'Positive balance = net debit position (Assets/Expenses increase). Negative balance = net credit position (Liabilities/Revenue increase). '
             'Use Case: Sum balances by account to generate Trial Balance report showing net position for each GL account. '
             'Example: "Cash account balance +$10K = net cash increase. Sales revenue balance -$50K = revenue earned (credit normal)". '
             'Important: Balance sign convention: Assets/Expenses positive when growing, Liabilities/Equity/Revenue negative when growing. '
             'Analysis: Group by account_id and sum balance to see net change in each account during reporting period. '
             'Related: For period P&L, sum balances of all expense accounts (positive) and revenue accounts (negative) to calculate profit.'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        help='The business partner (customer or vendor) associated with this financial transaction. '
             'For customer invoices/credits: this is the customer. For vendor bills/credits: this is the supplier. '
             'Use Case: Track accounts receivable per customer and accounts payable per vendor by branch/BU dimensions. '
             'Example: "Customer ABC owes $15K across 3 branches (A/R analysis), Vendor XYZ is owed $8K across 2 BUs (A/P analysis)". '
             'Important: Partner is only populated for A/R and A/P account lines - expense and revenue lines may have null partner. '
             'Analysis: Use get_receivables_payables_by_dimension() to see aged receivables and payables by customer/vendor and dimension. '
             'Related: Cross-reference with sales analysis to see customer profitability (revenue vs payment behavior).'
    )
    
    # ========================================================================
    # SQL VIEW CREATION
    # ========================================================================
    def init(self):
        """
        Create the PostgreSQL view when the model is initialized.
        
        The view:
        1. Joins account_move_line with account_move
        2. Filters for posted entries (state='posted')
        3. Includes only transaction moves (out_invoice, out_refund, in_invoice, in_refund)
        4. Includes Branch and Business Unit dimensions from the move
        5. Optimized for financial analysis and multi-dimensional reporting
        """
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    -- Identification
                    aml.id,
                    aml.move_id,
                    aml.account_id,
                    
                    -- Temporal
                    CAST(am.date AS date) AS date,
                    
                    -- OPS Matrix Dimensions (from move level)
                    am.ops_branch_id,
                    am.ops_business_unit_id,
                    
                    -- Move information
                    am.move_type,
                    am.partner_id,
                    
                    -- Amounts
                    aml.debit,
                    aml.credit,
                    (aml.debit - aml.credit) AS balance
                
                FROM account_move_line aml
                
                INNER JOIN account_move am ON aml.move_id = am.id
                
                WHERE
                    -- Only posted entries
                    am.state = 'posted'
                    -- Only transaction-related moves
                    AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
                    -- Exclude lines with zero balance
                    AND (aml.debit != 0 OR aml.credit != 0)
            )
            """
        )
    
    # ========================================================================
    # STATISTICS & AGGREGATIONS
    # ========================================================================
    @api.model
    def get_summary_by_branch(self):
        """
        Get financial summary grouped by branch.
        
        Returns aggregated financial data by branch:
        - Total debits
        - Total credits
        - Net balance
        - Transaction count
        """
        self.env.cr.execute(
            """
            SELECT
                ops_branch_id,
                COUNT(*) as transaction_count,
                SUM(debit) as total_debits,
                SUM(credit) as total_credits,
                SUM(balance) as net_balance
            FROM ops_financial_analysis
            WHERE ops_branch_id IN (
                SELECT id FROM res_company
                WHERE id IN (
                    SELECT branch_id FROM res_users_ops_allowed_branch_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY ops_branch_id
            ORDER BY net_balance DESC
            """,
            [self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_summary_by_business_unit(self):
        """
        Get financial summary grouped by business unit.
        
        Returns aggregated financial data by BU:
        - Total debits
        - Total credits
        - Net balance
        - Transaction count
        """
        self.env.cr.execute(
            """
            SELECT
                ops_business_unit_id,
                COUNT(*) as transaction_count,
                SUM(debit) as total_debits,
                SUM(credit) as total_credits,
                SUM(balance) as net_balance
            FROM ops_financial_analysis
            WHERE ops_business_unit_id IN (
                SELECT id FROM ops_business_unit
                WHERE id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY ops_business_unit_id
            ORDER BY net_balance DESC
            """,
            [self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_account_analysis(self):
        """
        Get detailed analysis by account, branch, and business unit.
        
        Shows financial position by GL account and dimension:
        - Account balance by dimension
        - Helps identify cost centers and profit centers
        """
        self.env.cr.execute(
            """
            SELECT
                account_id,
                ops_branch_id,
                ops_business_unit_id,
                COUNT(*) as transaction_count,
                SUM(debit) as total_debits,
                SUM(credit) as total_credits,
                SUM(balance) as account_balance
            FROM ops_financial_analysis
            WHERE 
                ops_branch_id IN (
                    SELECT branch_id FROM res_users_ops_allowed_branch_rel
                    WHERE user_id = %s
                )
                AND ops_business_unit_id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            GROUP BY account_id, ops_branch_id, ops_business_unit_id
            ORDER BY account_balance DESC
            """,
            [self.env.uid, self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_receivables_payables_by_dimension(self):
        """
        Get A/R and A/P analysis by dimension.
        
        Shows:
        - Customer receivables by branch/BU
        - Vendor payables by branch/BU
        - Helps manage working capital by dimension
        """
        self.env.cr.execute(
            """
            SELECT
                ops_branch_id,
                ops_business_unit_id,
                move_type,
                partner_id,
                COUNT(*) as transaction_count,
                SUM(balance) as dimension_balance
            FROM ops_financial_analysis
            WHERE 
                move_type IN ('out_invoice', 'in_invoice')
                AND ops_branch_id IN (
                    SELECT branch_id FROM res_users_ops_allowed_branch_rel
                    WHERE user_id = %s
                )
                AND ops_business_unit_id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            GROUP BY ops_branch_id, ops_business_unit_id, move_type, partner_id
            ORDER BY dimension_balance DESC
            """,
            [self.env.uid, self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    # ========================================================================
    # CONSTRAINTS
    # ========================================================================
    @api.model
    def create(self, vals):
        """Prevent creation of records (read-only view)"""
        raise NotImplementedError("This is a read-only view. Records cannot be created.")
    
    def write(self, vals):
        """Prevent modification of records (read-only view)"""
        raise NotImplementedError("This is a read-only view. Records cannot be modified.")
    
    def unlink(self):
        """Prevent deletion of records (read-only view)"""
        raise NotImplementedError("This is a read-only view. Records cannot be deleted.")
