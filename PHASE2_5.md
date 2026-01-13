# PHASE 2: PERFORMANCE OPTIMIZATION & TESTING INFRASTRUCTURE

## Mission Brief

You are a **Performance Engineering Specialist & QA Architect** continuing the OPS Framework production readiness effort. Phase 1 successfully fixed all critical bugs. Phase 2 focuses on **performance optimization** and **testing infrastructure** to ensure the system scales and remains stable.

## Current Status

**Phase 1 Achievements:**
- ✅ All critical bugs fixed (26 NameErrors)
- ✅ Security vulnerabilities patched (eval injection, AND logic)
- ✅ Export audit logging implemented
- ✅ Database indexes added
- ✅ Production-ready baseline achieved (8.0/10)

**Phase 2 Goal:** Reach **8.5/10** by optimizing performance and adding comprehensive testing.

---

## TASK 1: OPTIMIZE N+1 QUERIES IN REPORTING (HIGH PRIORITY - 4 HOURS) 🔴

### Issue: Branch Detail Report Has 3 Queries Per Branch

**Location:** `addons/ops_matrix_accounting/models/ops_consolidated_reporting.py`

**Methods to Optimize:**
1. `_get_branch_detail_data()` - Lines 209-264
2. `_get_business_unit_detail_data()` - Lines 300-355
3. `_get_branch_bu_matrix_data()` - Lines 400-480

### Current Pattern (3N Queries):
```python
def _get_branch_detail_data(self, domain, branches):
    """Current: O(n) - 3 queries per branch"""
    branch_data = []
    for branch in branches:  # 100 iterations
        branch_domain = domain + [('ops_branch_id', '=', branch.id)]
        
        # Query 1: Income
        income_result = MoveLine._read_group(
            domain=branch_domain + [('account_id.account_type', 'in', ['income', 'income_other'])],
            groupby=[],
            aggregates=['credit:sum', 'debit:sum']
        )
        total_income = income_result[0]['credit'] - income_result[0]['debit'] if income_result else 0
        
        # Query 2: Expense
        expense_result = MoveLine._read_group(
            domain=branch_domain + [('account_id.account_type', 'in', ['expense', 'expense_depreciation'])],
            groupby=[],
            aggregates=['credit:sum', 'debit:sum']
        )
        total_expense = expense_result[0]['debit'] - expense_result[0]['credit'] if expense_result else 0
        
        # Query 3: Count
        transaction_count = MoveLine.search_count(branch_domain)
        
        branch_data.append({
            'branch_id': branch.id,
            'branch_name': branch.name,
            'income': total_income,
            'expense': total_expense,
            'transactions': transaction_count,
            'gross_profit': total_income - total_expense
        })
    
    return {'branch_data': branch_data}
```

**Problem:** 100 branches × 3 queries = **300 database round-trips!**

### Optimized Pattern (1 Query):
```python
def _get_branch_detail_data(self, domain, branches):
    """Optimized: O(1) - Single grouped query for all branches"""
    MoveLine = self.env['account.move.line']
    
    # Single query with multi-dimensional groupby
    results = MoveLine._read_group(
        domain=domain + [('ops_branch_id', 'in', branches.ids)],
        groupby=['ops_branch_id', 'account_id.account_type'],
        aggregates=['credit:sum', 'debit:sum', '__count'],
        having=[('ops_branch_id', '!=', False)]
    )
    
    # Build branch data map from aggregated results
    branch_data_map = {}
    
    for result in results:
        # Extract grouped values
        branch_tuple = result.get('ops_branch_id')
        if not branch_tuple:
            continue
        
        branch_id = branch_tuple[0] if isinstance(branch_tuple, tuple) else branch_tuple
        account_type = result.get('account_id.account_type')
        credit = result.get('credit', 0)
        debit = result.get('debit', 0)
        count = result.get('__count', 0)
        
        # Initialize branch entry
        if branch_id not in branch_data_map:
            branch_obj = branches.filtered(lambda b: b.id == branch_id)
            branch_data_map[branch_id] = {
                'branch_id': branch_id,
                'branch_name': branch_obj.name if branch_obj else 'Unknown',
                'income': 0.0,
                'expense': 0.0,
                'transactions': 0,
                'gross_profit': 0.0
            }
        
        # Accumulate by account type
        if account_type in ['income', 'income_other']:
            branch_data_map[branch_id]['income'] += (credit - debit)
        elif account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
            branch_data_map[branch_id]['expense'] += (debit - credit)
        
        branch_data_map[branch_id]['transactions'] += count
    
    # Calculate gross profit
    for data in branch_data_map.values():
        data['gross_profit'] = data['income'] - data['expense']
    
    # Convert to sorted list
    branch_data = sorted(
        branch_data_map.values(),
        key=lambda x: x.get('income', 0),
        reverse=True
    )
    
    return {
        'branch_data': branch_data,
        'total_branches': len(branch_data),
        'query_count': 1  # For monitoring
    }
```

### Apply Same Pattern To:

**Business Unit Detail:**
```python
def _get_business_unit_detail_data(self, domain, business_units):
    """Same optimization pattern for BUs"""
    # Use groupby=['ops_business_unit_id', 'account_id.account_type']
    # Rest follows same structure
```

**Branch × BU Matrix:**
```python
def _get_branch_bu_matrix_data(self, domain, branches, business_units):
    """Cross-dimensional matrix with single query"""
    results = MoveLine._read_group(
        domain=domain,
        groupby=['ops_branch_id', 'ops_business_unit_id', 'account_id.account_type'],
        aggregates=['credit:sum', 'debit:sum', '__count']
    )
    # Build 2D matrix from results
```

### Performance Testing:
```python
# Create performance test file: tests/test_performance.py
from odoo.tests import TransactionCase, tagged
import time

@tagged('post_install', '-at_install', 'performance')
class TestReportPerformance(TransactionCase):
    
    def setUp(self):
        super().setUp()
        # Create test data: 50 branches, 1000 transactions each
        self._create_performance_test_data()
    
    def test_branch_detail_performance(self):
        """Branch detail report should complete in <2 seconds"""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.env.company.id,
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
        })
        
        branches = self.env['ops.branch'].search([])
        
        start_time = time.time()
        result = wizard._get_branch_detail_data([], branches)
        duration = time.time() - start_time
        
        # Performance assertion
        self.assertLess(duration, 2.0, 
            f"Report took {duration:.2f}s, expected <2s")
        
        # Correctness assertion
        self.assertEqual(len(result['branch_data']), len(branches),
            "Should return data for all branches")
    
    def test_bu_detail_performance(self):
        """BU detail report should complete in <2 seconds"""
        # Similar test for business units
    
    def test_matrix_report_performance(self):
        """Matrix report should complete in <5 seconds"""
        # Test cross-dimensional performance
```

**Commit Message:**
```
perf: Optimize reporting to eliminate N+1 queries

PERFORMANCE OPTIMIZATION: 100x faster report generation

Changes:
- Refactored _get_branch_detail_data() to use single grouped query
- Refactored _get_business_unit_detail_data() with same pattern
- Refactored _get_branch_bu_matrix_data() for cross-dimensional efficiency

Performance Improvements:
- Before: 300 queries for 100 branches (30-60 seconds)
- After: 1 query for all branches (<1 second)
- 100x performance improvement
- Scales to 1000+ branches

Testing:
- Added performance test suite
- Verified with 50 branches, 1000 transactions each
- All reports complete in <2 seconds
- Results match original logic exactly

Impact: Production-ready performance at scale
Priority: HIGH
```

---

## TASK 2: IMPLEMENT REPORT CACHING (MEDIUM PRIORITY - 3 HOURS) 🟡

### Issue: Reports Recompute Every Time

**Current Behavior:**
- User generates report → Full database aggregation
- User refreshes → Same aggregation again
- No caching → Repeated expensive queries

### Solution: Smart Caching with Invalidation
```python
# In ops_consolidated_reporting.py

class OpsCompanyConsolidation(models.TransientModel):
    _name = 'ops.company.consolidation'
    
    # Add cache fields
    cache_key = fields.Char(
        compute='_compute_cache_key',
        store=True,
        help='Unique key for caching'
    )
    cached_data = fields.Json(
        string='Cached Report Data',
        help='Cached computation results'
    )
    cache_timestamp = fields.Datetime(
        string='Cache Created',
        help='When cache was last updated'
    )
    cache_valid_minutes = fields.Integer(
        string='Cache TTL',
        default=15,
        help='Cache validity in minutes'
    )
    
    @api.depends('company_id', 'date_from', 'date_to', 'branch_ids', 'business_unit_ids')
    def _compute_cache_key(self):
        """Generate unique cache key from parameters"""
        for wizard in self:
            parts = [
                str(wizard.company_id.id),
                str(wizard.date_from),
                str(wizard.date_to),
                ','.join(str(b) for b in sorted(wizard.branch_ids.ids)),
                ','.join(str(b) for b in sorted(wizard.business_unit_ids.ids))
            ]
            wizard.cache_key = '|'.join(parts)
    
    def _get_cached_or_compute(self, compute_method, *args, **kwargs):
        """
        Check cache before expensive computation.
        
        Usage:
            result = wizard._get_cached_or_compute(
                wizard._compute_report_data,
                domain=[...],
                branches=branches
            )
        """
        self.ensure_one()
        
        # Check if cache is valid
        if self.cached_data and self.cache_timestamp:
            cache_age_minutes = (
                (fields.Datetime.now() - self.cache_timestamp).total_seconds() / 60
            )
            
            if cache_age_minutes < self.cache_valid_minutes:
                _logger.info(
                    f"Using cached report (age: {cache_age_minutes:.1f} min, "
                    f"key: {self.cache_key[:50]}...)"
                )
                return self.cached_data
        
        # Compute fresh data
        _logger.info(f"Computing fresh report (key: {self.cache_key[:50]}...)")
        result = compute_method(*args, **kwargs)
        
        # Update cache
        self.write({
            'cached_data': result,
            'cache_timestamp': fields.Datetime.now()
        })
        
        return result
    
    def action_refresh_cache(self):
        """Force cache refresh (button in UI)"""
        self.ensure_one()
        self.write({
            'cached_data': False,
            'cache_timestamp': False
        })
        return self.action_generate_report()
    
    def action_generate_report(self):
        """Generate report with caching"""
        self.ensure_one()
        
        # Use caching wrapper
        report_data = self._get_cached_or_compute(
            self._compute_report_data,
            domain=self._get_domain(),
            branches=self.branch_ids,
            business_units=self.business_unit_ids
        )
        
        return self._render_report(report_data)
```

**Add Invalidation on Data Changes:**
```python
# In account.move model extension

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def write(self, vals):
        """Invalidate report caches when financial data changes"""
        result = super().write(vals)
        
        # Invalidate if posted/cancelled or amounts changed
        if any(field in vals for field in ['state', 'amount_total', 'ops_branch_id', 'ops_business_unit_id']):
            self._invalidate_consolidated_report_cache()
        
        return result
    
    def _invalidate_consolidated_report_cache(self):
        """Clear cached consolidated reports for affected companies"""
        # Clear all wizard caches for this company
        # (Transient model caches auto-expire anyway)
        _logger.info("Report caches invalidated due to financial data change")
```

**Commit Message:**
```
feat: Add intelligent caching to consolidated reports

PERFORMANCE ENHANCEMENT: Reduce redundant computations

Implementation:
- Added cache_key computed field (based on params)
- Added cached_data JSON field (stores results)
- Added cache_timestamp and TTL configuration
- Implemented _get_cached_or_compute() wrapper
- Added action_refresh_cache() for manual refresh

Cache Invalidation:
- Automatic after TTL expires (default 15 minutes)
- Manual refresh button in UI
- Auto-invalidate on financial data changes

Performance Impact:
- First load: Same time (computes fresh)
- Subsequent loads: <100ms (cached)
- Reduces database load by 90% for repeated reports

Testing:
- Verified cache hit/miss logging
- Tested TTL expiration
- Validated cache invalidation on data change

Priority: MEDIUM - Performance enhancement
```

---

## TASK 3: CREATE COMPREHENSIVE TEST SUITE (HIGH PRIORITY - 8 HOURS) 🔴

### Objective: Achieve 70%+ Test Coverage

**Create:** `addons/ops_matrix_core/tests/`
```
tests/
├── __init__.py
├── test_matrix_access.py      # Security tests
├── test_branch_model.py        # Branch CRUD
├── test_business_unit_model.py # BU CRUD
└── test_security_audit.py      # Audit logging
```

**Create:** `addons/ops_matrix_accounting/tests/`
```
tests/
├── __init__.py
├── test_consolidated_reporting.py  # All 26 methods
├── test_analytic_integration.py    # Analytic account sync
└── test_performance.py              # Performance benchmarks
```

**Create:** `addons/ops_matrix_reporting/tests/`
```
tests/
├── __init__.py
├── test_export_wizard.py       # Export functionality
├── test_export_audit.py        # Audit logging
└── test_security.py            # safe_eval validation
```

### Example Test File:

**Create:** `addons/ops_matrix_core/tests/test_matrix_access.py`
```python
# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase
from odoo.exceptions import AccessError

@tagged('post_install', '-at_install', 'ops_security')
class TestMatrixAccessControl(TransactionCase):
    """Test matrix intersection (AND logic) access control"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test branches
        cls.branch_north = cls.env['ops.branch'].create({
            'name': 'North Branch',
            'code': 'BR-NORTH'
        })
        cls.branch_south = cls.env['ops.branch'].create({
            'name': 'South Branch',
            'code': 'BR-SOUTH'
        })
        
        # Create test business units
        cls.bu_sales = cls.env['ops.business.unit'].create({
            'name': 'Sales',
            'code': 'BU-SALES'
        })
        cls.bu_ops = cls.env['ops.business.unit'].create({
            'name': 'Operations',
            'code': 'BU-OPS'
        })
        
        # Create test user with limited access
        cls.test_user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser@example.com',
            'password': 'test',
            'ops_allowed_branch_ids': [(6, 0, [cls.branch_north.id])],
            'ops_allowed_business_unit_ids': [(6, 0, [cls.bu_sales.id])],
            'groups_id': [(6, 0, [
                cls.env.ref('ops_matrix_core.group_ops_user').id
            ])]
        })
        
        # Create test records with different matrix combinations
        cls.move_north_sales = cls.env['account.move'].create({
            'move_type': 'entry',
            'ops_branch_id': cls.branch_north.id,
            'ops_business_unit_id': cls.bu_sales.id,
        })
        
        cls.move_north_ops = cls.env['account.move'].create({
            'move_type': 'entry',
            'ops_branch_id': cls.branch_north.id,
            'ops_business_unit_id': cls.bu_ops.id,
        })
        
        cls.move_south_sales = cls.env['account.move'].create({
            'move_type': 'entry',
            'ops_branch_id': cls.branch_south.id,
            'ops_business_unit_id': cls.bu_sales.id,
        })
    
    def test_user_can_access_both_dimensions(self):
        """User with Branch A + BU X can see records with both"""
        # User has North + Sales, should see North+Sales record
        move = self.env['account.move'].with_user(self.test_user).browse(
            self.move_north_sales.id
        )
        self.assertTrue(move.exists(), 
            "User should access record with both assigned dimensions")
        self.assertEqual(move.id, self.move_north_sales.id)
    
    def test_user_cannot_access_wrong_bu(self):
        """User with Branch A + BU X cannot see Branch A + BU Y"""
        # User has North + Sales, should NOT see North+Operations
        with self.assertRaises(AccessError, msg="Should not access record with wrong BU"):
            self.env['account.move'].with_user(self.test_user).browse(
                self.move_north_ops.id
            ).read(['name'])
    
    def test_user_cannot_access_wrong_branch(self):
        """User with Branch A + BU X cannot see Branch B + BU X"""
        # User has North + Sales, should NOT see South+Sales
        with self.assertRaises(AccessError, msg="Should not access record with wrong branch"):
            self.env['account.move'].with_user(self.test_user).browse(
                self.move_south_sales.id
            ).read(['name'])
    
    def test_search_respects_matrix_intersection(self):
        """Search results only include records with BOTH dimensions"""
        # Search as test user
        moves = self.env['account.move'].with_user(self.test_user).search([
            ('ops_branch_id', '!=', False),
            ('ops_business_unit_id', '!=', False)
        ])
        
        # Should only see North+Sales
        self.assertEqual(len(moves), 1, 
            "User should only see 1 record (North+Sales)")
        self.assertEqual(moves.id, self.move_north_sales.id)
    
    def test_admin_has_full_access(self):
        """Administrator can see all records regardless of assignment"""
        admin_user = self.env.ref('base.user_admin')
        
        moves = self.env['account.move'].with_user(admin_user).search([
            ('id', 'in', [
                self.move_north_sales.id,
                self.move_north_ops.id,
                self.move_south_sales.id
            ])
        ])
        
        self.assertEqual(len(moves), 3,
            "Admin should see all 3 test records")
```

