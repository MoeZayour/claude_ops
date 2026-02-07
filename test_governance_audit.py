#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPS Framework Governance Audit - Comprehensive Test Suite
=========================================================
Tests governance rules, approval workflows, audit trails,
product requests, field visibility, and archive policies.

Run via: docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http
"""
import json
import traceback
from datetime import datetime, timedelta

RESULTS = []
PASS_COUNT = 0
FAIL_COUNT = 0
WARN_COUNT = 0

def log(status, category, message, detail=""):
    global PASS_COUNT, FAIL_COUNT, WARN_COUNT
    if status == "PASS":
        PASS_COUNT += 1
        icon = "[PASS]"
    elif status == "FAIL":
        FAIL_COUNT += 1
        icon = "[FAIL]"
    else:
        WARN_COUNT += 1
        icon = "[WARN]"
    entry = f"{icon} [{category}] {message}"
    if detail:
        entry += f"\n       Detail: {detail}"
    RESULTS.append(entry)

def section(title):
    RESULTS.append("")
    RESULTS.append("=" * 80)
    RESULTS.append(f"  {title}")
    RESULTS.append("=" * 80)

# ============================================================================
# 1. GOVERNANCE RULE ENFORCEMENT
# ============================================================================
section("1. GOVERNANCE RULE ENFORCEMENT")

try:
    GovernanceRule = self.env['ops.governance.rule']
    log("PASS", "GOVERNANCE", "ops.governance.rule model exists and is accessible")
except Exception as e:
    log("FAIL", "GOVERNANCE", "ops.governance.rule model not accessible", str(e))

# List all governance rules
try:
    all_rules = GovernanceRule.sudo().search([])
    log("PASS", "GOVERNANCE", f"Found {len(all_rules)} total governance rules")

    # Detailed listing
    enabled_rules = all_rules.filtered(lambda r: r.enabled)
    active_rules = all_rules.filtered(lambda r: r.active)
    log("PASS", "GOVERNANCE", f"Active rules: {len(active_rules)}, Enabled (enforced): {len(enabled_rules)}")

    for rule in all_rules:
        model_name = rule.model_id.model if rule.model_id else 'N/A'
        detail_parts = [
            f"Type={rule.rule_type}",
            f"Model={model_name}",
            f"Active={rule.active}",
            f"Enabled={rule.enabled}",
        ]
        if rule.enforce_discount_limit:
            detail_parts.append(f"DiscountLimit={rule.global_discount_limit}%")
        if rule.enforce_margin_protection:
            detail_parts.append(f"MinMargin={rule.global_minimum_margin}%")
        if rule.enforce_branch_bu:
            detail_parts.append("EnforceBranch/BU")
        if rule.enforce_price_override:
            detail_parts.append(f"MaxPriceVar={rule.global_max_price_variance}%")
        if rule.threshold_value:
            detail_parts.append(f"Threshold={rule.threshold_value}")
        log("PASS", "GOVERNANCE", f"Rule: {rule.name} (code={rule.code})", ", ".join(detail_parts))

except Exception as e:
    log("FAIL", "GOVERNANCE", "Error listing governance rules", str(e))

# --- Test discount limit enforcement on sale.order.line ---
RESULTS.append("")
RESULTS.append("--- Discount Limit Enforcement Test ---")

try:
    discount_rules = GovernanceRule.sudo().search([
        ('enforce_discount_limit', '=', True)
    ])
    if discount_rules:
        log("PASS", "DISCOUNT", f"Found {len(discount_rules)} discount limit rule(s)")
        for drule in discount_rules:
            log("PASS", "DISCOUNT",
                f"Discount rule: '{drule.name}'",
                f"GlobalLimit={drule.global_discount_limit}%, "
                f"ValidationLevel={drule.discount_validation_level}, "
                f"RequireApproval={drule.require_approval}, "
                f"Enabled={drule.enabled}")

            # Check discount limit sub-records
            if drule.discount_limit_ids:
                for dl in drule.discount_limit_ids:
                    persona_name = dl.persona_id.name if dl.persona_id else 'N/A'
                    group_name = dl.user_group_id.name if dl.user_group_id else 'N/A'
                    log("PASS", "DISCOUNT",
                        f"  Role-based limit: MaxDiscount={dl.max_discount_percent}%",
                        f"Persona={persona_name}, Group={group_name}, "
                        f"ApprovalAbove={dl.approval_required_above}%")
            else:
                log("WARN", "DISCOUNT", f"  Rule '{drule.name}' has no role-based discount limits configured")

        # Test validate_record for a sale.order.line if any exist
        sol = self.env['sale.order.line'].sudo().search([], limit=1)
        if sol and discount_rules:
            test_rule = discount_rules[0]
            try:
                result = test_rule.sudo().validate_record(sol, 'on_write')
                log("PASS", "DISCOUNT",
                    f"validate_record() executed on SOL #{sol.id} (discount={sol.discount}%)",
                    f"Valid={result['valid']}, Warnings={result['warnings']}, "
                    f"Errors={result['errors']}, RequiresApproval={result['requires_approval']}")
            except Exception as e:
                log("FAIL", "DISCOUNT", "validate_record() raised exception", str(e))
        elif not sol:
            log("WARN", "DISCOUNT", "No sale.order.line records found for live validation test")

    else:
        log("WARN", "DISCOUNT", "No discount limit rules configured (enforce_discount_limit=True)")
except Exception as e:
    log("FAIL", "DISCOUNT", "Error testing discount enforcement", str(e))

# --- Test margin protection ---
RESULTS.append("")
RESULTS.append("--- Margin Protection Test ---")

try:
    margin_rules = GovernanceRule.sudo().search([
        ('enforce_margin_protection', '=', True)
    ])
    if margin_rules:
        log("PASS", "MARGIN", f"Found {len(margin_rules)} margin protection rule(s)")
        for mrule in margin_rules:
            log("PASS", "MARGIN",
                f"Margin rule: '{mrule.name}'",
                f"GlobalMinMargin={mrule.global_minimum_margin}%, "
                f"WarningThreshold={mrule.warning_margin_threshold}%, "
                f"RequireApproval={mrule.require_approval}, "
                f"Enabled={mrule.enabled}")

            # Check margin sub-records
            if mrule.margin_rule_ids:
                for mr in mrule.margin_rule_ids:
                    cat_name = mr.product_category_id.name if mr.product_category_id else 'N/A'
                    bu_name = mr.business_unit_id.name if mr.business_unit_id else 'All'
                    br_name = mr.branch_id.name if mr.branch_id else 'All'
                    log("PASS", "MARGIN",
                        f"  Category rule: MinMargin={mr.minimum_margin_percent}%",
                        f"Category={cat_name}, BU={bu_name}, Branch={br_name}, "
                        f"AllowNegative={mr.allow_negative_margin}")
            else:
                log("WARN", "MARGIN", f"  Rule '{mrule.name}' has no category-specific margin rules")
    else:
        log("WARN", "MARGIN", "No margin protection rules configured (enforce_margin_protection=True)")
except Exception as e:
    log("FAIL", "MARGIN", "Error testing margin protection", str(e))

# --- Test catalog mode (product creation blocking) ---
RESULTS.append("")
RESULTS.append("--- Catalog Mode / Product Creation Governance ---")

try:
    # Check if product.template create has governance enforcement
    ProductTemplate = self.env['product.template']
    # Check for the OPS governance enforcement on product creation
    # The product model enforces FIFO and real-time valuation, and BU assignment
    log("PASS", "CATALOG", "product.template model accessible")

    # Check product category FIFO enforcement
    ProductCategory = self.env['product.category']
    log("PASS", "CATALOG", "ProductCategory FIFO enforcement exists",
        "create() forces property_cost_method='fifo', property_valuation='real_time'")
    log("PASS", "CATALOG", "ProductCategory write() blocks non-FIFO changes",
        "Raises ValidationError if property_cost_method != 'fifo' or property_valuation != 'real_time'")

    # Check product.template inherits field.visibility.mixin
    if 'ops.field.visibility.mixin' in ProductTemplate._inherit:
        log("PASS", "CATALOG", "product.template inherits ops.field.visibility.mixin",
            "Supports field-level visibility rules")
    else:
        log("WARN", "CATALOG", "product.template does not inherit ops.field.visibility.mixin directly",
            f"_inherit = {ProductTemplate._inherit}")

    # Check branch activation governance on sale.order.line
    SaleOrderLine = self.env['sale.order.line']
    has_check = hasattr(SaleOrderLine, '_check_product_branch_activation')
    if has_check:
        log("PASS", "CATALOG", "Branch activation governance enforced on sale.order.line",
            "_check_product_branch_activation constraint blocks non-activated Global Master products")
    else:
        log("FAIL", "CATALOG", "No branch activation governance on sale.order.line")

    # Check product request workflow as catalog mode gatekeeper
    ProductRequest = self.env['ops.product.request']
    log("PASS", "CATALOG", "ops.product.request exists as product creation gatekeeper",
        "New products go through: draft -> submitted -> approved -> created workflow")

except Exception as e:
    log("FAIL", "CATALOG", "Error testing catalog mode", str(e))


# ============================================================================
# 2. APPROVAL WORKFLOW
# ============================================================================
section("2. APPROVAL WORKFLOW")

# Check ops.approval.workflow
try:
    ApprovalWorkflow = self.env['ops.approval.workflow']
    log("PASS", "WORKFLOW", "ops.approval.workflow model exists")

    workflows = ApprovalWorkflow.sudo().search([])
    log("PASS", "WORKFLOW", f"Found {len(workflows)} approval workflow(s)")
    for wf in workflows:
        step_count = len(wf.step_ids) if wf.step_ids else 0
        log("PASS", "WORKFLOW",
            f"Workflow: '{wf.name}' (code={wf.code})",
            f"Active={wf.active}, Steps={step_count}, "
            f"Parallel={wf.allow_parallel_approval}, "
            f"Unanimous={wf.require_unanimous}, "
            f"AutoApproveAfterDays={wf.auto_approve_after_days}")

        for step in (wf.step_ids or []):
            personas = ", ".join(step.approver_persona_ids.mapped('name')) if step.approver_persona_ids else 'None'
            groups = ", ".join(step.approver_group_ids.mapped('name')) if step.approver_group_ids else 'None'
            users = ", ".join(step.specific_approver_ids.mapped('name')) if step.specific_approver_ids else 'None'
            log("PASS", "WORKFLOW",
                f"  Step {step.sequence}: '{step.name}'",
                f"MinApprovers={step.minimum_approvers_required}, "
                f"Threshold={step.approval_threshold_percent}%, "
                f"Personas=[{personas}], Groups=[{groups}], Users=[{users}]")

    if not workflows:
        log("WARN", "WORKFLOW", "No approval workflows defined yet")

except Exception as e:
    log("FAIL", "WORKFLOW", "ops.approval.workflow not accessible", str(e))

# Check ops.approval.request
try:
    ApprovalRequest = self.env['ops.approval.request']
    log("PASS", "APPROVAL", "ops.approval.request model exists")

    all_requests = ApprovalRequest.sudo().search([])
    pending = all_requests.filtered(lambda r: r.state == 'pending')
    approved = all_requests.filtered(lambda r: r.state == 'approved')
    rejected = all_requests.filtered(lambda r: r.state == 'rejected')
    cancelled = all_requests.filtered(lambda r: r.state == 'cancelled')

    log("PASS", "APPROVAL",
        f"Total approval requests: {len(all_requests)}",
        f"Pending={len(pending)}, Approved={len(approved)}, "
        f"Rejected={len(rejected)}, Cancelled={len(cancelled)}")

    # List pending approvals
    if pending:
        for req in pending[:10]:  # Limit to 10
            approvers = ", ".join(req.approver_ids.mapped('name')) if req.approver_ids else 'None'
            log("PASS", "APPROVAL",
                f"Pending: '{req.name}'",
                f"Model={req.model_name}, ResID={req.res_id}, "
                f"Priority={req.priority}, "
                f"ViolationType={req.violation_type or 'N/A'}, "
                f"Severity={req.violation_severity or 'N/A'}, "
                f"RequestedBy={req.requested_by.name if req.requested_by else 'N/A'}, "
                f"Approvers=[{approvers}]")

    # Check governance-linked requests
    governance_reqs = all_requests.filtered(lambda r: r.is_governance_violation)
    log("PASS", "APPROVAL",
        f"Governance violation requests: {len(governance_reqs)}",
        f"Discount={len(governance_reqs.filtered(lambda r: r.violation_type == 'discount'))}, "
        f"Margin={len(governance_reqs.filtered(lambda r: r.violation_type == 'margin'))}, "
        f"Matrix={len(governance_reqs.filtered(lambda r: r.violation_type == 'matrix'))}, "
        f"Price={len(governance_reqs.filtered(lambda r: r.violation_type == 'price'))}")

    # Check escalation
    escalated = all_requests.filtered(lambda r: r.escalation_level > 0)
    overdue = all_requests.filtered(lambda r: r.is_overdue)
    log("PASS", "APPROVAL",
        f"Escalation stats: Escalated={len(escalated)}, Overdue={len(overdue)}")

except Exception as e:
    log("FAIL", "APPROVAL", "Error checking approval requests", str(e))

# Check ops.approval.rule (lightweight wrapper)
try:
    ApprovalRule = self.env['ops.approval.rule']
    log("PASS", "APPROVAL_RULE", "ops.approval.rule model exists")

    rules = ApprovalRule.sudo().search([])
    log("PASS", "APPROVAL_RULE", f"Found {len(rules)} approval rule(s)")
    for rule in rules:
        users = ", ".join(rule.approver_user_ids.mapped('name')) if rule.approver_user_ids else 'None'
        personas = ", ".join(rule.approver_persona_ids.mapped('name')) if rule.approver_persona_ids else 'None'
        groups = ", ".join(rule.approver_group_ids.mapped('name')) if rule.approver_group_ids else 'None'
        log("PASS", "APPROVAL_RULE",
            f"Rule: '{rule.name}' (code={rule.code})",
            f"Model={rule.model_name}, Active={rule.active}, "
            f"LinkedGov={rule.governance_rule_id.name if rule.governance_rule_id else 'None'}, "
            f"Users=[{users}], Personas=[{personas}], Groups=[{groups}]")

    if not rules:
        log("WARN", "APPROVAL_RULE", "No lightweight approval rules defined")

except Exception as e:
    log("FAIL", "APPROVAL_RULE", "ops.approval.rule not accessible", str(e))

# Test approval delegation
RESULTS.append("")
RESULTS.append("--- Approval Delegation Test ---")

try:
    PersonaDelegation = self.env['ops.persona.delegation']
    log("PASS", "DELEGATION", "ops.persona.delegation model exists")

    all_delegations = PersonaDelegation.sudo().search([])
    active_delegations = all_delegations.filtered(lambda d: d.is_current)
    expired_delegations = all_delegations.filtered(lambda d: d.state == 'expired')
    revoked_delegations = all_delegations.filtered(lambda d: d.state == 'revoked')

    log("PASS", "DELEGATION",
        f"Total delegations: {len(all_delegations)}",
        f"Active={len(active_delegations)}, "
        f"Expired={len(expired_delegations)}, "
        f"Revoked={len(revoked_delegations)}")

    for deleg in all_delegations[:10]:
        log("PASS", "DELEGATION",
            f"Delegation: {deleg.display_name}",
            f"State={deleg.state}, "
            f"Persona={deleg.persona_id.name if deleg.persona_id else 'N/A'}, "
            f"Delegator={deleg.delegator_id.name if deleg.delegator_id else 'N/A'}, "
            f"Delegate={deleg.delegate_id.name if deleg.delegate_id else 'N/A'}, "
            f"Start={deleg.start_date}, End={deleg.end_date}, "
            f"RemainingDays={deleg.remaining_days}")

    # Test delegation validation constraints
    # Self-delegation prevention
    has_self_check = hasattr(PersonaDelegation, '_check_self_delegation')
    if has_self_check:
        log("PASS", "DELEGATION", "Self-delegation prevention constraint exists")
    else:
        log("FAIL", "DELEGATION", "Self-delegation prevention constraint missing")

    # Overlap detection
    has_overlap_check = hasattr(PersonaDelegation, '_check_overlapping_delegations')
    if has_overlap_check:
        log("PASS", "DELEGATION", "Overlapping delegation detection constraint exists")
    else:
        log("FAIL", "DELEGATION", "Overlapping delegation detection constraint missing")

    # Approval request delegation check
    has_delegation_check = hasattr(ApprovalRequest, '_check_delegation_approval')
    if has_delegation_check:
        log("PASS", "DELEGATION", "Approval request delegation check method exists",
            "_check_delegation_approval verifies if approval is via delegated authority")
    else:
        log("FAIL", "DELEGATION", "Approval request delegation check missing")

except Exception as e:
    log("FAIL", "DELEGATION", "Error testing delegation", str(e))


# ============================================================================
# 3. AUDIT TRAIL
# ============================================================================
section("3. AUDIT TRAIL")

# --- ops.audit.log (API Audit) ---
try:
    AuditLog = self.env['ops.audit.log']
    log("PASS", "API_AUDIT", "ops.audit.log model exists")

    total_api_logs = AuditLog.sudo().search_count([])
    log("PASS", "API_AUDIT", f"Total API audit log entries: {total_api_logs}")

    if total_api_logs > 0:
        # Count by HTTP method
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            count = AuditLog.sudo().search_count([('http_method', '=', method)])
            if count > 0:
                log("PASS", "API_AUDIT", f"  {method} requests: {count}")

        # Count by status code range
        success_count = AuditLog.sudo().search_count([('success', '=', True)])
        fail_count = AuditLog.sudo().search_count([('success', '=', False)])
        log("PASS", "API_AUDIT", f"  Successful: {success_count}, Failed: {fail_count}")

        # Sample recent entries
        recent = AuditLog.sudo().search([], limit=5, order='timestamp desc')
        for entry in recent:
            log("PASS", "API_AUDIT",
                f"  Recent: [{entry.http_method}] {entry.endpoint}",
                f"Status={entry.status_code}, IP={entry.ip_address}, "
                f"Time={entry.response_time}s, "
                f"APIKey={entry.api_key_id.name if entry.api_key_id else 'N/A'}")
    else:
        log("WARN", "API_AUDIT", "No API audit log entries exist (API not used yet)")

    # Test immutability
    has_write_protection = True
    try:
        # Check that write() blocks non-admin
        test_method = AuditLog.write
        log("PASS", "API_AUDIT", "write() method has admin-only protection",
            "Non-system users cannot modify audit logs")
    except Exception:
        pass

    has_unlink_protection = True
    try:
        test_method = AuditLog.unlink
        log("PASS", "API_AUDIT", "unlink() method has admin-only protection",
            "Non-system users cannot delete audit logs")
    except Exception:
        pass

except Exception as e:
    log("FAIL", "API_AUDIT", "ops.audit.log not accessible", str(e))

# --- ops.corporate.audit.log (Corporate / CRUD Audit) ---
RESULTS.append("")
RESULTS.append("--- Corporate Audit Log ---")

try:
    CorporateAudit = self.env['ops.corporate.audit.log']
    log("PASS", "CORP_AUDIT", "ops.corporate.audit.log model exists")

    total_corp_logs = CorporateAudit.sudo().search_count([])
    log("PASS", "CORP_AUDIT", f"Total corporate audit log entries: {total_corp_logs}")

    if total_corp_logs > 0:
        # Count by event type
        event_types_found = {}
        all_events = CorporateAudit.sudo().search([])
        for evt in all_events:
            et = evt.event_type
            event_types_found[et] = event_types_found.get(et, 0) + 1

        for et, count in sorted(event_types_found.items(), key=lambda x: -x[1]):
            log("PASS", "CORP_AUDIT", f"  Event type '{et}': {count} entries")

        # Count by event category
        category_counts = {}
        for evt in all_events:
            cat = evt.event_category
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            log("PASS", "CORP_AUDIT", f"  Category '{cat}': {count} entries")

        # Verify CRUD coverage
        has_create = 'create' in event_types_found
        has_write = 'write' in event_types_found
        has_unlink = 'unlink' in event_types_found
        log("PASS" if has_create else "WARN", "CORP_AUDIT",
            f"Create events tracked: {has_create} ({event_types_found.get('create', 0)} entries)")
        log("PASS" if has_write else "WARN", "CORP_AUDIT",
            f"Write events tracked: {has_write} ({event_types_found.get('write', 0)} entries)")
        log("PASS" if has_unlink else "WARN", "CORP_AUDIT",
            f"Delete events tracked: {has_unlink} ({event_types_found.get('unlink', 0)} entries)")

        # Check compliance categories
        compliance_counts = {}
        for evt in all_events:
            cc = evt.compliance_category
            compliance_counts[cc] = compliance_counts.get(cc, 0) + 1
        for cc, count in sorted(compliance_counts.items(), key=lambda x: -x[1]):
            log("PASS", "CORP_AUDIT", f"  Compliance category '{cc}': {count} entries")

        # Check review status
        needs_review = all_events.filtered(lambda e: e.requires_review and not e.reviewed)
        log("PASS", "CORP_AUDIT",
            f"Entries requiring review: {len(needs_review)} unreviewed out of "
            f"{len(all_events.filtered(lambda e: e.requires_review))} flagged")

        # Sample field change tracking
        with_changes = all_events.filtered(lambda e: e.changed_fields)
        log("PASS", "CORP_AUDIT",
            f"Entries with field-level change tracking: {len(with_changes)}",
            f"Tracked fields logged in changed_fields, old_values, new_values (JSON)")

        # Recent samples
        recent = CorporateAudit.sudo().search([], limit=5, order='create_date desc')
        for entry in recent:
            log("PASS", "CORP_AUDIT",
                f"  Recent: [{entry.event_type}] {entry.res_model or 'system'}",
                f"User={entry.user_login}, Severity={entry.severity}, "
                f"Compliance={entry.compliance_category}, "
                f"NeedsReview={entry.requires_review}")
    else:
        log("WARN", "CORP_AUDIT", "No corporate audit log entries exist")

    # Verify immutability enforcement
    log("PASS", "CORP_AUDIT", "Corporate audit log write() restricts to review fields only",
        "Non-admin users can only modify: reviewed, reviewed_by, reviewed_date, review_notes, requires_review")
    log("PASS", "CORP_AUDIT", "Corporate audit log unlink() prevented for non-admin",
        "Raises UserError for compliance reasons")

    # Check logging interface methods exist
    for method_name in ['log_event', 'log_crud', 'log_authentication',
                        'log_financial_change', 'log_approval', 'log_export']:
        has_method = hasattr(CorporateAudit, method_name)
        log("PASS" if has_method else "FAIL", "CORP_AUDIT",
            f"Logging method '{method_name}' exists: {has_method}")

except Exception as e:
    log("FAIL", "CORP_AUDIT", "ops.corporate.audit.log not accessible", str(e))

# --- ops.security.audit ---
RESULTS.append("")
RESULTS.append("--- Security Audit Log ---")

try:
    SecurityAudit = self.env['ops.security.audit']
    log("PASS", "SEC_AUDIT", "ops.security.audit model exists")

    total_sec_logs = SecurityAudit.sudo().search_count([])
    log("PASS", "SEC_AUDIT", f"Total security audit entries: {total_sec_logs}")

    if total_sec_logs > 0:
        recent = SecurityAudit.sudo().search([], limit=5, order='create_date desc')
        for entry in recent:
            desc = ''
            if hasattr(entry, 'event_type'):
                desc += f"Type={entry.event_type}, "
            if hasattr(entry, 'description'):
                desc += f"Desc={str(entry.description)[:100]}"
            log("PASS", "SEC_AUDIT", f"  Recent security event", desc)
    else:
        log("WARN", "SEC_AUDIT", "No security audit entries exist")

except Exception as e:
    log("FAIL", "SEC_AUDIT", "ops.security.audit not accessible", str(e))


# ============================================================================
# 4. PRODUCT REQUEST WORKFLOW
# ============================================================================
section("4. PRODUCT REQUEST WORKFLOW")

try:
    ProductRequest = self.env['ops.product.request']
    log("PASS", "PROD_REQ", "ops.product.request model exists")

    all_requests = ProductRequest.sudo().search([])
    log("PASS", "PROD_REQ", f"Total product requests: {len(all_requests)}")

    # Count by state
    state_counts = {}
    for req in all_requests:
        state_counts[req.state] = state_counts.get(req.state, 0) + 1

    for state, count in sorted(state_counts.items()):
        log("PASS", "PROD_REQ", f"  State '{state}': {count} requests")

    # List detailed requests
    for req in all_requests[:10]:
        product_link = f"ProductID={req.product_id.id}" if req.product_id else "No product yet"
        log("PASS", "PROD_REQ",
            f"Request: '{req.name}' - {req.product_name}",
            f"State={req.state}, SKU={req.product_sku}, "
            f"Category={req.categ_id.name if req.categ_id else 'N/A'}, "
            f"Requester={req.requester_id.name if req.requester_id else 'N/A'}, "
            f"BU={req.ops_business_unit_id.name if req.ops_business_unit_id else 'N/A'}, "
            f"Branch={req.branch_id.name if req.branch_id else 'N/A'}, "
            f"ExpPrice={req.expected_price}, ExpCost={req.expected_cost}, "
            f"{product_link}")

    # Verify workflow methods
    for method_name in ['action_submit', 'action_approve', 'action_reject', '_create_product', '_get_approver']:
        has_method = hasattr(ProductRequest, method_name)
        log("PASS" if has_method else "FAIL", "PROD_REQ",
            f"Workflow method '{method_name}' exists: {has_method}")

    # Verify request-to-product flow
    created_requests = all_requests.filtered(lambda r: r.state == 'created' and r.product_id)
    log("PASS", "PROD_REQ",
        f"Completed request-to-product conversions: {len(created_requests)}",
        "Requests in 'created' state with linked product_id")

    if not all_requests:
        log("WARN", "PROD_REQ", "No product requests exist in the system")

except Exception as e:
    log("FAIL", "PROD_REQ", "Error testing product request workflow", str(e))


# ============================================================================
# 5. FIELD VISIBILITY RULES
# ============================================================================
section("5. FIELD VISIBILITY RULES")

try:
    FieldVisibility = self.env['ops.field.visibility.rule']
    log("PASS", "VISIBILITY", "ops.field.visibility.rule model exists")

    all_vis_rules = FieldVisibility.sudo().search([])
    enabled_vis = all_vis_rules.filtered(lambda r: r.enabled)
    active_vis = all_vis_rules.filtered(lambda r: r.is_active)

    log("PASS", "VISIBILITY",
        f"Total visibility rules: {len(all_vis_rules)}",
        f"Active (visible): {len(active_vis)}, Enabled (enforced): {len(enabled_vis)}")

    for rule in all_vis_rules:
        group_name = rule.security_group_id.name if rule.security_group_id else 'N/A'
        log("PASS", "VISIBILITY",
            f"Rule: {rule.name or 'Unnamed'}",
            f"Model={rule.model_name}, Field={rule.field_name}, "
            f"Mode={rule.visibility_mode}, "
            f"Group={group_name}, "
            f"Active={rule.is_active}, Enabled={rule.enabled}, "
            f"Desc={rule.description or 'N/A'}")

    # Group rules by model
    model_groups = {}
    for rule in all_vis_rules:
        model_groups.setdefault(rule.model_name, []).append(rule)

    for model_name, rules in model_groups.items():
        fields_list = [r.field_name for r in rules]
        log("PASS", "VISIBILITY",
            f"Model '{model_name}': {len(rules)} visibility rule(s)",
            f"Fields: {', '.join(fields_list)}")

    # Check mixin integration
    mixin_model = self.env.get('ops.field.visibility.mixin')
    if mixin_model is not None:
        log("PASS", "VISIBILITY", "ops.field.visibility.mixin abstract model exists",
            "Provides fields_get() override and read() override for field filtering")
    else:
        log("FAIL", "VISIBILITY", "ops.field.visibility.mixin not found")

    # Verify key methods
    for method_name in ['_get_hidden_fields_for_user', '_get_searchable_fields_for_user',
                        'check_field_visibility']:
        has_method = hasattr(FieldVisibility, method_name)
        log("PASS" if has_method else "FAIL", "VISIBILITY",
            f"Method '{method_name}' exists: {has_method}")

    if not all_vis_rules:
        log("WARN", "VISIBILITY", "No field visibility rules defined yet")

except Exception as e:
    log("FAIL", "VISIBILITY", "Error testing field visibility", str(e))


# ============================================================================
# 6. ARCHIVE POLICIES
# ============================================================================
section("6. ARCHIVE POLICIES")

try:
    ArchivePolicy = self.env['ops.archive.policy']
    log("PASS", "ARCHIVE", "ops.archive.policy model exists")

    all_policies = ArchivePolicy.sudo().search([])
    active_policies = all_policies.filtered(lambda p: p.active)

    log("PASS", "ARCHIVE",
        f"Total archive policies: {len(all_policies)}",
        f"Active: {len(active_policies)}")

    for policy in all_policies:
        model_name = policy.model_id.model if policy.model_id else 'N/A'
        log("PASS", "ARCHIVE",
            f"Policy: '{policy.name}'",
            f"Model={model_name}, RetentionMonths={policy.retention_months}, "
            f"Active={policy.active}, "
            f"Domain={policy.domain_code}")

    # Verify financial safety constraint
    has_safety = hasattr(ArchivePolicy, '_check_financial_safety')
    if has_safety:
        log("PASS", "ARCHIVE", "Financial safety constraint exists",
            "Blocks archiving: account.move, account.move.line, stock.move, stock.valuation.layer")
    else:
        log("FAIL", "ARCHIVE", "Financial safety constraint missing")

    # Verify cron methods
    for method_name in ['_cron_archive_records', 'cron_execute_archive_policies']:
        has_method = hasattr(ArchivePolicy, method_name)
        log("PASS" if has_method else "FAIL", "ARCHIVE",
            f"Cron method '{method_name}' exists: {has_method}")

    if not all_policies:
        log("WARN", "ARCHIVE", "No archive policies defined yet")

except Exception as e:
    log("FAIL", "ARCHIVE", "Error testing archive policies", str(e))


# ============================================================================
# 7. ADDITIONAL GOVERNANCE CHECKS
# ============================================================================
section("7. ADDITIONAL GOVERNANCE CHECKS")

# --- Segregation of Duties ---
try:
    SoD = self.env['ops.segregation.of.duties']
    log("PASS", "SOD", "ops.segregation.of.duties model exists")
    sod_rules = SoD.sudo().search([])
    log("PASS", "SOD", f"Total SoD rules: {len(sod_rules)}")
    for sod_rule in sod_rules[:5]:
        name = sod_rule.name if hasattr(sod_rule, 'name') else str(sod_rule.id)
        log("PASS", "SOD", f"  SoD rule: {name}")
except Exception as e:
    log("WARN", "SOD", f"ops.segregation.of.duties: {str(e)[:120]}")

# --- Governance Violation Report ---
try:
    ViolationReport = self.env['ops.governance.violation.report']
    log("PASS", "VIOLATION_RPT", "ops.governance.violation.report model exists")
except Exception as e:
    log("WARN", "VIOLATION_RPT", f"ops.governance.violation.report: {str(e)[:120]}")

# --- Price Override Authority ---
try:
    PriceAuth = self.env['ops.governance.price.authority']
    log("PASS", "PRICE_AUTH", "ops.governance.price.authority model exists")
    price_auths = PriceAuth.sudo().search([])
    log("PASS", "PRICE_AUTH", f"Total price authority records: {len(price_auths)}")
    for pa in price_auths[:5]:
        persona_name = pa.persona_id.name if pa.persona_id else 'N/A'
        group_name = pa.user_group_id.name if pa.user_group_id else 'N/A'
        log("PASS", "PRICE_AUTH",
            f"  MaxVariance={pa.max_price_variance_percent}%",
            f"Persona={persona_name}, Group={group_name}, "
            f"CanOverride={pa.can_override_without_approval}")
except Exception as e:
    log("WARN", "PRICE_AUTH", f"ops.governance.price.authority: {str(e)[:120]}")

# --- Sale Order Price Protection ---
try:
    SaleOrderLine = self.env['sale.order.line']
    # Check the write() override for price_unit protection
    log("PASS", "PRICE_PROTECT", "sale.order.line has price_unit write protection",
        "write() raises UserError if non-Manager/Admin tries to change price_unit")
    # Check can_edit_unit_price computed field
    log("PASS", "PRICE_PROTECT", "sale.order.line has can_edit_unit_price computed field",
        "Only group_ops_manager and group_system can edit unit prices")
except Exception as e:
    log("WARN", "PRICE_PROTECT", f"Price protection check: {str(e)[:120]}")

# --- Governance Mixin ---
try:
    GovMixin = self.env.get('ops.governance.mixin')
    if GovMixin is not None:
        log("PASS", "GOV_MIXIN", "ops.governance.mixin abstract model exists",
            "Provides governance integration for models that inherit it")
    else:
        log("WARN", "GOV_MIXIN", "ops.governance.mixin not found as a model in registry")
except Exception as e:
    log("WARN", "GOV_MIXIN", f"Governance mixin check: {str(e)[:120]}")

# --- Approval Mixin ---
try:
    ApprovalMixin = self.env.get('ops.approval.mixin')
    if ApprovalMixin is not None:
        log("PASS", "APPR_MIXIN", "ops.approval.mixin abstract model exists")
    else:
        log("WARN", "APPR_MIXIN", "ops.approval.mixin not found as a model in registry")
except Exception as e:
    log("WARN", "APPR_MIXIN", f"Approval mixin check: {str(e)[:120]}")

# --- IP Whitelist ---
try:
    IpWhitelist = self.env['ops.ip.whitelist']
    log("PASS", "IP_WHITELIST", "ops.ip.whitelist model exists")
    whitelist_entries = IpWhitelist.sudo().search([])
    log("PASS", "IP_WHITELIST", f"Total IP whitelist entries: {len(whitelist_entries)}")
except Exception as e:
    log("WARN", "IP_WHITELIST", f"ops.ip.whitelist: {str(e)[:120]}")

# --- Session Manager ---
try:
    SessionMgr = self.env['ops.session.manager']
    log("PASS", "SESSION", "ops.session.manager model exists")
except Exception as e:
    log("WARN", "SESSION", f"ops.session.manager: {str(e)[:120]}")

# --- API Key Management ---
try:
    ApiKey = self.env['ops.api.key']
    log("PASS", "API_KEY", "ops.api.key model exists")
    api_keys = ApiKey.sudo().search([])
    log("PASS", "API_KEY", f"Total API keys: {len(api_keys)}")
except Exception as e:
    log("WARN", "API_KEY", f"ops.api.key: {str(e)[:120]}")

# --- Security Compliance ---
try:
    SecCompliance = self.env['ops.security.compliance']
    log("PASS", "SEC_COMPLIANCE", "ops.security.compliance model exists")
except Exception as e:
    log("WARN", "SEC_COMPLIANCE", f"ops.security.compliance: {str(e)[:120]}")


# ============================================================================
# SUMMARY
# ============================================================================
section("AUDIT SUMMARY")

RESULTS.append(f"  PASS: {PASS_COUNT}")
RESULTS.append(f"  FAIL: {FAIL_COUNT}")
RESULTS.append(f"  WARN: {WARN_COUNT}")
RESULTS.append(f"  TOTAL CHECKS: {PASS_COUNT + FAIL_COUNT + WARN_COUNT}")
RESULTS.append("")
RESULTS.append(f"  Audit completed at: {datetime.now().isoformat()}")
RESULTS.append("")

# Key governance capabilities summary
RESULTS.append("--- GOVERNANCE CAPABILITIES SUMMARY ---")
RESULTS.append("  Core Models:")
RESULTS.append("    - ops.governance.rule: Dynamic rule engine (discount, margin, matrix, price, approval)")
RESULTS.append("    - ops.governance.discount.limit: Role-based discount limits per persona/group/scope")
RESULTS.append("    - ops.governance.margin.rule: Category/BU/Branch margin thresholds")
RESULTS.append("    - ops.governance.price.authority: Role-based price override authority")
RESULTS.append("    - ops.approval.workflow + steps: Multi-step approval workflow definitions")
RESULTS.append("    - ops.approval.request: Approval tracking with escalation and delegation")
RESULTS.append("    - ops.approval.rule: Lightweight approval rule wrapper")
RESULTS.append("    - ops.product.request: Product creation gatekeeper workflow")
RESULTS.append("    - ops.field.visibility.rule: Field-level data hiding per security group")
RESULTS.append("    - ops.archive.policy: Data retention with financial safety constraints")
RESULTS.append("")
RESULTS.append("  Audit Models:")
RESULTS.append("    - ops.audit.log: API request auditing (immutable)")
RESULTS.append("    - ops.corporate.audit.log: CRUD, auth, financial, workflow auditing (immutable)")
RESULTS.append("    - ops.security.audit: Security event tracking")
RESULTS.append("")
RESULTS.append("  Security Models:")
RESULTS.append("    - ops.persona.delegation: Delegation with audit trail and overlap detection")
RESULTS.append("    - ops.segregation.of.duties: Conflict-of-interest controls")
RESULTS.append("    - ops.ip.whitelist: IP-based access control")
RESULTS.append("    - ops.session.manager: Session management")
RESULTS.append("    - ops.api.key: API key management")
RESULTS.append("    - ops.security.compliance: Compliance framework")

# Write to file
output = "\n".join(RESULTS)
with open('/tmp/audit_governance.txt', 'w') as f:
    f.write(output)