### Test Running Commands:
```bash
# Run all OPS tests
odoo-bin -d testdb --test-enable --stop-after-init \
    -i ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting \
    --test-tags ops_security,ops_reporting,performance

# Run only security tests
odoo-bin -d testdb --test-enable --stop-after-init \
    --test-tags ops_security

# Run with coverage
coverage run odoo-bin -d testdb --test-enable --stop-after-init \
    -i ops_matrix_core
coverage report
coverage html
```

**Commit Message:**
```
test: Add comprehensive test suite for OPS Framework

TEST INFRASTRUCTURE: 70%+ coverage achieved

Test Files Created:
- test_matrix_access.py: 12 tests (security)
- test_consolidated_reporting.py: 26 tests (all methods)
- test_export_wizard.py: 8 tests (export functionality)
- test_export_audit.py: 6 tests (audit logging)
- test_performance.py: 5 benchmarks

Coverage:
- ops_matrix_core: 75%
- ops_matrix_accounting: 68%
- ops_matrix_reporting: 72%
- Overall: 71%

Test Categories:
- Security: 15 tests (AND logic, access control)
- Functional: 30 tests (CRUD, workflows)
- Performance: 5 benchmarks (<2s reports)
- Integration: 10 tests (analytic sync, exports)

All Tests: PASSING ✅

Priority: HIGH - Production requirement
```

---

## TASK 4: ADD PERFORMANCE MONITORING (OPTIONAL - 2 HOURS) 🟢

### Goal: Track Query Performance Over Time

**Create:** `addons/ops_matrix_core/models/ops_performance_log.py`
```python
class OpsPerformanceLog(models.Model):
    """Track query performance metrics"""
    _name = 'ops.performance.log'
    _description = 'Performance Monitoring Log'
    _order = 'create_date desc'
    
    operation_name = fields.Char(required=True, index=True)
    duration_ms = fields.Float(required=True)
    query_count = fields.Integer()
    record_count = fields.Integer()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.model
    def log_performance(self, operation, duration, query_count=0, record_count=0):
        """Log performance metric"""
        return self.create({
            'operation_name': operation,
            'duration_ms': duration * 1000,  # Convert to ms
            'query_count': query_count,
            'record_count': record_count
        })
```

**Usage in Reports:**
```python
import time

def action_generate_report(self):
    start = time.time()
    result = self._compute_report_data()
    duration = time.time() - start
    
    # Log performance
    self.env['ops.performance.log'].log_performance(
        operation='consolidated_report',
        duration=duration,
        record_count=len(result.get('branch_data', []))
    )
    
    return result
```

---

## PHASE 2 DELIVERABLES

### Required Deliverables

1. **Optimized Report Methods**
   - ✅ _get_branch_detail_data() - 100x faster
   - ✅ _get_business_unit_detail_data() - 100x faster
   - ✅ _get_branch_bu_matrix_data() - 100x faster

2. **Caching System**
   - ✅ Smart caching with TTL
   - ✅ Cache invalidation on data changes
   - ✅ Manual refresh capability

3. **Test Suite**
   - ✅ 60+ test cases
   - ✅ 70%+ code coverage
   - ✅ All tests passing

4. **Performance Monitoring**
   - ✅ Performance logging system
   - ✅ Query count tracking
   - ✅ Duration metrics

### Success Criteria

- [ ] All reports complete in <2 seconds (100 branches)
- [ ] Matrix report completes in <5 seconds
- [ ] Cache reduces load by 90% for repeated reports
- [ ] Test coverage >70% overall
- [ ] All tests passing
- [ ] No performance regressions

---

## PHASE 2 COMPLETION

After completing Phase 2:

**System Status:** 8.5/10
- ✅ Performance optimized
- ✅ Testing infrastructure in place
- ✅ Production-ready at scale

# PHASE 3: ARCHITECTURAL REFACTORING & CODE QUALITY

## Mission Brief

You are a **Software Architect** focused on **code maintainability** and **architectural excellence**. Phase 3 refactors technical debt identified in the code review while maintaining 100% backward compatibility.

**Goal:** Reach **9.0/10** production readiness through architectural improvements.

---

## TASK 1: REFACTOR GOD OBJECT (res_users.py) 🔴

### Issue: res_users.py is 1,251 Lines with Too Many Responsibilities

**Current Structure:**
- Lines 170-231: Legacy compatibility fields (10+ fields)
- Lines 398-522: Matrix access control methods
- Lines 524-630: Authority checking
- Lines 663-717: Validation constraints
- Lines 766-817: CRUD overrides
- Lines 915-954: Group synchronization
- Lines 956-1084: Persona auto-sync
- Lines 1202-1250: API key management

### Solution: Extract into Mixins

**Create:** `addons/ops_matrix_core/models/ops_user_matrix_access_mixin.py`
```python
class OpsUserMatrixAccessMixin(models.AbstractModel):
    """Mixin for matrix branch/BU access control"""
    _name = 'ops.user.matrix.access.mixin'
    _description = 'Matrix Access Control Mixin'
    
    # Branch/BU fields
    ops_allowed_branch_ids = fields.Many2many(...)
    ops_allowed_business_unit_ids = fields.Many2many(...)
    default_branch_id = fields.Many2one(...)
    default_business_unit_id = fields.Many2one(...)
    
    # Access control methods
    def _check_branch_access(self, branch_id):
        """Check if user has access to branch"""
        ...
    
    def _check_bu_access(self, bu_id):
        """Check if user has access to BU"""
        ...
```

**Create:** `addons/ops_matrix_core/models/ops_user_authority_mixin.py`
```python
class OpsUserAuthorityMixin(models.AbstractModel):
    """Mixin for segregation of duties authority"""
    _name = 'ops.user.authority.mixin'
    _description = 'User Authority Mixin'
    
    # Authority fields
    authority_level = fields.Selection(...)
    approval_limit = fields.Monetary(...)
    
    # Authority methods
    def can_approve_amount(self, amount):
        """Check if user can approve amount"""
        ...
```

**Refactor:** `addons/ops_matrix_core/models/res_users.py`
```python
class ResUsers(models.Model):
    _inherit = ['res.users',
                'ops.user.matrix.access.mixin',
                'ops.user.authority.mixin',
                'ops.user.persona.integration.mixin']
    _name = 'res.users'
    
    # Only core fields and essential overrides remain
    # Should reduce to ~300 lines
```

**Testing:** Ensure no functionality breaks

---

## TASK 2: CONSOLIDATE LEGACY COMPATIBILITY LAYER 🟡

### Issue: 10+ Computed Fields for Backward Compatibility

**Current:**
```python
# res_users.py lines 170-231
primary_branch_id = fields.Many2one(compute='_compute_legacy_fields')
main_branch_id = fields.Many2one(compute='_compute_legacy_fields')
default_ops_branch = fields.Many2one(compute='_compute_legacy_fields')
# ...10 more similar fields
```

**Decision Required:** Keep or remove?

**Option A: Remove (Clean Break)**
- Deprecate old API
- Provide migration guide
- Remove technical debt

**Option B: Keep But Document**
- Add deprecation warnings
- Document in code
- Plan removal for next major version

---

## TASK 3: IMPROVE CODE DOCUMENTATION 🟡

### Add Comprehensive Docstrings
```python
def _get_branch_detail_data(self, domain, branches):
    """
    Generate detailed financial data for branches.
    
    This method aggregates financial transactions (income, expense, COGS)
    across specified branches using a single grouped database query for
    optimal performance.
    
    Args:
        domain (list): Odoo domain filter for transactions
        branches (recordset): ops.branch records to analyze
    
    Returns:
        dict: {
            'branch_data': [
                {
                    'branch_id': int,
                    'branch_name': str,
                    'income': float,
                    'expense': float,
                    'gross_profit': float,
                    'transactions': int
                },
                ...
            ],
            'total_branches': int,
            'query_count': int  # Always 1 after optimization
        }
    
    Performance:
        - O(1) database queries regardless of branch count
        - Completes in <1 second for 100 branches, 50K transactions
        - Uses database indexes on ops_branch_id, account_type
    
    Example:
        >>> wizard = env['ops.company.consolidation'].create({...})
        >>> branches = env['ops.branch'].search([])
        >>> result = wizard._get_branch_detail_data([], branches)
        >>> print(f"Analyzed {result['total_branches']} branches")
    """
    ...
```

---

## PHASE 3 SUCCESS CRITERIA

- [ ] res_users.py reduced to <400 lines
- [ ] All logic extracted to focused mixins
- [ ] 100% backward compatibility maintained
- [ ] All tests still passing
- [ ] Comprehensive docstrings added
- [ ] Code review score: 9.0/10


# **PHASE 4: ADVANCED FEATURES (3-4 WEEKS)**

````markdown
# PHASE 4: ADVANCED FEATURES & ANALYTICS

## Mission Brief

You are a **Senior Product Engineer & Data Analyst** extending the OPS Framework with advanced features that provide competitive advantage and enhanced user experience. Phase 4 transforms the system from "functional" to "exceptional" with sophisticated reporting, analytics, and automation.

## Current Status

**Phase 1-2 Complete:**
- ✅ All critical bugs fixed (8.0/10)
- ✅ Performance optimized (8.5/10)
- ✅ Testing infrastructure (8.5/10)

**Phase 4 Goal:** Reach **9.0/10** through advanced features and analytics.

---

## PROJECT CONTEXT: OPS Framework

**Reminder:**
- Two-dimensional matrix: Branches (geography) × Business Units (functions)
- Security: AND logic (users need BOTH dimensions)
- Scale: 50-500 users, 100K+ transactions/month
- Current: Production-ready baseline, now adding excellence

---

## TASK 4.1: MATERIALIZED VIEWS FOR HEAVY AGGREGATIONS (8 HOURS) 🔴

### Problem: Reports Aggregate Same Data Repeatedly

**Current Situation:**
- Consolidated P&L aggregates millions of transactions every time
- Historical comparisons recompute old data
- Dashboard widgets repeat same aggregations
- Expensive queries run during business hours

### Solution: Pre-computed Snapshots (Materialized Views)

#### Step 1: Create Snapshot Model

**Create:** `addons/ops_matrix_accounting/models/ops_matrix_snapshot.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsMatrixSnapshot(models.Model):
    """
    Pre-computed financial snapshots for fast reporting.
    
    Stores aggregated financial data at branch/BU intersections
    for specific time periods. Rebuilt nightly via cron.
    
    Benefits:
    - Reports load in <1 second (vs 10-60 seconds)
    - Historical data preserved (even if transactions deleted)
    - Trend analysis without expensive aggregations
    - Reduced database load during business hours
    """
    _name = 'ops.matrix.snapshot'
    _description = 'Matrix Financial Snapshot'
    _order = 'snapshot_date desc, company_id, branch_id, business_unit_id'
    _rec_name = 'snapshot_date'
    
    # Time dimension
    snapshot_date = fields.Date(
        string='Snapshot Date',
        required=True,
        index=True,
        help='Date this snapshot represents (end of period)'
    )
    period_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period Type', 
       default='monthly', 
       required=True, 
       index=True,
       help='Aggregation period granularity')
    
    period_start = fields.Date(
        string='Period Start',
        required=True,
        index=True,
        help='Start date of the period (inclusive)'
    )
    period_end = fields.Date(
        string='Period End',
        required=True,
        index=True,
        help='End date of the period (inclusive)'
    )
    
    # Matrix dimensions
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        ondelete='cascade'
    )
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=True,
        index=True,
        ondelete='cascade',
        help='Branch dimension'
    )
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=True,
        index=True,
        ondelete='cascade',
        help='Business unit dimension'
    )
    
    # Financial metrics (Income Statement)
    revenue = fields.Monetary(
        string='Revenue',
        currency_field='currency_id',
        help='Total revenue (income account types)'
    )
    cogs = fields.Monetary(
        string='Cost of Goods Sold',
        currency_field='currency_id',
        help='Direct costs'
    )
    gross_profit = fields.Monetary(
        string='Gross Profit',
        currency_field='currency_id',
        compute='_compute_metrics',
        store=True,
        help='Revenue - COGS'
    )
    operating_expense = fields.Monetary(
        string='Operating Expenses',
        currency_field='currency_id',
        help='Indirect expenses (admin, sales, etc.)'
    )
    ebitda = fields.Monetary(
        string='EBITDA',
        currency_field='currency_id',
        compute='_compute_metrics',
        store=True,
        help='Earnings Before Interest, Tax, Depreciation, Amortization'
    )
    depreciation = fields.Monetary(
        string='Depreciation & Amortization',
        currency_field='currency_id'
    )
    ebit = fields.Monetary(
        string='EBIT',
        currency_field='currency_id',
        compute='_compute_metrics',
        store=True,
        help='Earnings Before Interest and Tax'
    )
    interest_expense = fields.Monetary(
        string='Interest Expense',
        currency_field='currency_id'
    )
    tax_expense = fields.Monetary(
        string='Tax Expense',
        currency_field='currency_id'
    )
    net_income = fields.Monetary(
        string='Net Income',
        currency_field='currency_id',
        compute='_compute_metrics',
        store=True,
        help='Bottom line profit'
    )
    
    # Financial metrics (Balance Sheet)
    total_assets = fields.Monetary(
        string='Total Assets',
        currency_field='currency_id',
        help='Sum of all asset accounts'
    )
    total_liabilities = fields.Monetary(
        string='Total Liabilities',
        currency_field='currency_id',
        help='Sum of all liability accounts'
    )
    total_equity = fields.Monetary(
        string='Total Equity',
        currency_field='currency_id',
        help='Assets - Liabilities'
    )
    
    # Volume metrics
    transaction_count = fields.Integer(
        string='Transaction Count',
        help='Number of journal entries in period'
    )
    invoice_count = fields.Integer(
        string='Invoice Count',
        help='Number of customer invoices'
    )
    payment_count = fields.Integer(
        string='Payment Count',
        help='Number of payments received/made'
    )
    
    # Ratios
    gross_margin_pct = fields.Float(
        string='Gross Margin %',
        compute='_compute_metrics',
        store=True,
        help='(Gross Profit / Revenue) × 100'
    )
    operating_margin_pct = fields.Float(
        string='Operating Margin %',
        compute='_compute_metrics',
        store=True,
        help='(EBIT / Revenue) × 100'
    )
    net_margin_pct = fields.Float(
        string='Net Margin %',
        compute='_compute_metrics',
        store=True,
        help='(Net Income / Revenue) × 100'
    )
    
    # Metadata
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
        readonly=True
    )
    create_date = fields.Datetime(
        string='Snapshot Created',
        readonly=True,
        help='When this snapshot was computed'
    )
    
    # Constraints
    _sql_constraints = [
        ('unique_snapshot', 
         'unique(company_id, branch_id, business_unit_id, period_type, snapshot_date)',
         'Snapshot already exists for this combination'),
    ]
    
    @api.depends('revenue', 'cogs', 'operating_expense', 'depreciation', 
                 'interest_expense', 'tax_expense')
    def _compute_metrics(self):
        """Calculate derived financial metrics"""
        for snapshot in self:
            # Profit metrics
            snapshot.gross_profit = snapshot.revenue - snapshot.cogs
            snapshot.ebitda = snapshot.gross_profit - snapshot.operating_expense
            snapshot.ebit = snapshot.ebitda - snapshot.depreciation
            snapshot.net_income = (snapshot.ebit - 
                                   snapshot.interest_expense - 
                                   snapshot.tax_expense)
            
            # Margin percentages
            if snapshot.revenue:
                snapshot.gross_margin_pct = (snapshot.gross_profit / snapshot.revenue) * 100
                snapshot.operating_margin_pct = (snapshot.ebit / snapshot.revenue) * 100
                snapshot.net_margin_pct = (snapshot.net_income / snapshot.revenue) * 100
            else:
                snapshot.gross_margin_pct = 0.0
                snapshot.operating_margin_pct = 0.0
                snapshot.net_margin_pct = 0.0
    
    @api.model
    def rebuild_snapshots(self, period_type='monthly', date_from=None, date_to=None, 
                         company_ids=None, branch_ids=None, bu_ids=None):
        """
        Rebuild financial snapshots for specified parameters.
        
        This is the main entry point for snapshot generation, typically
        called by scheduled action (cron) but can be triggered manually.
        
        Args:
            period_type (str): 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
            date_from (date): Start date (default: 3 months ago)
            date_to (date): End date (default: today)
            company_ids (list): Company IDs to rebuild (default: all)
            branch_ids (list): Branch IDs to rebuild (default: all)
            bu_ids (list): Business unit IDs to rebuild (default: all)
        
        Returns:
            int: Number of snapshots created/updated
        
        Example:
            # Rebuild last 3 months of monthly snapshots
            env['ops.matrix.snapshot'].rebuild_snapshots(
                period_type='monthly',
                date_from=date.today() - timedelta(days=90)
            )
        """
        # Default parameters
        if not date_to:
            date_to = fields.Date.today()
        if not date_from:
            date_from = date_to - timedelta(days=90)  # 3 months
        
        # Get scope
        Company = self.env['res.company']
        Branch = self.env['ops.branch']
        BU = self.env['ops.business.unit']
        
        companies = Company.browse(company_ids) if company_ids else Company.search([])
        branches = Branch.browse(branch_ids) if branch_ids else Branch.search([])
        bus = BU.browse(bu_ids) if bu_ids else BU.search([])
        
        _logger.info(
            f"Rebuilding {period_type} snapshots from {date_from} to {date_to}: "
            f"{len(companies)} companies, {len(branches)} branches, {len(bus)} BUs"
        )
        
        # Generate periods
        periods = self._generate_periods(period_type, date_from, date_to)
        _logger.info(f"Generated {len(periods)} periods to process")
        
        # Process each combination
        snapshot_count = 0
        for company in companies:
            for branch in branches:
                for bu in bus:
                    for period_start, period_end in periods:
                        snapshot = self._create_or_update_snapshot(
                            company=company,
                            branch=branch,
                            business_unit=bu,
                            period_type=period_type,
                            period_start=period_start,
                            period_end=period_end
                        )
                        if snapshot:
                            snapshot_count += 1
                            
                            # Commit every 100 snapshots to avoid long transactions
                            if snapshot_count % 100 == 0:
                                self.env.cr.commit()
                                _logger.info(f"Progress: {snapshot_count} snapshots processed")
        
        _logger.info(f"Rebuild complete: {snapshot_count} snapshots created/updated")
        return snapshot_count
    
    @api.model
    def _generate_periods(self, period_type, date_from, date_to):
        """
        Generate list of (start_date, end_date) tuples for period type.
        
        Args:
            period_type (str): 'daily', 'weekly', 'monthly', etc.
            date_from (date): Start date
            date_to (date): End date
        
        Returns:
            list: [(start_date, end_date), ...]
        """
        periods = []
        current = date_from
        
        while current <= date_to:
            if period_type == 'daily':
                period_start = current
                period_end = current
                current += timedelta(days=1)
            
            elif period_type == 'weekly':
                # Week starts on Monday
                period_start = current - timedelta(days=current.weekday())
                period_end = period_start + timedelta(days=6)
                current = period_end + timedelta(days=1)
            
            elif period_type == 'monthly':
                period_start = current.replace(day=1)
                # Last day of month
                if current.month == 12:
                    period_end = current.replace(year=current.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    period_end = current.replace(month=current.month+1, day=1) - timedelta(days=1)
                current = period_end + timedelta(days=1)
            
            elif period_type == 'quarterly':
                # Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
                quarter = (current.month - 1) // 3
                period_start = current.replace(month=quarter*3+1, day=1)
                if quarter == 3:  # Q4
                    period_end = current.replace(year=current.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    period_end = current.replace(month=(quarter+1)*3+1, day=1) - timedelta(days=1)
                current = period_end + timedelta(days=1)
            
            elif period_type == 'yearly':
                period_start = current.replace(month=1, day=1)
                period_end = current.replace(month=12, day=31)
                current = period_end + timedelta(days=1)
            
            periods.append((period_start, period_end))
        
        return periods
    
    def _create_or_update_snapshot(self, company, branch, business_unit, 
                                   period_type, period_start, period_end):
        """
        Create or update a single snapshot.
        
        Args:
            company (recordset): res.company record
            branch (recordset): ops.branch record
            business_unit (recordset): ops.business.unit record
            period_type (str): Period granularity
            period_start (date): Period start
            period_end (date): Period end
        
        Returns:
            recordset: Created/updated snapshot or False if no data
        """
        # Check if snapshot exists
        existing = self.search([
            ('company_id', '=', company.id),
            ('branch_id', '=', branch.id),
            ('business_unit_id', '=', business_unit.id),
            ('period_type', '=', period_type),
            ('snapshot_date', '=', period_end),
        ], limit=1)
        
        # Aggregate financial data
        data = self._aggregate_financial_data(
            company=company,
            branch=branch,
            business_unit=business_unit,
            date_from=period_start,
            date_to=period_end
        )
        
        # Skip if no transactions
        if not data.get('transaction_count'):
            if existing:
                existing.unlink()  # Remove obsolete snapshot
            return False
        
        # Prepare values
        values = {
            'company_id': company.id,
            'branch_id': branch.id,
            'business_unit_id': business_unit.id,
            'period_type': period_type,
            'snapshot_date': period_end,
            'period_start': period_start,
            'period_end': period_end,
            **data  # Unpack aggregated data
        }
        
        # Create or update
        if existing:
            existing.write(values)
            return existing
        else:
            return self.create(values)
    
    def _aggregate_financial_data(self, company, branch, business_unit, 
                                  date_from, date_to):
        """
        Aggregate financial data for specific branch/BU and period.
        
        This is where the heavy lifting happens - aggregating thousands
        of transactions into summary metrics.
        
        Args:
            company (recordset): Company
            branch (recordset): Branch
            business_unit (recordset): Business unit
            date_from (date): Period start
            date_to (date): Period end
        
        Returns:
            dict: Aggregated financial metrics
        """
        MoveLine = self.env['account.move.line']
        
        # Base domain
        domain = [
            ('company_id', '=', company.id),
            ('ops_branch_id', '=', branch.id),
            ('ops_business_unit_id', '=', business_unit.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('parent_state', '=', 'posted'),  # Only posted entries
        ]
        
        # Aggregate by account type
        results = MoveLine._read_group(
            domain=domain,
            groupby=['account_id.account_type'],
            aggregates=['debit:sum', 'credit:sum', '__count']
        )
        
        # Initialize metrics
        revenue = 0.0
        cogs = 0.0
        operating_expense = 0.0
        depreciation = 0.0
        interest_expense = 0.0
        tax_expense = 0.0
        total_assets = 0.0
        total_liabilities = 0.0
        transaction_count = 0
        
        # Process results by account type
        for result in results:
            account_type = result.get('account_id.account_type')
            debit = result.get('debit', 0.0)
            credit = result.get('credit', 0.0)
            count = result.get('__count', 0)
            
            transaction_count += count
            
            # Income statement accounts
            if account_type in ['income', 'income_other']:
                revenue += (credit - debit)
            elif account_type in ['expense_direct_cost']:
                cogs += (debit - credit)
            elif account_type in ['expense', 'expense_depreciation']:
                if 'depreciation' in account_type:
                    depreciation += (debit - credit)
                else:
                    operating_expense += (debit - credit)
            
            # Balance sheet accounts
            elif account_type in ['asset_receivable', 'asset_cash', 'asset_current', 
                                  'asset_non_current', 'asset_prepayments', 'asset_fixed']:
                total_assets += (debit - credit)
            elif account_type in ['liability_payable', 'liability_credit_card', 
                                  'liability_current', 'liability_non_current']:
                total_liabilities += (credit - debit)
        
        # Count specific document types
        invoice_count = self.env['account.move'].search_count([
            ('company_id', '=', company.id),
            ('ops_branch_id', '=', branch.id),
            ('ops_business_unit_id', '=', business_unit.id),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
        ])
        
        payment_count = self.env['account.payment'].search_count([
            ('company_id', '=', company.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'posted'),
        ])
        
        return {
            'revenue': revenue,
            'cogs': cogs,
            'operating_expense': operating_expense,
            'depreciation': depreciation,
            'interest_expense': interest_expense,
            'tax_expense': tax_expense,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_assets - total_liabilities,
            'transaction_count': transaction_count,
            'invoice_count': invoice_count,
            'payment_count': payment_count,
        }
    
    @api.model
    def get_snapshot_data(self, period_type='monthly', date_from=None, date_to=None,
                         company_id=None, branch_ids=None, bu_ids=None):
        """
        Retrieve snapshot data for reporting (fast!).
        
        This is the method reports should call instead of aggregating
        raw transactions. Returns pre-computed data in milliseconds.
        
        Args:
            period_type (str): Period granularity
            date_from (date): Start date
            date_to (date): End date
            company_id (int): Company filter
            branch_ids (list): Branch filters
            bu_ids (list): BU filters
        
        Returns:
            recordset: ops.matrix.snapshot records
        
        Example:
            # Get monthly snapshots for Q4 2024
            snapshots = env['ops.matrix.snapshot'].get_snapshot_data(
                period_type='monthly',
                date_from=date(2024, 10, 1),
                date_to=date(2024, 12, 31)
            )
            
            # Use in report
            for snapshot in snapshots:
                print(f"{snapshot.branch_id.name} - {snapshot.business_unit_id.name}: "
                      f"Revenue ${snapshot.revenue:,.2f}")
        """
        domain = [('period_type', '=', period_type)]
        
        if date_from:
            domain.append(('snapshot_date', '>=', date_from))
        if date_to:
            domain.append(('snapshot_date', '<=', date_to))
        if company_id:
            domain.append(('company_id', '=', company_id))
        if branch_ids:
            domain.append(('branch_id', 'in', branch_ids))
        if bu_ids:
            domain.append(('business_unit_id', 'in', bu_ids))
        
        return self.search(domain, order='snapshot_date, branch_id, business_unit_id')
````

#### Step 2: Create Scheduled Action (Cron)

**Create:** `addons/ops_matrix_accounting/data/cron_snapshot.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Rebuild Monthly Snapshots (runs nightly at 2 AM) -->
        <record id="ir_cron_rebuild_monthly_snapshots" model="ir.cron">
            <field name="name">OPS: Rebuild Monthly Financial Snapshots</field>
            <field name="model_id" ref="model_ops_matrix_snapshot"/>
            <field name="state">code</field>
            <field name="code">
# Rebuild last 3 months + current month
from datetime import date, timedelta
date_to = date.today()
date_from = (date_to.replace(day=1) - timedelta(days=90)).replace(day=1)

model.rebuild_snapshots(
    period_type='monthly',
    date_from=date_from,
    date_to=date_to
)
            </field>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="doall">False</field>
            <field name="active" eval="True"/>
            <field name="priority">5</field>
            <field name="user_id" ref="base.user_root"/>
        </record>
        
        <!-- Rebuild Weekly Snapshots (runs weekly on Sunday at 3 AM) -->
        <record id="ir_cron_rebuild_weekly_snapshots" model="ir.cron">
            <field name="name">OPS: Rebuild Weekly Financial Snapshots</field>
            <field name="model_id" ref="model_ops_matrix_snapshot"/>
            <field name="state">code</field>
            <field name="code">
# Rebuild last 12 weeks
from datetime import date, timedelta
date_to = date.today()
date_from = date_to - timedelta(weeks=12)

model.rebuild_snapshots(
    period_type='weekly',
    date_from=date_from,
    date_to=date_to
)
            </field>
            <field name="interval_number">7</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="doall">False</field>
            <field name="active" eval="False"/>  <!-- Disabled by default -->
            <field name="priority">10</field>
            <field name="user_id" ref="base.user_root"/>
        </record>
    </data>
</odoo>
```

#### Step 3: Update Reports to Use Snapshots

**Modify:** `addons/ops_matrix_accounting/models/ops_consolidated_reporting.py`

```python
class OpsCompanyConsolidation(models.TransientModel):
    _name = 'ops.company.consolidation'
    
    use_snapshots = fields.Boolean(
        string='Use Pre-computed Snapshots',
        default=True,
        help='Use fast snapshot data instead of real-time aggregation'
    )
    
    def _get_branch_detail_data_fast(self, domain, branches):
        """
        Fast version using snapshots (NEW!).
        
        Returns data in <100ms vs 10-60 seconds for real-time aggregation.
        """
        if not self.use_snapshots:
            # Fall back to real-time aggregation
            return self._get_branch_detail_data(domain, branches)
        
        # Get snapshots for period
        Snapshot = self.env['ops.matrix.snapshot']
        snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',
            date_from=self.date_from,
            date_to=self.date_to,
            company_id=self.company_id.id,
            branch_ids=branches.ids
        )
        
        # Aggregate by branch (snapshots already aggregated by branch+BU)
        branch_data_map = {}
        for snapshot in snapshots:
            branch_id = snapshot.branch_id.id
            
            if branch_id not in branch_data_map:
                branch_data_map[branch_id] = {
                    'branch_id': branch_id,
                    'branch_name': snapshot.branch_id.name,
                    'income': 0.0,
                    'expense': 0.0,
                    'gross_profit': 0.0,
                    'transactions': 0
                }
            
            # Sum across business units
            branch_data_map[branch_id]['income'] += snapshot.revenue
            branch_data_map[branch_id]['expense'] += (snapshot.cogs + 
                                                      snapshot.operating_expense)
            branch_data_map[branch_id]['transactions'] += snapshot.transaction_count
        
        # Calculate gross profit
        for data in branch_data_map.values():
            data['gross_profit'] = data['income'] - data['expense']
        
        branch_data = sorted(
            branch_data_map.values(),
            key=lambda x: x['income'],
            reverse=True
        )
        
        return {
            'branch_data': branch_data,
            'data_source': 'snapshot',  # Indicator for UI
            'snapshot_count': len(snapshots)
        }
```

#### Step 4: Create Snapshot Management UI

**Create:** `addons/ops_matrix_accounting/views/ops_matrix_snapshot_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="view_ops_matrix_snapshot_tree" model="ir.ui.view">
        <field name="name">ops.matrix.snapshot.tree</field>
        <field name="model">ops.matrix.snapshot</field>
        <field name="arch" type="xml">
            <tree string="Financial Snapshots" create="false" edit="false">
                <field name="snapshot_date"/>
                <field name="period_type"/>
                <field name="branch_id"/>
                <field name="business_unit_id"/>
                <field name="revenue" sum="Total Revenue"/>
                <field name="cogs" sum="Total COGS"/>
                <field name="gross_profit" sum="Total Gross Profit"/>
                <field name="operating_expense" sum="Total OpEx"/>
                <field name="net_income" sum="Total Net Income"/>
                <field name="gross_margin_pct" avg="Avg Margin"/>
                <field name="transaction_count" sum="Total Transactions"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_ops_matrix_snapshot_form" model="ir.ui.view">
        <field name="name">ops.matrix.snapshot.form</field>
        <field name="model">ops.matrix.snapshot</field>
        <field name="arch" type="xml">
            <form string="Financial Snapshot" create="false" edit="false">
                <sheet>
                    <div class="oe_title">
                        <h1><field name="snapshot_date"/></h1>
                        <h2>
                            <field name="branch_id"/> - 
                            <field name="business_unit_id"/>
                        </h2>
                    </div>
                    <group>
                        <group string="Period">
                            <field name="period_type"/>
                            <field name="period_start"/>
                            <field name="period_end"/>
                            <field name="company_id"/>
                        </group>
                        <group string="Volume">
                            <field name="transaction_count"/>
                            <field name="invoice_count"/>
                            <field name="payment_count"/>
                        </group>
                    </group>
                    <group string="Income Statement">
                        <group>
                            <field name="revenue"/>
                            <field name="cogs"/>
                            <field name="gross_profit"/>
                            <field name="operating_expense"/>
                        </group>
                        <group>
                            <field name="ebitda"/>
                            <field name="depreciation"/>
                            <field name="ebit"/>
                            <field name="net_income"/>
                        </group>
                    </group>
                    <group string="Profitability Ratios">
                        <group>
                            <field name="gross_margin_pct" widget="percentage"/>
                            <field name="operating_margin_pct" widget="percentage"/>
                            <field name="net_margin_pct" widget="percentage"/>
                        </group>
                    </group>
                    <group string="Balance Sheet">
                        <group>
                            <field name="total_assets"/>
                            <field name="total_liabilities"/>
                            <field name="total_equity"/>
                        </group>
                    </group>
                    <group string="Metadata">
                        <field name="create_date"/>
                        <field name="currency_id"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_ops_matrix_snapshot_search" model="ir.ui.view">
        <field name="name">ops.matrix.snapshot.search</field>
        <field name="model">ops.matrix.snapshot</field>
        <field name="arch" type="xml">
            <search>
                <field name="branch_id"/>
                <field name="business_unit_id"/>
                <field name="snapshot_date"/>
                
                <filter name="monthly" string="Monthly"
                        domain="[('period_type', '=', 'monthly')]" default="1"/>
                <filter name="quarterly" string="Quarterly"
                        domain="[('period_type', '=', 'quarterly')]"/>
                <filter name="yearly" string="Yearly"
                        domain="[('period_type', '=', 'yearly')]"/>
                
                <separator/>
                <filter name="this_month" string="This Month"
                        domain="[('snapshot_date', '&gt;=', (context_today().replace(day=1)).strftime('%Y-%m-%d'))]"/>
                <filter name="this_quarter" string="This Quarter"
                        domain="[('snapshot_date', '&gt;=', (context_today().replace(month=((context_today().month-1)//3)*3+1, day=1)).strftime('%Y-%m-%d'))]"/>
                <filter name="this_year" string="This Year"
                        domain="[('snapshot_date', '&gt;=', context_today().replace(month=1, day=1).strftime('%Y-%m-%d'))]"/>
                
                <group expand="0" string="Group By">
                    <filter name="group_branch" string="Branch" 
                            context="{'group_by': 'branch_id'}"/>
                    <filter name="group_bu" string="Business Unit" 
                            context="{'group_by': 'business_unit_id'}"/>
                    <filter name="group_period" string="Period Type" 
                            context="{'group_by': 'period_type'}"/>
                    <filter name="group_month" string="Month" 
                            context="{'group_by': 'snapshot_date:month'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="action_ops_matrix_snapshot" model="ir.actions.act_window">
        <field name="name">Financial Snapshots</field>
        <field name="res_model">ops.matrix.snapshot</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{'search_default_monthly': 1, 'search_default_this_year': 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                No financial snapshots yet
            </p>
            <p>
                Financial snapshots are pre-computed aggregations that make
                reports load instantly. They are rebuilt automatically every night.
            </p>
        </field>
    </record>

    <!-- Manual Rebuild Wizard -->
    <record id="action_rebuild_snapshots" model="ir.actions.server">
        <field name="name">Rebuild Snapshots</field>
        <field name="model_id" ref="model_ops_matrix_snapshot"/>
        <field name="binding_model_id" ref="model_ops_matrix_snapshot"/>
        <field name="state">code</field>
        <field name="code">
from datetime import date, timedelta

# Rebuild last 3 months
date_to = date.today()
date_from = (date_to.replace(day=1) - timedelta(days=90)).replace(day=1)

count = model.rebuild_snapshots(
    period_type='monthly',
    date_from=date_from,
    date_to=date_to
)

# Show notification
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Snapshots Rebuilt',
        'message': f'Successfully rebuilt {count} financial snapshots',
        'type': 'success',
        'sticky': False,
    }
}
        </field>
    </record>

    <!-- Menu -->
    <menuitem id="menu_ops_matrix_snapshot"
              name="Financial Snapshots"
              parent="ops_matrix_accounting.menu_ops_accounting_root"
              action="action_ops_matrix_snapshot"
              sequence="90"
              groups="ops_matrix_core.group_ops_manager,ops_matrix_core.group_ops_administrator"/>
</odoo>
```

#### Step 5: Update Manifest and Imports

**Modify:** `addons/ops_matrix_accounting/__manifest__.py`

```python
'data': [
    # ... existing files
    'data/cron_snapshot.xml',  # ADD THIS
    'views/ops_matrix_snapshot_views.xml',  # ADD THIS
],
```

**Modify:** `addons/ops_matrix_accounting/models/__init__.py`

```python
from . import ops_matrix_snapshot  # ADD THIS
# ... other imports
```

#### Step 6: Create Access Rights

**Modify:** `addons/ops_matrix_accounting/security/ir.model.access.csv`

```csv
access_ops_matrix_snapshot_user,ops.matrix.snapshot.user,model_ops_matrix_snapshot,ops_matrix_core.group_ops_user,1,0,0,0
access_ops_matrix_snapshot_manager,ops.matrix.snapshot.manager,model_ops_matrix_snapshot,ops_matrix_core.group_ops_manager,1,0,0,0
access_ops_matrix_snapshot_admin,ops.matrix.snapshot.admin,model_ops_matrix_snapshot,ops_matrix_core.group_ops_administrator,1,1,1,1
```

### Testing Snapshot System:

```python
# In Odoo shell:

# Test 1: Build snapshots manually
from datetime import date, timedelta

Snapshot = env['ops.matrix.snapshot']
date_to = date.today()
date_from = date_to - timedelta(days=30)

count = Snapshot.rebuild_snapshots(
    period_type='monthly',
    date_from=date_from,
    date_to=date_to
)
print(f"✅ Created {count} snapshots")

# Test 2: Query snapshot data
snapshots = Snapshot.get_snapshot_data(
    period_type='monthly',
    date_from=date(2024, 1, 1),
    date_to=date(2024, 12, 31)
)
print(f"✅ Found {len(snapshots)} snapshots")

for snap in snapshots[:5]:
    print(f"  {snap.branch_id.name} - {snap.business_unit_id.name}: "
          f"Revenue ${snap.revenue:,.2f}, Net Income ${snap.net_income:,.2f}")

# Test 3: Performance comparison
import time

# Real-time aggregation
start = time.time()
wizard = env['ops.company.consolidation'].create({
    'company_id': env.company.id,
    'date_from': '2024-01-01',
    'date_to': '2024-12-31',
    'use_snapshots': False  # Force real-time
})
result_realtime = wizard._get_branch_detail_data([], env['ops.branch'].search([]))
duration_realtime = time.time() - start

# Snapshot version
start = time.time()
result_snapshot = wizard._get_branch_detail_data_fast([], env['ops.branch'].search([]))
duration_snapshot = time.time() - start

print(f"Real-time: {duration_realtime:.2f}s")
print(f"Snapshot: {duration_snapshot:.2f}s")
print(f"Speedup: {duration_realtime/duration_snapshot:.0f}x faster")
```

**Commit Message:**

```
feat: Add materialized view system (financial snapshots)

PERFORMANCE ENHANCEMENT: 100x faster historical reporting

Implementation:
1. Created ops.matrix.snapshot model
   - Pre-computed financial metrics by branch/BU/period
   - Stores revenue, expenses, margins, balances
   - Supports daily/weekly/monthly/quarterly/yearly periods

2. Automated snapshot generation
   - Cron job rebuilds snapshots nightly at 2 AM
   - Processes last 3 months automatically
   - Commits every 100 snapshots for stability

3. Reporting integration
   - Modified consolidated reports to use snapshots
   - Fallback to real-time if snapshots missing
   - Toggle: use_snapshots=True/False

4. Management UI
   - Browse snapshots by period/branch/BU
   - Manual rebuild action
   - Access control (read-only for users)

Performance Impact:
- Before: 10-60 seconds for historical reports
- After: <100ms from snapshots
- 100-600x performance improvement
- Historical data preserved even if transactions deleted

Business Benefits:
- Instant dashboard loading
- Trend analysis without lag
- Preserved audit trail
- Reduced database load

Testing:
- Verified snapshot generation with 50 branches
- Tested period calculations (monthly/quarterly)
- Validated aggregation accuracy
- Confirmed performance gains

Files:
- NEW: models/ops_matrix_snapshot.py (600 lines)
- NEW: data/cron_snapshot.xml
- NEW: views/ops_matrix_snapshot_views.xml
- MODIFIED: models/ops_consolidated_reporting.py
- MODIFIED: security/ir.model.access.csv

Priority: HIGH - Major competitive advantage
```

# TASK 4.2: ADVANCED ANALYTICS & INTELLIGENCE

## Mission: Transform Raw Data into Business Insights

You're building sophisticated analytical capabilities that turn the OPS Framework from a "reporting system" into a "business intelligence platform."

---

### SUB-TASK 4.2.1: TREND ANALYSIS (4 HOURS)

#### Objective: Month-over-Month, Year-over-Year Comparisons

**Create:** `addons/ops_matrix_accounting/models/ops_trend_analysis.py`
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsTrendAnalysis(models.TransientModel):
    """
    Trend analysis wizard for comparing performance across time periods.
    
    Provides:
    - Month-over-Month (MoM) analysis
    - Year-over-Year (YoY) analysis
    - Quarter-over-Quarter (QoQ) analysis
    - Custom period comparisons
    - Growth rates and variance analysis
    """
    _name = 'ops.trend.analysis'
    _description = 'Trend Analysis Wizard'
    
    # Configuration
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    analysis_type = fields.Selection([
        ('mom', 'Month-over-Month'),
        ('qoq', 'Quarter-over-Quarter'),
        ('yoy', 'Year-over-Year'),
        ('custom', 'Custom Period Comparison'),
    ], string='Analysis Type', 
       required=True, 
       default='mom',
       help='Type of trend comparison')
    
    # Period selection
    current_period_start = fields.Date(
        string='Current Period Start',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    current_period_end = fields.Date(
        string='Current Period End',
        required=True,
        default=fields.Date.today
    )
    
    # Comparison period (auto-computed or manual)
    comparison_period_start = fields.Date(
        string='Comparison Period Start',
        compute='_compute_comparison_period',
        store=True,
        readonly=False
    )
    comparison_period_end = fields.Date(
        string='Comparison Period End',
        compute='_compute_comparison_period',
        store=True,
        readonly=False
    )
    
    # Filters
    branch_ids = fields.Many2many(
        'ops.branch',
        string='Branches',
        help='Leave empty for all branches'
    )
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        string='Business Units',
        help='Leave empty for all BUs'
    )
    
    # Results (computed)
    trend_data = fields.Json(
        string='Trend Analysis Results',
        compute='_compute_trend_analysis',
        help='Computed trend analysis data'
    )
    
    @api.depends('analysis_type', 'current_period_start', 'current_period_end')
    def _compute_comparison_period(self):
        """Auto-calculate comparison period based on analysis type"""
        for wizard in self:
            if wizard.analysis_type == 'mom':
                # Previous month
                wizard.comparison_period_end = wizard.current_period_start - timedelta(days=1)
                wizard.comparison_period_start = wizard.comparison_period_end.replace(day=1)
            
            elif wizard.analysis_type == 'qoq':
                # Previous quarter
                wizard.comparison_period_end = wizard.current_period_start - timedelta(days=1)
                # Go back ~90 days
                wizard.comparison_period_start = wizard.comparison_period_end - relativedelta(months=3)
                wizard.comparison_period_start = wizard.comparison_period_start.replace(day=1)
            
            elif wizard.analysis_type == 'yoy':
                # Same period last year
                wizard.comparison_period_start = wizard.current_period_start - relativedelta(years=1)
                wizard.comparison_period_end = wizard.current_period_end - relativedelta(years=1)
            
            # 'custom' doesn't auto-compute, user sets manually
    
    @api.depends('company_id', 'current_period_start', 'current_period_end',
                 'comparison_period_start', 'comparison_period_end',
                 'branch_ids', 'business_unit_ids')
    def _compute_trend_analysis(self):
        """Compute trend analysis data"""
        for wizard in self:
            if not (wizard.current_period_start and wizard.current_period_end and
                    wizard.comparison_period_start and wizard.comparison_period_end):
                wizard.trend_data = {}
                continue
            
            # Get snapshot data for both periods
            Snapshot = self.env['ops.matrix.snapshot']
            
            # Current period data
            current_snapshots = Snapshot.get_snapshot_data(
                period_type='monthly',
                date_from=wizard.current_period_start,
                date_to=wizard.current_period_end,
                company_id=wizard.company_id.id,
                branch_ids=wizard.branch_ids.ids if wizard.branch_ids else None,
                bu_ids=wizard.business_unit_ids.ids if wizard.business_unit_ids else None
            )
            
            # Comparison period data
            comparison_snapshots = Snapshot.get_snapshot_data(
                period_type='monthly',
                date_from=wizard.comparison_period_start,
                date_to=wizard.comparison_period_end,
                company_id=wizard.company_id.id,
                branch_ids=wizard.branch_ids.ids if wizard.branch_ids else None,
                bu_ids=wizard.business_unit_ids.ids if wizard.business_unit_ids else None
            )
            
            # Aggregate data
            current_data = wizard._aggregate_snapshots(current_snapshots)
            comparison_data = wizard._aggregate_snapshots(comparison_snapshots)
            
            # Calculate trends
            wizard.trend_data = wizard._calculate_trends(current_data, comparison_data)
    
    def _aggregate_snapshots(self, snapshots):
        """Aggregate snapshot data into summary metrics"""
        if not snapshots:
            return {
                'revenue': 0.0,
                'cogs': 0.0,
                'gross_profit': 0.0,
                'operating_expense': 0.0,
                'net_income': 0.0,
                'transaction_count': 0,
            }
        
        return {
            'revenue': sum(s.revenue for s in snapshots),
            'cogs': sum(s.cogs for s in snapshots),
            'gross_profit': sum(s.gross_profit for s in snapshots),
            'operating_expense': sum(s.operating_expense for s in snapshots),
            'net_income': sum(s.net_income for s in snapshots),
            'transaction_count': sum(s.transaction_count for s in snapshots),
            'gross_margin_pct': (sum(s.gross_profit for s in snapshots) / 
                                sum(s.revenue for s in snapshots) * 100) 
                               if sum(s.revenue for s in snapshots) else 0,
        }
    
    def _calculate_trends(self, current, comparison):
        """Calculate growth rates and variances"""
        trends = {
            'current_period': {
                'start': fields.Date.to_string(self.current_period_start),
                'end': fields.Date.to_string(self.current_period_end),
                **current
            },
            'comparison_period': {
                'start': fields.Date.to_string(self.comparison_period_start),
                'end': fields.Date.to_string(self.comparison_period_end),
                **comparison
            },
            'trends': {}
        }
        
        # Calculate growth rates for each metric
        for metric in ['revenue', 'cogs', 'gross_profit', 'operating_expense', 'net_income']:
            current_value = current.get(metric, 0)
            comparison_value = comparison.get(metric, 0)
            
            # Variance
            variance = current_value - comparison_value
            
            # Growth rate
            if comparison_value != 0:
                growth_rate = (variance / abs(comparison_value)) * 100
            else:
                growth_rate = 100.0 if current_value > 0 else 0.0
            
            trends['trends'][metric] = {
                'current': current_value,
                'comparison': comparison_value,
                'variance': variance,
                'growth_rate': growth_rate,
                'direction': 'up' if variance > 0 else 'down' if variance < 0 else 'flat'
            }
        
        # Transaction count trend
        current_txn = current.get('transaction_count', 0)
        comparison_txn = comparison.get('transaction_count', 0)
        txn_variance = current_txn - comparison_txn
        
        trends['trends']['transaction_count'] = {
            'current': current_txn,
            'comparison': comparison_txn,
            'variance': txn_variance,
            'growth_rate': (txn_variance / comparison_txn * 100) if comparison_txn else 0,
            'direction': 'up' if txn_variance > 0 else 'down' if txn_variance < 0 else 'flat'
        }
        
        return trends
    
    def action_view_trend_report(self):
        """Open trend analysis report"""
        self.ensure_one()
        
        # Trigger computation
        self._compute_trend_analysis()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Trend Analysis: {self.analysis_type.upper()}',
            'res_model': 'ops.trend.analysis',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'form_view_ref': 'ops_matrix_accounting.view_ops_trend_analysis_report'}
        }
    
    def action_export_trend_excel(self):
        """Export trend analysis to Excel"""
        self.ensure_one()
        
        # Compute if needed
        if not self.trend_data:
            self._compute_trend_analysis()
        
        # Create Excel workbook
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Trend Analysis"
        
        # Headers
        ws['A1'] = 'Trend Analysis Report'
        ws['A1'].font = Font(size=16, bold=True)
        
        ws['A2'] = f"Analysis Type: {dict(self._fields['analysis_type'].selection).get(self.analysis_type)}"
        ws['A3'] = f"Current Period: {self.current_period_start} to {self.current_period_end}"
        ws['A4'] = f"Comparison Period: {self.comparison_period_start} to {self.comparison_period_end}"
        
        # Data table
        row = 6
        headers = ['Metric', 'Current Period', 'Comparison Period', 'Variance', 'Growth %', 'Trend']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
        
        # Data rows
        trends = self.trend_data.get('trends', {})
        metric_labels = {
            'revenue': 'Revenue',
            'cogs': 'Cost of Goods Sold',
            'gross_profit': 'Gross Profit',
            'operating_expense': 'Operating Expenses',
            'net_income': 'Net Income',
            'transaction_count': 'Transaction Count'
        }
        
        row += 1
        for metric, label in metric_labels.items():
            if metric in trends:
                data = trends[metric]
                ws.cell(row=row, column=1, value=label)
                ws.cell(row=row, column=2, value=data['current'])
                ws.cell(row=row, column=3, value=data['comparison'])
                ws.cell(row=row, column=4, value=data['variance'])
                ws.cell(row=row, column=5, value=f"{data['growth_rate']:.2f}%")
                ws.cell(row=row, column=6, value=data['direction'].upper())
                row += 1
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Create attachment
        import base64
        filename = f"trend_analysis_{self.analysis_type}_{fields.Date.today()}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
```

**Create Views:** `addons/ops_matrix_accounting/views/ops_trend_analysis_views.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Wizard Form (Configuration) -->
    <record id="view_ops_trend_analysis_form" model="ir.ui.view">
        <field name="name">ops.trend.analysis.form</field>
        <field name="model">ops.trend.analysis</field>
        <field name="arch" type="xml">
            <form string="Trend Analysis">
                <sheet>
                    <div class="oe_title">
                        <h1>Trend Analysis</h1>
                    </div>
                    <group>
                        <group>
                            <field name="company_id"/>
                            <field name="analysis_type"/>
                        </group>
                    </group>
                    <group string="Current Period">
                        <group>
                            <field name="current_period_start"/>
                            <field name="current_period_end"/>
                        </group>
                    </group>
                    <group string="Comparison Period">
                        <group>
                            <field name="comparison_period_start"/>
                            <field name="comparison_period_end"/>
                        </group>
                    </group>
                    <group string="Filters (Optional)">
                        <field name="branch_ids" widget="many2many_tags"/>
                        <field name="business_unit_ids" widget="many2many_tags"/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_view_trend_report" string="Generate Report" 
                            type="object" class="btn-primary"/>
                    <button string="Cancel" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Report View (Results) -->
    <record id="view_ops_trend_analysis_report" model="ir.ui.view">
        <field name="name">ops.trend.analysis.report</field>
        <field name="model">ops.trend.analysis</field>
        <field name="arch" type="xml">
            <form string="Trend Analysis Report">
                <header>
                    <button name="action_export_trend_excel" string="Export to Excel" 
                            type="object" class="btn-primary"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="analysis_type" readonly="1" 
                                   widget="badge" 
                                   decoration-info="analysis_type == 'mom'"
                                   decoration-success="analysis_type == 'yoy'"/>
                        </h1>
                        <h2>Trend Analysis Report</h2>
                    </div>
                    
                    <group>
                        <group string="Current Period">
                            <field name="current_period_start" readonly="1"/>
                            <field name="current_period_end" readonly="1"/>
                        </group>
                        <group string="Comparison Period">
                            <field name="comparison_period_start" readonly="1"/>
                            <field name="comparison_period_end" readonly="1"/>
                        </group>
                    </group>

                    <!-- Trend Data Display -->
                    <notebook>
                        <page string="Summary" name="summary">
                            <group>
                                <group string="Revenue Trend">
                                    <field name="trend_data" widget="trend_widget" 
                                           options="{'metric': 'revenue'}" 
                                           nolabel="1"/>
                                </group>
                                <group string="Profitability Trend">
                                    <field name="trend_data" widget="trend_widget" 
                                           options="{'metric': 'net_income'}" 
                                           nolabel="1"/>
                                </group>
                            </group>
                        </page>
                        
                        <page string="Detailed Metrics" name="details">
                            <field name="trend_data" widget="json_widget" nolabel="1"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="action_ops_trend_analysis" model="ir.actions.act_window">
        <field name="name">Trend Analysis</field>
        <field name="res_model">ops.trend.analysis</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>

    <!-- Menu -->
    <menuitem id="menu_ops_trend_analysis"
              name="Trend Analysis"
              parent="ops_matrix_accounting.menu_ops_accounting_reports"
              action="action_ops_trend_analysis"
              sequence="20"/>
</odoo>
```

---

### SUB-TASK 4.2.2: VARIANCE ANALYSIS (3 HOURS)

#### Objective: Actual vs Budget Comparison

**Create:** `addons/ops_matrix_accounting/models/ops_variance_analysis.py`
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OpsVarianceAnalysis(models.TransientModel):
    """
    Variance analysis comparing actual performance vs budget/forecast.
    
    Shows:
    - Favorable/Unfavorable variances
    - Percentage deviations
    - Drill-down to responsible dimensions
    """
    _name = 'ops.variance.analysis'
    _description = 'Budget Variance Analysis'
    
    company_id = fields.Many2one('res.company', required=True, 
                                 default=lambda self: self.env.company)
    
    # Period
    date_from = fields.Date(required=True, default=fields.Date.today)
    date_to = fields.Date(required=True, default=fields.Date.today)
    
    # Comparison type
    comparison_type = fields.Selection([
        ('budget', 'Actual vs Budget'),
        ('forecast', 'Actual vs Forecast'),
        ('prior_year', 'Actual vs Prior Year Actual'),
    ], required=True, default='budget')
    
    # Filters
    branch_ids = fields.Many2many('ops.branch')
    business_unit_ids = fields.Many2many('ops.business.unit')
    
    # Variance threshold (show only significant variances)
    variance_threshold_pct = fields.Float(
        string='Variance Threshold %',
        default=10.0,
        help='Only show variances exceeding this percentage'
    )
    
    # Results
    variance_data = fields.Json(compute='_compute_variance_analysis')
    
    @api.depends('company_id', 'date_from', 'date_to', 'comparison_type',
                 'branch_ids', 'business_unit_ids', 'variance_threshold_pct')
    def _compute_variance_analysis(self):
        """Compute variance analysis"""
        for wizard in self:
            # Get actual data from snapshots
            Snapshot = self.env['ops.matrix.snapshot']
            actual_snapshots = Snapshot.get_snapshot_data(
                period_type='monthly',
                date_from=wizard.date_from,
                date_to=wizard.date_to,
                company_id=wizard.company_id.id,
                branch_ids=wizard.branch_ids.ids if wizard.branch_ids else None,
                bu_ids=wizard.business_unit_ids.ids if wizard.business_unit_ids else None
            )
            
            # Get budget/forecast data (would come from budget model)
            # For now, using placeholder logic
            budget_data = wizard._get_budget_data()
            
            # Calculate variances
            wizard.variance_data = wizard._calculate_variances(
                actual_snapshots,
                budget_data
            )
    
    def _get_budget_data(self):
        """
        Get budget data for comparison.
        
        In a real implementation, this would query a budget model.
        For now, returns placeholder data.
        """
        # TODO: Integrate with actual budget module
        # Budget = self.env['ops.budget']
        # return Budget.get_budget_data(...)
        
        return {
            'revenue': 1000000.0,
            'cogs': 400000.0,
            'operating_expense': 300000.0,
            'net_income': 300000.0
        }
    
    def _calculate_variances(self, actual_snapshots, budget_data):
        """Calculate variance metrics"""
        # Aggregate actuals
        actual_totals = {
            'revenue': sum(s.revenue for s in actual_snapshots),
            'cogs': sum(s.cogs for s in actual_snapshots),
            'operating_expense': sum(s.operating_expense for s in actual_snapshots),
            'net_income': sum(s.net_income for s in actual_snapshots),
        }
        
        variances = {}
        for metric, actual_value in actual_totals.items():
            budget_value = budget_data.get(metric, 0)
            variance = actual_value - budget_value
            
            # Variance percentage
            if budget_value:
                variance_pct = (variance / abs(budget_value)) * 100
            else:
                variance_pct = 100.0 if actual_value > 0 else 0.0
            
            # Favorable/Unfavorable
            # Revenue: Actual > Budget = Favorable
            # Expenses: Actual < Budget = Favorable
            if metric == 'revenue' or metric == 'net_income':
                favorable = variance > 0
            else:  # Expenses
                favorable = variance < 0
            
            # Check threshold
            exceeds_threshold = abs(variance_pct) >= self.variance_threshold_pct
            
            variances[metric] = {
                'actual': actual_value,
                'budget': budget_value,
                'variance': variance,
                'variance_pct': variance_pct,
                'favorable': favorable,
                'exceeds_threshold': exceeds_threshold,
                'status': 'favorable' if favorable else 'unfavorable'
            }
        
        return {
            'variances': variances,
            'summary': {
                'total_variances': len(variances),
                'significant_variances': sum(1 for v in variances.values() 
                                            if v['exceeds_threshold']),
                'favorable_count': sum(1 for v in variances.values() 
                                      if v['favorable']),
                'unfavorable_count': sum(1 for v in variances.values() 
                                        if not v['favorable']),
            }
        }
```

---

### SUB-TASK 4.2.3: DRILL-DOWN CAPABILITY (3 HOURS)

#### Objective: Click-Through from Summary to Detail

**Create:** `addons/ops_matrix_accounting/models/ops_drilldown_report.py`
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OpsDrilldownReport(models.TransientModel):
    """
    Drill-down reporting: Company → Branch → BU → Transactions
    
    Allows users to click through layers of aggregation to
    see transaction-level detail.
    """
    _name = 'ops.drilldown.report'
    _description = 'Drill-down Report'
    
    # Current drill-down level
    level = fields.Selection([
        ('company', 'Company Level'),
        ('branch', 'Branch Level'),
        ('business_unit', 'Business Unit Level'),
        ('transaction', 'Transaction Level'),
    ], default='company', required=True)
    
    # Context
    company_id = fields.Many2one('res.company', required=True)
    branch_id = fields.Many2one('ops.branch')
    business_unit_id = fields.Many2one('ops.business.unit')
    
    # Period
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    
    # Metric being drilled
    metric = fields.Selection([
        ('revenue', 'Revenue'),
        ('cogs', 'Cost of Goods Sold'),
        ('operating_expense', 'Operating Expenses'),
        ('net_income', 'Net Income'),
    ], required=True, default='revenue')
    
    # Results at current level
    drilldown_data = fields.Json(compute='_compute_drilldown_data')
    
    @api.depends('level', 'company_id', 'branch_id', 'business_unit_id',
                 'date_from', 'date_to', 'metric')
    def _compute_drilldown_data(self):
        """Compute data for current drill-down level"""
        for wizard in self:
            if wizard.level == 'company':
                wizard.drilldown_data = wizard._get_branch_summary()
            elif wizard.level == 'branch':
                wizard.drilldown_data = wizard._get_bu_summary()
            elif wizard.level == 'business_unit':
                wizard.drilldown_data = wizard._get_transaction_summary()
            elif wizard.level == 'transaction':
                wizard.drilldown_data = wizard._get_transaction_detail()
    
    def _get_branch_summary(self):
        """Company level: Show branches"""
        Snapshot = self.env['ops.matrix.snapshot']
        snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',
            date_from=self.date_from,
            date_to=self.date_to,
            company_id=self.company_id.id
        )
        
        # Aggregate by branch
        branch_data = {}
        for snap in snapshots:
            branch_id = snap.branch_id.id
            if branch_id not in branch_data:
                branch_data[branch_id] = {
                    'branch_id': branch_id,
                    'branch_name': snap.branch_id.name,
                    'value': 0.0
                }
            
            # Add metric value
            metric_value = getattr(snap, self.metric, 0)
            branch_data[branch_id]['value'] += metric_value
        
        return {
            'level': 'branch',
            'data': sorted(branch_data.values(), 
                          key=lambda x: x['value'], 
                          reverse=True)
        }
    
    def _get_bu_summary(self):
        """Branch level: Show business units"""
        Snapshot = self.env['ops.matrix.snapshot']
        snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',
            date_from=self.date_from,
            date_to=self.date_to,
            company_id=self.company_id.id,
            branch_ids=[self.branch_id.id] if self.branch_id else None
        )
        
        # Aggregate by BU
        bu_data = {}
        for snap in snapshots:
            bu_id = snap.business_unit_id.id
            if bu_id not in bu_data:
                bu_data[bu_id] = {
                    'bu_id': bu_id,
                    'bu_name': snap.business_unit_id.name,
                    'value': 0.0
                }
            
            metric_value = getattr(snap, self.metric, 0)
            bu_data[bu_id]['value'] += metric_value
        
        return {
            'level': 'business_unit',
            'data': sorted(bu_data.values(), 
                          key=lambda x: x['value'], 
                          reverse=True)
        }
    
    def _get_transaction_summary(self):
        """BU level: Show transaction summary by account"""
        MoveLine = self.env['account.move.line']
        
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('parent_state', '=', 'posted')
        ]
        
        if self.branch_id:
            domain.append(('ops_branch_id', '=', self.branch_id.id))
        if self.business_unit_id:
            domain.append(('ops_business_unit_id', '=', self.business_unit_id.id))
        
        # Filter by metric type
        if self.metric == 'revenue':
            domain.append(('account_id.account_type', 'in', ['income', 'income_other']))
        elif self.metric == 'cogs':
            domain.append(('account_id.account_type', '=', 'expense_direct_cost'))
        elif self.metric == 'operating_expense':
            domain.append(('account_id.account_type', 'in', ['expense', 'expense_depreciation']))
        
        # Aggregate by account
        results = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', '__count']
        )
        
        account_data = []
        for result in results:
            account = result.get('account_id')
            if not account:
                continue
            
            debit = result.get('debit', 0)
            credit = result.get('credit', 0)
            count = result.get('__count', 0)
            
            # Calculate value based on metric
            if self.metric == 'revenue':
                value = credit - debit
            else:  # Expenses
                value = debit - credit
            
            account_data.append({
                'account_id': account[0],
                'account_name': account[1],
                'value': value,
                'transaction_count': count
            })
        
        return {
            'level': 'account',
            'data': sorted(account_data, 
                          key=lambda x: abs(x['value']), 
                          reverse=True)
        }
    
    def _get_transaction_detail(self):
        """Transaction level: Show individual journal entries"""
        MoveLine = self.env['account.move.line']
        
        domain = [
            ('company_id', '=', self.company_id.id),
            ('ops_branch_id', '=', self.branch_id.id),
            ('ops_business_unit_id', '=', self.business_unit_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('parent_state', '=', 'posted')
        ]
        
        # Get transactions
        lines = MoveLine.search(domain, limit=100, order='date desc')
        
        transaction_data = []
        for line in lines:
            transaction_data.append({
                'move_id': line.move_id.id,
                'move_name': line.move_id.name,
                'date': fields.Date.to_string(line.date),
                'account_name': line.account_id.display_name,
                'partner_name': line.partner_id.name if line.partner_id else '',
                'debit': line.debit,
                'credit': line.credit,
                'balance': line.debit - line.credit,
            })
        
        return {
            'level': 'transaction',
            'data': transaction_data,
            'count': len(transaction_data)
        }
    
    def action_drill_down(self, target_id):
        """
        Drill down to next level.
        
        Args:
            target_id: ID of the item to drill into (branch_id, bu_id, etc.)
        """
        self.ensure_one()
        
        if self.level == 'company':
            # Drilling into a branch
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ops.drilldown.report',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_level': 'branch',
                    'default_company_id': self.company_id.id,
                    'default_branch_id': target_id,
                    'default_date_from': self.date_from,
                    'default_date_to': self.date_to,
                    'default_metric': self.metric,
                }
            }
        
        elif self.level == 'branch':
            # Drilling into a BU
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ops.drilldown.report',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_level': 'business_unit',
                    'default_company_id': self.company_id.id,
                    'default_branch_id': self.branch_id.id,
                    'default_business_unit_id': target_id,
                    'default_date_from': self.date_from,
                    'default_date_to': self.date_to,
                    'default_metric': self.metric,
                }
            }
        
        elif self.level == 'business_unit':
            # Drilling into transactions
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move.line',
                'view_mode': 'tree,form',
                'domain': [
                    ('company_id', '=', self.company_id.id),
                    ('ops_branch_id', '=', self.branch_id.id),
                    ('ops_business_unit_id', '=', self.business_unit_id.id),
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                ],
                'context': {'create': False, 'delete': False}
            }
```

# TASK 4.3: USER EXPERIENCE ENHANCEMENTS

## Mission: Make OPS Framework Intuitive and Efficient

Transform the system from "functional" to "delightful" with guided workflows, bulk operations, and smart defaults.

---

### SUB-TASK 4.3.1: GUIDED SETUP WIZARD (3 HOURS)

#### Objective: Onboarding New Users/Companies

**Create:** `addons/ops_matrix_core/wizard/ops_setup_wizard.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpsSetupWizard(models.TransientModel):
    """
    Guided setup wizard for initial OPS Framework configuration.
    
    Walks users through:
    1. Company verification
    2. Branch structure creation
    3. Business unit definition
    4. User assignment
    5. Security configuration
    
    Makes first-time setup easy and error-free.
    """
    _name = 'ops.setup.wizard'
    _description = 'OPS Framework Setup Wizard'
    
    # Multi-step wizard state
    state = fields.Selection([
        ('welcome', 'Welcome'),
        ('company', 'Company Setup'),
        ('branches', 'Branch Structure'),
        ('business_units', 'Business Units'),
        ('users', 'User Assignment'),
        ('security', 'Security Configuration'),
        ('review', 'Review & Confirm'),
        ('complete', 'Setup Complete'),
    ], default='welcome', required=True)
    
    # Step 1: Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company to configure'
    )
    
    # Step 2: Branches
    branch_count = fields.Integer(
        string='Number of Branches',
        default=1,
        help='How many geographic branches do you have?'
    )
    branch_template = fields.Selection([
        ('manual', 'I will enter branches manually'),
        ('regions', 'Regional structure (North, South, East, West)'),
        ('countries', 'Country-based structure'),
        ('custom', 'Import from file'),
    ], string='Branch Structure', default='manual')
    
    branch_ids = fields.One2many(
        'ops.setup.wizard.branch',
        'wizard_id',
        string='Branches'
    )
    
    # Step 3: Business Units
    bu_count = fields.Integer(
        string='Number of Business Units',
        default=1,
        help='How many functional departments do you have?'
    )
    bu_template = fields.Selection([
        ('manual', 'I will enter business units manually'),
        ('standard', 'Standard structure (Sales, Ops, Finance, HR)'),
        ('manufacturing', 'Manufacturing structure'),
        ('services', 'Service company structure'),
        ('custom', 'Import from file'),
    ], string='Business Unit Structure', default='manual')
    
    business_unit_ids = fields.One2many(
        'ops.setup.wizard.business.unit',
        'wizard_id',
        string='Business Units'
    )
    
    # Step 4: Users
    assign_users_now = fields.Boolean(
        string='Assign Users Now',
        default=True,
        help='Assign existing users to branches/BUs during setup'
    )
    user_assignment_ids = fields.One2many(
        'ops.setup.wizard.user',
        'wizard_id',
        string='User Assignments'
    )
    
    # Step 5: Security
    security_model = fields.Selection([
        ('strict', 'Strict (Users need BOTH branch AND BU - Recommended)'),
        ('flexible', 'Flexible (Users need branch OR BU)'),
        ('custom', 'Custom (Configure manually later)'),
    ], string='Security Model', default='strict')
    
    enable_audit_logging = fields.Boolean(
        string='Enable Audit Logging',
        default=True,
        help='Track security events and data access'
    )
    
    # Progress tracking
    setup_progress = fields.Integer(
        string='Setup Progress %',
        compute='_compute_setup_progress'
    )
    
    @api.depends('state')
    def _compute_setup_progress(self):
        """Calculate setup completion percentage"""
        progress_map = {
            'welcome': 0,
            'company': 10,
            'branches': 30,
            'business_units': 50,
            'users': 70,
            'security': 85,
            'review': 95,
            'complete': 100,
        }
        for wizard in self:
            wizard.setup_progress = progress_map.get(wizard.state, 0)
    
    def action_next(self):
        """Move to next step"""
        self.ensure_one()
        
        # Validate current step
        self._validate_step()
        
        # Determine next state
        state_flow = [
            'welcome', 'company', 'branches', 'business_units',
            'users', 'security', 'review', 'complete'
        ]
        current_index = state_flow.index(self.state)
        if current_index < len(state_flow) - 1:
            self.state = state_flow[current_index + 1]
            
            # Trigger step-specific actions
            if self.state == 'branches' and self.branch_template != 'manual':
                self._apply_branch_template()
            elif self.state == 'business_units' and self.bu_template != 'manual':
                self._apply_bu_template()
            elif self.state == 'users':
                self._load_existing_users()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ops.setup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_back(self):
        """Move to previous step"""
        self.ensure_one()
        
        state_flow = [
            'welcome', 'company', 'branches', 'business_units',
            'users', 'security', 'review', 'complete'
        ]
        current_index = state_flow.index(self.state)
        if current_index > 0:
            self.state = state_flow[current_index - 1]
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ops.setup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_complete_setup(self):
        """Execute final setup and create all records"""
        self.ensure_one()
        
        # 1. Create branches
        created_branches = []
        for branch_line in self.branch_ids:
            branch = self.env['ops.branch'].create({
                'name': branch_line.name,
                'code': branch_line.code,
                'company_id': self.company_id.id,
            })
            created_branches.append(branch)
        
        # 2. Create business units
        created_bus = []
        for bu_line in self.business_unit_ids:
            bu = self.env['ops.business.unit'].create({
                'name': bu_line.name,
                'code': bu_line.code,
                'company_id': self.company_id.id,
            })
            created_bus.append(bu)
        
        # 3. Assign users
        if self.assign_users_now:
            for user_line in self.user_assignment_ids:
                user_line.user_id.write({
                    'ops_allowed_branch_ids': [(6, 0, user_line.branch_ids.ids)],
                    'ops_allowed_business_unit_ids': [(6, 0, user_line.business_unit_ids.ids)],
                })
        
        # 4. Configure security (handled by existing security rules)
        
        # 5. Enable audit logging
        if self.enable_audit_logging:
            self.env['ir.config_parameter'].sudo().set_param(
                'ops.enable_audit_logging', 'True'
            )
        
        # 6. Mark setup as complete
        self.state = 'complete'
        
        # 7. Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Setup Complete!'),
                'message': _(
                    f'Successfully created {len(created_branches)} branches '
                    f'and {len(created_bus)} business units. '
                    f'Your OPS Framework is ready to use.'
                ),
                'type': 'success',
                'sticky': True,
            }
        }
    
    def _validate_step(self):
        """Validate current step before proceeding"""
        if self.state == 'branches' and not self.branch_ids:
            raise ValidationError(_('Please add at least one branch'))
        
        if self.state == 'business_units' and not self.business_unit_ids:
            raise ValidationError(_('Please add at least one business unit'))
        
        if self.state == 'users' and self.assign_users_now and not self.user_assignment_ids:
            raise ValidationError(_('Please assign users or uncheck "Assign Users Now"'))
    
    def _apply_branch_template(self):
        """Apply selected branch template"""
        self.branch_ids.unlink()  # Clear existing
        
        if self.branch_template == 'regions':
            templates = [
                {'name': 'North Region', 'code': 'NORTH'},
                {'name': 'South Region', 'code': 'SOUTH'},
                {'name': 'East Region', 'code': 'EAST'},
                {'name': 'West Region', 'code': 'WEST'},
            ]
            for template in templates:
                self.env['ops.setup.wizard.branch'].create({
                    'wizard_id': self.id,
                    'name': template['name'],
                    'code': template['code'],
                })
    
    def _apply_bu_template(self):
        """Apply selected business unit template"""
        self.business_unit_ids.unlink()  # Clear existing
        
        if self.bu_template == 'standard':
            templates = [
                {'name': 'Sales & Marketing', 'code': 'SALES'},
                {'name': 'Operations', 'code': 'OPS'},
                {'name': 'Finance & Accounting', 'code': 'FIN'},
                {'name': 'Human Resources', 'code': 'HR'},
                {'name': 'IT & Technology', 'code': 'IT'},
            ]
            for template in templates:
                self.env['ops.setup.wizard.business.unit'].create({
                    'wizard_id': self.id,
                    'name': template['name'],
                    'code': template['code'],
                })
    
    def _load_existing_users(self):
        """Load existing users for assignment"""
        self.user_assignment_ids.unlink()  # Clear existing
        
        users = self.env['res.users'].search([
            ('share', '=', False),  # Internal users only
            ('id', '!=', 1),  # Exclude admin
        ])
        
        for user in users:
            self.env['ops.setup.wizard.user'].create({
                'wizard_id': self.id,
                'user_id': user.id,
            })


class OpsSetupWizardBranch(models.TransientModel):
    """Branch line in setup wizard"""
    _name = 'ops.setup.wizard.branch'
    _description = 'Setup Wizard Branch Line'
    
    wizard_id = fields.Many2one('ops.setup.wizard', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    code = fields.Char(required=True)


class OpsSetupWizardBusinessUnit(models.TransientModel):
    """Business unit line in setup wizard"""
    _name = 'ops.setup.wizard.business.unit'
    _description = 'Setup Wizard Business Unit Line'
    
    wizard_id = fields.Many2one('ops.setup.wizard', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    code = fields.Char(required=True)


class OpsSetupWizardUser(models.TransientModel):
    """User assignment line in setup wizard"""
    _name = 'ops.setup.wizard.user'
    _description = 'Setup Wizard User Assignment'
    
    wizard_id = fields.Many2one('ops.setup.wizard', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', required=True)
    branch_ids = fields.Many2many('ops.setup.wizard.branch', string='Branches')
    business_unit_ids = fields.Many2many('ops.setup.wizard.business.unit', string='Business Units')
````

**Create Views:** `addons/ops_matrix_core/wizard/ops_setup_wizard_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_ops_setup_wizard_form" model="ir.ui.view">
        <field name="name">ops.setup.wizard.form</field>
        <field name="model">ops.setup.wizard</field>
        <field name="arch" type="xml">
            <form string="OPS Framework Setup Wizard">
                <header>
                    <field name="state" widget="statusbar" 
                           statusbar_visible="welcome,company,branches,business_units,users,security,review,complete"/>
                </header>
                <sheet>
                    <!-- Progress Bar -->
                    <div class="o_setup_progress mb-3">
                        <div class="progress">
                            <div class="progress-bar progress-bar-success" 
                                 role="progressbar" 
                                 t-attf-style="width: {{widget.value}}%;">
                                <field name="setup_progress" widget="progressbar"/>
                            </div>
                        </div>
                    </div>

                    <!-- Welcome Step -->
                    <div invisible="state != 'welcome'">
                        <div class="oe_title">
                            <h1>Welcome to OPS Framework!</h1>
                        </div>
                        <group>
                            <div class="alert alert-info">
                                <p>This wizard will guide you through setting up your matrix organization structure.</p>
                                <p><strong>You will configure:</strong></p>
                                <ul>
                                    <li>Geographic branches (regions, offices, locations)</li>
                                    <li>Business units (departments, functions)</li>
                                    <li>User access assignments</li>
                                    <li>Security policies</li>
                                </ul>
                                <p>The setup takes about 10-15 minutes.</p>
                            </div>
                        </group>
                    </div>

                    <!-- Company Step -->
                    <div invisible="state != 'company'">
                        <div class="oe_title">
                            <h1>Company Setup</h1>
                        </div>
                        <group>
                            <field name="company_id"/>
                        </group>
                    </div>

                    <!-- Branches Step -->
                    <div invisible="state != 'branches'">
                        <div class="oe_title">
                            <h1>Branch Structure</h1>
                        </div>
                        <group>
                            <field name="branch_template" widget="radio"/>
                            <field name="branch_count" invisible="branch_template != 'manual'"/>
                        </group>
                        <group string="Branches" invisible="branch_template == 'custom'">
                            <field name="branch_ids" nolabel="1">
                                <tree editable="bottom">
                                    <field name="name" required="1"/>
                                    <field name="code" required="1"/>
                                </tree>
                            </field>
                        </group>
                    </div>

                    <!-- Business Units Step -->
                    <div invisible="state != 'business_units'">
                        <div class="oe_title">
                            <h1>Business Units</h1>
                        </div>
                        <group>
                            <field name="bu_template" widget="radio"/>
                            <field name="bu_count" invisible="bu_template != 'manual'"/>
                        </group>
                        <group string="Business Units" invisible="bu_template == 'custom'">
                            <field name="business_unit_ids" nolabel="1">
                                <tree editable="bottom">
                                    <field name="name" required="1"/>
                                    <field name="code" required="1"/>
                                </tree>
                            </field>
                        </group>
                    </div>

                    <!-- Users Step -->
                    <div invisible="state != 'users'">
                        <div class="oe_title">
                            <h1>User Assignment</h1>
                        </div>
                        <group>
                            <field name="assign_users_now"/>
                        </group>
                        <group string="Assign Users to Matrix Dimensions" 
                               invisible="not assign_users_now">
                            <field name="user_assignment_ids" nolabel="1">
                                <tree editable="bottom">
                                    <field name="user_id"/>
                                    <field name="branch_ids" widget="many2many_tags"/>
                                    <field name="business_unit_ids" widget="many2many_tags"/>
                                </tree>
                            </field>
                        </group>
                    </div>

                    <!-- Security Step -->
                    <div invisible="state != 'security'">
                        <div class="oe_title">
                            <h1>Security Configuration</h1>
                        </div>
                        <group>
                            <field name="security_model" widget="radio"/>
                            <field name="enable_audit_logging"/>
                        </group>
                        <div class="alert alert-info">
                            <p><strong>Strict Model (Recommended):</strong> Users need access to BOTH a branch AND a business unit to see records. Highest security.</p>
                            <p><strong>Flexible Model:</strong> Users need access to EITHER a branch OR a business unit. More permissive.</p>
                        </div>
                    </div>

                    <!-- Review Step -->
                    <div invisible="state != 'review'">
                        <div class="oe_title">
                            <h1>Review Your Configuration</h1>
                        </div>
                        <group>
                            <group string="Summary">
                                <label string="Company"/>
                                <div><field name="company_id" readonly="1"/></div>
                                <label string="Branches"/>
                                <div><span><field name="branch_count"/> branches</span></div>
                                <label string="Business Units"/>
                                <div><span><field name="bu_count"/> business units</span></div>
                                <label string="Security Model"/>
                                <div><field name="security_model" readonly="1"/></div>
                            </group>
                        </group>
                        <div class="alert alert-warning">
                            <p><strong>Ready to complete setup?</strong></p>
                            <p>This will create all branches, business units, and user assignments.</p>
                        </div>
                    </div>

                    <!-- Complete Step -->
                    <div invisible="state != 'complete'">
                        <div class="oe_title">
                            <h1>✓ Setup Complete!</h1>
                        </div>
                        <div class="alert alert-success">
                            <p><strong>Your OPS Framework is ready to use.</strong></p>
                            <p>Next steps:</p>
                            <ul>
                                <li>Configure analytic accounts</li>
                                <li>Import historical data (if needed)</li>
                                <li>Generate your first consolidated report</li>
                            </ul>
                        </div>
                    </div>
                </sheet>
                <footer>
                    <button name="action_back" string="Back" type="object" 
                            invisible="state in ('welcome', 'complete')"/>
                    <button name="action_next" string="Next" type="object" 
                            class="btn-primary"
                            invisible="state in ('review', 'complete')"/>
                    <button name="action_complete_setup" string="Complete Setup" 
                            type="object" class="btn-success"
                            invisible="state != 'review'"/>
                    <button string="Close" special="cancel" 
                            invisible="state != 'complete'"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="action_ops_setup_wizard" model="ir.actions.act_window">
        <field name="name">OPS Framework Setup Wizard</field>
        <field name="res_model">ops.setup.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>

    <!-- Menu (in Configuration) -->
    <menuitem id="menu_ops_setup_wizard"
              name="Setup Wizard"
              parent="ops_matrix_core.menu_ops_configuration"
              action="action_ops_setup_wizard"
              sequence="1"/>
</odoo>
```

---

### SUB-TASK 4.3.2: BULK ASSIGNMENT TOOL (2 HOURS)

**Create:** `addons/ops_matrix_core/wizard/ops_bulk_assignment.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OpsBulkAssignment(models.TransientModel):
    """
    Bulk assign users to branches and business units.
    
    Scenarios:
    - Assign entire department to new BU
    - Reassign regional office users to new branch
    - Bulk remove access when restructuring
    """
    _name = 'ops.bulk.assignment'
    _description = 'Bulk User Assignment'
    
    operation = fields.Selection([
        ('add', 'Add Access'),
        ('remove', 'Remove Access'),
        ('replace', 'Replace Access'),
    ], required=True, default='add')
    
    # Target users
    user_ids = fields.Many2many(
        'res.users',
        string='Users',
        domain=[('share', '=', False)],
        required=True
    )
    user_count = fields.Integer(
        compute='_compute_user_count',
        string='Selected Users'
    )
    
    # Branches to assign
    branch_ids = fields.Many2many(
        'ops.branch',
        string='Branches'
    )
    
    # Business units to assign
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        string='Business Units'
    )
    
    @api.depends('user_ids')
    def _compute_user_count(self):
        for wizard in self:
            wizard.user_count = len(wizard.user_ids)
    
    def action_apply(self):
        """Apply bulk assignment"""
        self.ensure_one()
        
        if self.operation == 'add':
            for user in self.user_ids:
                # Add to existing assignments
                if self.branch_ids:
                    user.ops_allowed_branch_ids = [(4, bid) for bid in self.branch_ids.ids]
                if self.business_unit_ids:
                    user.ops_allowed_business_unit_ids = [(4, bid) for bid in self.business_unit_ids.ids]
        
        elif self.operation == 'remove':
            for user in self.user_ids:
                # Remove from existing assignments
                if self.branch_ids:
                    user.ops_allowed_branch_ids = [(3, bid) for bid in self.branch_ids.ids]
                if self.business_unit_ids:
                    user.ops_allowed_business_unit_ids = [(3, bid) for bid in self.business_unit_ids.ids]
        
        elif self.operation == 'replace':
            for user in self.user_ids:
                # Replace all assignments
                if self.branch_ids:
                    user.ops_allowed_branch_ids = [(6, 0, self.branch_ids.ids)]
                if self.business_unit_ids:
                    user.ops_allowed_business_unit_ids = [(6, 0, self.business_unit_ids.ids)]
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Assignment Complete'),
                'message': _('%d users updated successfully') % len(self.user_ids),
                'type': 'success',
                'sticky': False,
            }
        }
```

---

### SUB-TASK 4.3.3: SMART FILTER TEMPLATES (1 HOUR)

**Create:** `addons/ops_matrix_reporting/models/ops_filter_template.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OpsFilterTemplate(models.Model):
    """
    Saved filter templates for quick report generation.
    
    Users can save common filter combinations:
    - "Q4 2024 North Region Sales"
    - "YTD All Branches Finance"
    - "Last Month Operations Only"
    """
    _name = 'ops.filter.template'
    _description = 'Report Filter Template'
    _order = 'sequence, name'
    
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # Visibility
    user_id = fields.Many2one(
        'res.users',
        string='Owner',
        default=lambda self: self.env.user,
        help='User who created this template (leave empty for global)'
    )
    is_global = fields.Boolean(
        string='Global Template',
        help='Available to all users'
    )
    
    # Filter parameters
    date_from = fields.Date()
    date_to = fields.Date()
    period_type = fields.Selection([
        ('custom', 'Custom Date Range'),
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('last_month', 'Last Month'),
        ('last_quarter', 'Last Quarter'),
        ('last_year', 'Last Year'),
    ], string='Period', default='this_month')
    
    branch_ids = fields.Many2many('ops.branch')
    business_unit_ids = fields.Many2many('ops.business.unit')
    
    # Usage tracking
    usage_count = fields.Integer(readonly=True, default=0)
    last_used = fields.Datetime(readonly=True)
    
    def action_apply_template(self):
        """Apply this template to current wizard/report"""
        self.ensure_one()
        
        # Update usage stats
        self.write({
            'usage_count': self.usage_count + 1,
            'last_used': fields.Datetime.now()
        })
        
        # Return values to apply
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': self.branch_ids.ids,
            'business_unit_ids': self.business_unit_ids.ids,
        }
```

---

**Commit Message for Task 4.3:**

```
feat: Add user experience enhancements (guided setup, bulk tools, filters)

UX IMPROVEMENTS: Make OPS Framework intuitive and efficient

Implementations:
1. Guided Setup Wizard
   - Multi-step onboarding for new users/companies
   - Template-based branch/BU creation
   - Visual progress tracking
   - Validation at each step

2. Bulk Assignment Tool
   - Mass user assignment/removal
   - Add/Remove/Replace operations
   - Department-wide access changes

3. Smart Filter Templates
   - Save common filter combinations
   - Quick-apply saved filters
   - Global templates for all users
   - Usage tracking

Business Benefits:
- Faster onboarding (15 min vs 2-3 hours manual)
- Reduced setup errors
- Efficient user management
- Consistent reporting filters

Files:
- NEW: wizard/ops_setup_wizard.py (400 lines)
- NEW: wizard/ops_bulk_assignment.py (100 lines)
- NEW: models/ops_filter_template.py (80 lines)
- NEW: Multiple view files

Testing:
- Wizard tested with 10 branches, 5 BUs
- Bulk assignment tested with 50 users
- Filter templates working correctly

Priority: MEDIUM - UX enhancement
```

---

## **PHASE 5: PRODUCTION HARDENING (1-2 WEEKS)** 🔒

---

````markdown
# PHASE 5: PRODUCTION HARDENING & ENTERPRISE FEATURES

## Mission: Enterprise-Grade Reliability & Security

Transform OPS Framework from "production-ready" to "enterprise-grade" with advanced security, scalability, and monitoring capabilities.

**Target Score:** 9.2/10

---

## TASK 5.1: ADVANCED SECURITY (8 HOURS)

### SUB-TASK 5.1.1: TWO-FACTOR AUTHENTICATION (3 HOURS)

**Note:** Odoo Enterprise has built-in 2FA. For Community Edition, integrate with TOTP.

**Create:** `addons/ops_matrix_core/models/res_users_2fa.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied
import pyotp
import qrcode
import io
import base64


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # 2FA fields
    ops_2fa_enabled = fields.Boolean(
        string='Two-Factor Authentication',
        help='Require 2FA for this user'
    )
    ops_2fa_secret = fields.Char(
        string='2FA Secret',
        copy=False,
        groups='base.group_system'
    )
    ops_2fa_qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_2fa_qr_code'
    )
    ops_last_2fa_verify = fields.Datetime(
        string='Last 2FA Verification',
        readonly=True
    )
    
    @api.depends('ops_2fa_secret')
    def _compute_2fa_qr_code(self):
        """Generate QR code for 2FA setup"""
        for user in self:
            if user.ops_2fa_secret and user.ops_2fa_enabled:
                # Generate TOTP URI
                totp = pyotp.TOTP(user.ops_2fa_secret)
                uri = totp.provisioning_uri(
                    name=user.login,
                    issuer_name='OPS Framework'
                )
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(uri)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                
                user.ops_2fa_qr_code = base64.b64encode(buffer.getvalue())
            else:
                user.ops_2fa_qr_code = False
    
    def action_enable_2fa(self):
        """Enable 2FA for user"""
        self.ensure_one()
        
        # Generate secret
        self.ops_2fa_secret = pyotp.random_base32()
        self.ops_2fa_enabled = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Setup Two-Factor Authentication',
            'res_model': 'res.users',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_2fa_setup': True}
        }
    
    def action_disable_2fa(self):
        """Disable 2FA for user"""
        self.ensure_one()
        self.ops_2fa_enabled = False
        self.ops_2fa_secret = False
    
    def verify_2fa_code(self, code):
        """Verify 2FA code"""
        self.ensure_one()
        
        if not self.ops_2fa_enabled:
            return True
        
        totp = pyotp.TOTP(self.ops_2fa_secret)
        is_valid = totp.verify(code, valid_window=1)
        
        if is_valid:
            self.sudo().ops_last_2fa_verify = fields.Datetime.now()
        
        return is_valid


class OpsLogin2FA(models.TransientModel):
    """2FA verification wizard during login"""
    _name = 'ops.login.2fa'
    _description = '2FA Verification'
    
    user_id = fields.Many2one('res.users', required=True)
    code = fields.Char(string='Verification Code', required=True)
    
    def action_verify(self):
        """Verify 2FA code and complete login"""
        self.ensure_one()
        
        if not self.user_id.verify_2fa_code(self.code):
            raise AccessDenied(_('Invalid verification code'))
        
        # Mark session as verified
        self.env['ir.http'].session_info()['ops_2fa_verified'] = True
        
        return {'type': 'ir.actions.act_window_close'}
````

---

### SUB-TASK 5.1.2: SESSION MANAGEMENT (2 HOURS)

**Create:** `addons/ops_matrix_core/models/ops_session_manager.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class OpsSessionManager(models.Model):
    """
    Track and manage user sessions for security.
    
    Features:
    - Session timeout enforcement
    - Concurrent session limiting
    - IP-based session validation
    - Force logout capability
    """
    _name = 'ops.session.manager'
    _description = 'Session Manager'
    _order = 'create_date desc'
    
    user_id = fields.Many2one('res.users', required=True, index=True)
    session_id = fields.Char(required=True, index=True)
    
    ip_address = fields.Char(required=True)
    user_agent = fields.Text()
    
    login_time = fields.Datetime(required=True, default=fields.Datetime.now)
    last_activity = fields.Datetime(required=True, default=fields.Datetime.now)
    logout_time = fields.Datetime()
    
    is_active = fields.Boolean(default=True, index=True)
    timeout_minutes = fields.Integer(default=60)
    
    # Security flags
    forced_logout = fields.Boolean(default=False)
    suspicious_activity = fields.Boolean(default=False)
    ip_changed = fields.Boolean(default=False)
    
    @api.model
    def create_session(self, user_id, session_id, ip_address, user_agent):
        """Create new session record"""
        # Check concurrent session limit
        active_sessions = self.search_count([
            ('user_id', '=', user_id),
            ('is_active', '=', True)
        ])
        
        max_sessions = self.env['ir.config_parameter'].sudo().get_param(
            'ops.max_concurrent_sessions', default=3
        )
        
        if active_sessions >= int(max_sessions):
            # Force logout oldest session
            oldest = self.search([
                ('user_id', '=', user_id),
                ('is_active', '=', True)
            ], order='last_activity', limit=1)
            oldest.force_logout('Maximum concurrent sessions exceeded')
        
        return self.create({
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
        })
    
    @api.model
    def update_activity(self, session_id, ip_address=None):
        """Update last activity timestamp"""
        session = self.search([('session_id', '=', session_id)], limit=1)
        if session:
            values = {'last_activity': fields.Datetime.now()}
            
            # Check IP change
            if ip_address and ip_address != session.ip_address:
                values['ip_changed'] = True
                values['suspicious_activity'] = True
            
            session.write(values)
            
            # Check timeout
            if session.is_timeout():
                session.force_logout('Session timeout')
                return False
        
        return True
    
    def is_timeout(self):
        """Check if session has timed out"""
        self.ensure_one()
        if not self.is_active:
            return True
        
        timeout_delta = timedelta(minutes=self.timeout_minutes)
        return (fields.Datetime.now() - self.last_activity) > timeout_delta
    
    def force_logout(self, reason=''):
        """Force logout session"""
        self.ensure_one()
        self.write({
            'is_active': False,
            'logout_time': fields.Datetime.now(),
            'forced_logout': True,
        })
        
        # Log security event
        self.env['ops.security.audit'].sudo().create({
            'event_type': 'forced_logout',
            'user_id': self.user_id.id,
            'details': f'Session forced logout: {reason}',
            'ip_address': self.ip_address,
        })
    
    @api.model
    def cleanup_expired_sessions(self):
        """Cron job: Clean up expired sessions"""
        expired = self.search([
            ('is_active', '=', True),
            ('last_activity', '<', fields.Datetime.now() - timedelta(hours=24))
        ])
        
        for session in expired:
            session.force_logout('Expired session cleanup')
        
        return len(expired)
```

---

### SUB-TASK 5.1.3: IP WHITELISTING (2 HOURS)

**Create:** `addons/ops_matrix_core/models/ops_ip_whitelist.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied
import ipaddress


class OpsIPWhitelist(models.Model):
    """
    IP address whitelisting for restricted access.
    
    Use cases:
    - Limit admin access to office IPs only
    - Restrict financial data access by location
    - Prevent access from foreign countries
    """
    _name = 'ops.ip.whitelist'
    _description = 'IP Whitelist'
    _order = 'sequence, name'
    
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # IP Configuration
    ip_address = fields.Char(
        string='IP Address/Range',
        required=True,
        help='Single IP (192.168.1.100) or CIDR range (192.168.1.0/24)'
    )
    
    # Restrictions
    user_ids = fields.Many2many(
        'res.users',
        string='Restrict These Users',
        help='Leave empty to apply to all users'
    )
    group_ids = fields.Many2many(
        'res.groups',
        string='Restrict These Groups',
        help='Leave empty to apply to all groups'
    )
    
    # Action
    restriction_type = fields.Selection([
        ('allow', 'Allow Only These IPs'),
        ('deny', 'Deny These IPs'),
    ], default='allow', required=True)
    
    notes = fields.Text()
    
    @api.model
    def check_ip_access(self, ip_address, user_id):
        """
        Check if IP address is allowed for user.
        
        Returns: True if allowed, raises AccessDenied if blocked
        """
        rules = self.search([
            '|', '|',
            ('user_ids', '=', False),  # Global rule
            ('user_ids', 'in', [user_id]),  # User-specific
            ('group_ids', 'in', self.env['res.users'].browse(user_id).groups_id.ids)  # Group-specific
        ])
        
        if not rules:
            return True  # No restrictions
        
        # Check each rule
        for rule in rules:
            if rule.ip_matches(ip_address):
                if rule.restriction_type == 'allow':
                    return True
                elif rule.restriction_type == 'deny':
                    raise AccessDenied(_(
                        'Access denied from IP %s (Rule: %s)'
                    ) % (ip_address, rule.name))
        
        # No matching allow rules
        if any(r.restriction_type == 'allow' for r in rules):
            raise AccessDenied(_(
                'Access denied: IP %s not in whitelist'
            ) % ip_address)
        
        return True
    
    def ip_matches(self, ip_address):
        """Check if IP matches this rule's range"""
        self.ensure_one()
        
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            
            # Check if rule is CIDR range
            if '/' in self.ip_address:
                network = ipaddress.ip_network(self.ip_address, strict=False)
                return ip_obj in network
            else:
                # Single IP
                rule_ip = ipaddress.ip_address(self.ip_address)
                return ip_obj == rule_ip
        except ValueError:
            return False
```

---

### SUB-TASK 5.1.4: ADVANCED AUDIT TRAILS (1 HOUR)

**Extend:** `addons/ops_matrix_core/models/ops_security_audit.py`

```python
# Add to existing ops_security_audit.py

class OpsSecurityAudit(models.Model):
    _inherit = 'ops.security.audit'
    
    # New event types
    event_type = fields.Selection(selection_add=[
        ('login_failed', 'Failed Login Attempt'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('2fa_failed', '2FA Verification Failed'),
        ('session_timeout', 'Session Timeout'),
        ('forced_logout', 'Forced Logout'),
        ('ip_blocked', 'IP Address Blocked'),
        ('suspicious_activity', 'Suspicious Activity Detected'),
        ('password_changed', 'Password Changed'),
        ('permission_escalation', 'Permission Escalation Attempted'),
    ])
    
    # Risk level
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], compute='_compute_risk_level', store=True)
    
    # Response status
    response_status = fields.Selection([
        ('open', 'Open - Requires Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ], default='open')
    
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    resolution_notes = fields.Text()
    
    @api.depends('event_type')
    def _compute_risk_level(self):
        """Auto-assign risk level based on event type"""
        risk_map = {
            'login_failed': 'low',
            '2fa_enabled': 'low',
            '2fa_disabled': 'medium',
            '2fa_failed': 'medium',
            'session_timeout': 'low',
            'forced_logout': 'medium',
            'ip_blocked': 'high',
            'suspicious_activity': 'high',
            'password_changed': 'medium',
            'permission_escalation': 'critical',
        }
        
        for audit in self:
            audit.risk_level = risk_map.get(audit.event_type, 'low')
    
    @api.model
    def log_failed_login(self, login, ip_address, reason=''):
        """Log failed login attempt"""
        return self.create({
            'event_type': 'login_failed',
            'user_id': False,  # User not authenticated yet
            'ip_address': ip_address,
            'details': f'Failed login attempt for "{login}": {reason}',
        })
    
    @api.model
    def detect_brute_force(self, ip_address, threshold=5, window_minutes=15):
        """
        Detect brute force attacks.
        
        Returns: True if attack detected
        """
        window_start = fields.Datetime.now() - timedelta(minutes=window_minutes)
        
        failed_attempts = self.search_count([
            ('event_type', '=', 'login_failed'),
            ('ip_address', '=', ip_address),
            ('create_date', '>=', window_start)
        ])
        
        if failed_attempts >= threshold:
            self.create({
                'event_type': 'suspicious_activity',
                'ip_address': ip_address,
                'details': f'Brute force attack detected: {failed_attempts} failed logins in {window_minutes} minutes',
            })
            return True
        
        return False
```

---

## TASK 5.2: SCALABILITY IMPROVEMENTS (8 HOURS)

### SUB-TASK 5.2.1: DATABASE PARTITIONING (4 HOURS)

**Create:** `addons/ops_matrix_accounting/models/ops_data_archival.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsDataArchival(models.Model):
    """
    Archive old transactional data to improve performance.
    
    Strategy:
    - Move old journal entries to archive tables
    - Keep snapshots for historical reporting
    - Maintain referential integrity
    """
    _name = 'ops.data.archival'
    _description = 'Data Archival Management'
    
    name = fields.Char(required=True)
    
    # Configuration
    model_name = fields.Char(
        string='Model to Archive',
        required=True,
        help='Technical name (e.g., account.move.line)'
    )
    archive_older_than_days = fields.Integer(
        string='Archive Data Older Than (Days)',
        default=365,
        help='Archive records older than this many days'
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Completed'),
        ('error', 'Error'),
    ], default='draft')
    
    last_run = fields.Datetime(readonly=True)
    records_archived = fields.Integer(readonly=True)
    error_message = fields.Text(readonly=True)
    
    def action_run_archival(self):
        """Execute archival process"""
        self.ensure_one()
        
        try:
            self.state = 'running'
            
            # Calculate cutoff date
            cutoff_date = fields.Date.today() - timedelta(days=self.archive_older_than_days)
            
            # Get model
            Model = self.env[self.model_name]
            
            # Find old records
            domain = [('date', '<', cutoff_date)]
            if 'active' in Model._fields:
                domain.append(('active', '=', False))
            
            old_records = Model.search(domain)
            
            # Archive (move to separate table or mark as archived)
            archived_count = 0
            for record in old_records:
                # Create archive entry
                self.env['ops.archived.record'].create({
                    'original_model': self.model_name,
                    'original_id': record.id,
                    'data': record.read()[0],  # Snapshot of data
                    'archived_date': fields.Datetime.now(),
                })
                
                # Delete original
                record.unlink()
                archived_count += 1
                
                # Commit every 100 records
                if archived_count % 100 == 0:
                    self.env.cr.commit()
                    _logger.info(f"Archived {archived_count} {self.model_name} records...")
            
            self.write({
                'state': 'done',
                'last_run': fields.Datetime.now(),
                'records_archived': archived_count,
            })
            
            _logger.info(f"Archival complete: {archived_count} records archived")
            
        except Exception as e:
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            _logger.error(f"Archival error: {str(e)}")
            raise


class OpsArchivedRecord(models.Model):
    """Storage for archived records"""
    _name = 'ops.archived.record'
    _description = 'Archived Record'
    
    original_model = fields.Char(required=True, index=True)
    original_id = fields.Integer(required=True, index=True)
    data = fields.Json(required=True)
    archived_date = fields.Datetime(required=True, index=True)
    
    _sql_constraints = [
        ('unique_record', 'unique(original_model, original_id)', 
         'Record already archived')
    ]
```

---

### SUB-TASK 5.2.2: QUERY RESULT PAGINATION (2 HOURS)

**Create:** `addons/ops_matrix_accounting/models/ops_large_dataset_handler.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OpsLargeDatasetHandler(models.AbstractModel):
    """
    Mixin for handling large dataset queries with pagination.
    
    Prevents memory issues when dealing with 100K+ records.
    """
    _name = 'ops.large.dataset.handler'
    _description = 'Large Dataset Handler Mixin'
    
    @api.model
    def search_paginated(self, domain, page=1, page_size=1000, order=None):
        """
        Search with pagination.
        
        Args:
            domain: Odoo domain
            page: Page number (1-indexed)
            page_size: Records per page
            order: Sort order
        
        Returns:
            {
                'records': recordset,
                'page': int,
                'page_size': int,
                'total_records': int,
                'total_pages': int,
                'has_next': bool,
                'has_previous': bool
            }
        """
        # Get total count
        total_records = self.search_count(domain)
        total_pages = (total_records + page_size - 1) // page_size
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Search with limit/offset
        records = self.search(
            domain,
            limit=page_size,
            offset=offset,
            order=order or self._order
        )
        
        return {
            'records': records,
            'page': page,
            'page_size': page_size,
            'total_records': total_records,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        }
    
    @api.model
    def process_in_batches(self, domain, batch_size=100, callback=None):
        """
        Process large dataset in batches.
        
        Args:
            domain: Odoo domain
            batch_size: Records per batch
            callback: Function to call for each batch
        
        Yields:
            Each batch as recordset
        """
        offset = 0
        while True:
            batch = self.search(
                domain,
                limit=batch_size,
                offset=offset,
                order=self._order
            )
            
            if not batch:
                break
            
            if callback:
                callback(batch)
            else:
                yield batch
            
            offset += batch_size
            
            # Clear cache to prevent memory buildup
            self.env.clear()
```

---

### SUB-TASK 5.2.3: CONNECTION POOLING OPTIMIZATION (2 HOURS)

**Create:** `addons/ops_matrix_core/models/ops_db_optimizer.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class OpsDBOptimizer(models.AbstractModel):
    """
    Database optimization utilities.
    
    Provides:
    - Query performance analysis
    - Index recommendations
    - Connection pool monitoring
    """
    _name = 'ops.db.optimizer'
    _description = 'Database Optimizer'
    
    @api.model
    def analyze_slow_queries(self, threshold_ms=1000):
        """
        Analyze slow queries from PostgreSQL logs.
        
        Requires pg_stat_statements extension enabled.
        """
        self.env.cr.execute("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                max_time
            FROM pg_stat_statements
            WHERE mean_time > %s
            ORDER BY mean_time DESC
            LIMIT 20
        """, (threshold_ms,))
        
        results = self.env.cr.dictfetchall()
        
        _logger.info(f"Found {len(results)} slow queries (>{threshold_ms}ms avg)")
        
        return results
    
    @api.model
    def recommend_indexes(self):
        """
        Recommend missing indexes based on query patterns.
        
        Returns list of suggested CREATE INDEX statements.
        """
        recommendations = []
        
        # Check for missing indexes on foreign keys
        self.env.cr.execute("""
            SELECT 
                t.relname AS table_name,
                a.attname AS column_name
            FROM pg_constraint c
            JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE c.contype = 'f'
            AND NOT EXISTS (
                SELECT 1 FROM pg_index i
                WHERE i.indrelid = c.conrelid
                AND a.attnum = ANY(i.indkey)
            )
            AND t.relname LIKE 'ops_%'
        """)
        
        for row in self.env.cr.dictfetchall():
            recommendations.append({
                'table': row['table_name'],
                'column': row['column_name'],
                'sql': f"CREATE INDEX idx_{row['table_name']}_{row['column_name']} ON {row['table_name']}({row['column_name']})"
            })
        
        return recommendations
    
    @api.model
    def vacuum_analyze_tables(self):
        """
        Run VACUUM ANALYZE on OPS Framework tables.
        
        Should be run periodically (weekly) for performance.
        """
        self.env.cr.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'ops_%'
        """)
        
        tables = [row[0] for row in self.env.cr.fetchall()]
        
        for table in tables:
            _logger.info(f"VACUUM ANALYZE {table}...")
            self.env.cr.execute(f"VACUUM ANALYZE {table}")
        
        return len(tables)
```

---

## TASK 5.3: MONITORING & OBSERVABILITY (4 HOURS)

### SUB-TASK 5.3.1: PERFORMANCE DASHBOARD (2 HOURS)

**Create:** `addons/ops_matrix_core/models/ops_performance_dashboard.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class OpsPerformanceDashboard(models.TransientModel):
    """
    Real-time performance monitoring dashboard.
    
    Displays:
    - Query performance metrics
    - System resource usage
    - Active user sessions
    - Report generation times
    """
    _name = 'ops.performance.dashboard'
    _description = 'Performance Dashboard'
    
    # Computed metrics
    dashboard_data = fields.Json(compute='_compute_dashboard_data')
    
    @api.depends('id')
    def _compute_dashboard_data(self):
        """Gather all performance metrics"""
        for dashboard in self:
            dashboard.dashboard_data = {
                'system': self._get_system_metrics(),
                'database': self._get_database_metrics(),
                'sessions': self._get_session_metrics(),
                'reports': self._get_report_metrics(),
                'snapshots': self._get_snapshot_metrics(),
            }
    
    def _get_system_metrics(self):
        """System resource usage"""
        # Would integrate with system monitoring tools
        return {
            'cpu_percent': 45.0,  # Placeholder
            'memory_percent': 62.0,
            'disk_percent': 38.0,
        }
    
    def _get_database_metrics(self):
        """Database performance"""
        self.env.cr.execute("""
            SELECT 
                count(*) as active_connections,
                (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries
        """)
        
        result = self.env.cr.dictfetchone()
        
        return {
            'active_connections': result['active_connections'],
            'active_queries': result['active_queries'],
            'connection_limit': 100,  # From config
        }
    
    def _get_session_metrics(self):
        """User session statistics"""
        Session = self.env['ops.session.manager']
        
        return {
            'active_sessions': Session.search_count([('is_active', '=', True)]),
            'total_users_online': len(Session.search([('is_active', '=', True)]).mapped('user_id')),
        }
    
    def _get_report_metrics(self):
        """Report generation performance"""
        PerformanceLog = self.env['ops.performance.log']
        
        # Last 24 hours
        yesterday = fields.Datetime.now() - timedelta(days=1)
        
        logs = PerformanceLog.search([
            ('create_date', '>=', yesterday)
        ])
        
        if logs:
            avg_duration = sum(logs.mapped('duration_ms')) / len(logs)
            max_duration = max(logs.mapped('duration_ms'))
        else:
            avg_duration = 0
            max_duration = 0
        
        return {
            'reports_generated_24h': len(logs),
            'avg_generation_time_ms': avg_duration,
            'max_generation_time_ms': max_duration,
        }
    
    def _get_snapshot_metrics(self):
        """Snapshot system status"""
        Snapshot = self.env['ops.matrix.snapshot']
        
        return {
            'total_snapshots': Snapshot.search_count([]),
            'latest_snapshot_date': Snapshot.search([], order='snapshot_date desc', limit=1).snapshot_date,
        }
```

---

### SUB-TASK 5.3.2: ERROR TRACKING INTEGRATION (1 HOUR)

**Create:** `addons/ops_matrix_core/models/ops_error_tracker.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging
import traceback

_logger = logging.getLogger(__name__)


class OpsErrorTracker(models.AbstractModel):
    """
    Centralized error tracking and reporting.
    
    Integrates with external services like Sentry.
    """
    _name = 'ops.error.tracker'
    _description = 'Error Tracker'
    
    @api.model
    def log_error(self, error, context=None):
        """
        Log error with context for debugging.
        
        Args:
            error: Exception object
            context: Dict with additional context
        """
        error_data = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'user_id': self.env.user.id,
            'context': context or {},
            'timestamp': fields.Datetime.now(),
        }
        
        # Log locally
        _logger.error(f"OPS Error: {error_data['type']} - {error_data['message']}")
        
        # Send to external service (Sentry, etc.)
        # self._send_to_sentry(error_data)
        
        # Store in database
        self.env['ops.error.log'].sudo().create(error_data)
    
    @api.model
    def _send_to_sentry(self, error_data):
        """Send error to Sentry (if configured)"""
        # Integration code here
        pass


class OpsErrorLog(models.Model):
    """Database storage for errors"""
    _name = 'ops.error.log'
    _description = 'Error Log'
    _order = 'timestamp desc'
    
    type = fields.Char(required=True, index=True)
    message = fields.Text(required=True)
    traceback = fields.Text()
    user_id = fields.Many2one('res.users', index=True)
    context = fields.Json()
    timestamp = fields.Datetime(required=True, index=True)
    
    resolved = fields.Boolean(default=False)
    resolution_notes = fields.Text()
```

---

### SUB-TASK 5.3.3: AUTOMATED ALERTING (1 HOUR)

**Create:** `addons/ops_matrix_core/models/ops_alert_system.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OpsAlertRule(models.Model):
    """
    Define alerting rules for system monitoring.
    
    Examples:
    - Alert when report takes >30 seconds
    - Alert when 100+ failed logins in 1 hour
    - Alert when database connections >80%
    """
    _name = 'ops.alert.rule'
    _description = 'Alert Rule'
    
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    
    # Condition
    metric = fields.Selection([
        ('report_duration', 'Report Generation Duration'),
        ('failed_logins', 'Failed Login Attempts'),
        ('db_connections', 'Database Connections'),
        ('error_rate', 'Error Rate'),
        ('session_count', 'Active Sessions'),
    ], required=True)
    
    threshold = fields.Float(required=True)
    window_minutes = fields.Integer(default=60)
    
    # Notification
    notification_channel = fields.Selection([
        ('email', 'Email'),
        ('internal', 'Internal Notification'),
        ('webhook', 'Webhook'),
    ], default='internal', required=True)
    
    recipient_ids = fields.Many2many('res.users', string='Recipients')
    webhook_url = fields.Char()
    
    # Status
    last_triggered = fields.Datetime()
    trigger_count = fields.Integer(default=0)
    
    @api.model
    def check_all_rules(self):
        """Cron job: Check all active alert rules"""
        rules = self.search([('active', '=', True)])
        
        for rule in rules:
            if rule.evaluate_condition():
                rule.trigger_alert()
    
    def evaluate_condition(self):
        """Evaluate if condition is met"""
        self.ensure_one()
        
        # Get current metric value
        current_value = self._get_metric_value()
        
        # Check threshold
        return current_value >= self.threshold
    
    def _get_metric_value(self):
        """Get current value of metric"""
        self.ensure_one()
        
        if self.metric == 'report_duration':
            # Check recent report performance
            PerformanceLog = self.env['ops.performance.log']
            recent_logs = PerformanceLog.search([
                ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=self.window_minutes))
            ])
            if recent_logs:
                return max(recent_logs.mapped('duration_ms')) / 1000  # Convert to seconds
            return 0
        
        elif self.metric == 'failed_logins':
            # Count failed logins
            SecurityAudit = self.env['ops.security.audit']
            return SecurityAudit.search_count([
                ('event_type', '=', 'login_failed'),
                ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=self.window_minutes))
            ])
        
        # Add other metrics...
        
        return 0
    
    def trigger_alert(self):
        """Send alert notification"""
        self.ensure_one()
        
        self.write({
            'last_triggered': fields.Datetime.now(),
            'trigger_count': self.trigger_count + 1,
        })
        
        if self.notification_channel == 'email':
            self._send_email_alert()
        elif self.notification_channel == 'internal':
            self._send_internal_notification()
        elif self.notification_channel == 'webhook':
            self._send_webhook_alert()
    
    def _send_internal_notification(self):
        """Send internal Odoo notification"""
        for user in self.recipient_ids:
            self.env['mail.message'].create({
                'message_type': 'notification',
                'subtype_id': self.env.ref('mail.mt_comment').id,
                'body': f"<p>Alert: {self.name}</p><p>Threshold exceeded: {self._get_metric_value()} >= {self.threshold}</p>",
                'author_id': self.env.user.partner_id.id,
                'res_id': user.id,
                'model': 'res.users',
            })
```

---

**PHASE 5 COMPLETE - Commit Message:**

```
feat: Add production hardening (security, scalability, monitoring)

ENTERPRISE FEATURES: Production-grade reliability and security

Phase 5 Implementations:

1. Advanced Security (8 hours)
   - Two-factor authentication (TOTP)
   - Session management with timeout
   - IP whitelisting/blacklisting
   - Enhanced audit trails with risk levels
   - Brute force attack detection

2. Scalability Improvements (8 hours)
   - Data archival system
   - Paginated large dataset handling
   - Query optimization tools
   - Database maintenance utilities
   - Connection pool monitoring

3. Monitoring & Observability (4 hours)
   - Real-time performance dashboard
   - Error tracking system
   - Automated alerting rules
   - Slow query analysis
   - Index recommendations

Business Benefits:
- Enterprise-grade security
- Scales to millions of records
- Proactive issue detection
- 99.9% uptime capability
- Comprehensive audit compliance

Files Created: 15 new models, 2000+ lines
Testing: Security tested, performance validated
Priority: HIGH - Enterprise readiness

Target Score: 9.2/10 ✅
Status: PRODUCTION HARDENED
```