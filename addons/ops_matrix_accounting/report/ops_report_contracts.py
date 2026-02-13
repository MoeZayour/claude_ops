# -*- coding: utf-8 -*-
"""
OPS Report Data Contracts
=========================

Defines the three report data shapes used by all 29 OPS corporate reports:

- **Shape A (Lines)**: Grouped journal entry lines with running balances.
  Used by: GL, Partner Ledger, SOA, Cash Book, Day Book, Bank Book.

- **Shape B (Hierarchy)**: Recursive financial hierarchy with value columns.
  Used by: P&L, Balance Sheet, Cash Flow, Budget vs Actual, Consolidation reports.

- **Shape C (Matrix)**: Dynamic-column tabular data with row styling.
  Used by: Trial Balance, Aged Receivables/Payables, Asset, Treasury, Inventory reports.

Every wizard's ``_get_report_data()`` returns ``asdict(ShapeXReport(...))`` — a plain
nested dict that QWeb templates can consume directly.

Helper functions ``build_report_meta()`` and ``build_report_colors()`` standardize
metadata extraction from any wizard instance.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import date, datetime

from odoo import fields as odoo_fields


# ============================================================================
# Common Metadata
# ============================================================================

@dataclass
class ReportMeta:
    """Common metadata block present in all report shapes."""
    report_type: str           # 'gl', 'tb', 'pl', 'bs', 'cf', etc.
    report_title: str          # Human-readable: "General Ledger"
    shape: str                 # 'lines', 'hierarchy', 'matrix'
    company_name: str
    company_vat: str = ''
    company_logo: str = ''     # Base64 or URL
    currency_symbol: str = ''
    currency_name: str = ''
    currency_position: str = 'before'  # 'before' or 'after'
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    as_of_date: Optional[str] = None
    generated_at: str = ''     # ISO datetime string
    generated_by: str = ''     # User display name
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportColors:
    """Company branding colors for report rendering."""
    primary: str = '#5B6BBB'
    primary_dark: str = '#44508c'
    primary_light: str = '#edeef5'
    text_on_primary: str = '#FFFFFF'
    body_text: str = '#1a1a1a'
    success: str = '#059669'
    danger: str = '#dc2626'
    warning: str = '#d97706'
    zero: str = '#94a3b8'
    border: str = '#e5e7eb'


# ============================================================================
# Shape A — Line-Based Reports
# ============================================================================

@dataclass
class LineEntry:
    """Single journal entry line for Shape A reports."""
    date: str
    entry: str            # Move name (JV/2026/0001)
    journal: str          # Journal code
    account_code: str
    account_name: str
    label: str            # Line narration
    ref: str = ''
    partner: str = ''
    branch: str = ''
    bu: str = ''
    debit: float = 0.0
    credit: float = 0.0
    balance: float = 0.0   # Running balance (cumulative within group)
    currency: str = ''      # Foreign currency code
    amount_currency: float = 0.0
    reconciled: bool = False


@dataclass
class LineGroup:
    """Group of lines (by account, partner, bank, etc.) for Shape A."""
    group_key: str        # Account code, partner ref, bank name
    group_name: str       # Display name
    group_meta: Dict[str, Any] = field(default_factory=dict)
    opening_balance: float = 0.0
    lines: List[LineEntry] = field(default_factory=list)
    total_debit: float = 0.0
    total_credit: float = 0.0
    closing_balance: float = 0.0


@dataclass
class ShapeAReport:
    """Complete line-based report data contract (Shape A)."""
    meta: ReportMeta = None
    colors: ReportColors = None
    groups: List[LineGroup] = field(default_factory=list)
    grand_totals: Dict[str, float] = field(default_factory=dict)
    visible_columns: List[str] = field(default_factory=lambda: [
        'date', 'entry', 'journal', 'account_code', 'account_name',
        'label', 'partner', 'branch', 'bu', 'debit', 'credit', 'balance'
    ])


# ============================================================================
# Shape B — Hierarchy-Based Reports
# ============================================================================

@dataclass
class HierarchyNode:
    """Single node in a financial hierarchy (Shape B).

    Recursive: each node can contain children of the same type.
    """
    code: str = ''
    name: str = ''
    level: int = 0          # 0=section, 1=group, 2=account, 3=detail
    style: str = 'detail'   # 'section' | 'group' | 'detail' | 'total' | 'grand_total'
    values: Dict[str, float] = field(default_factory=dict)
    children: List['HierarchyNode'] = field(default_factory=list)


@dataclass
class ShapeBReport:
    """Complete hierarchy-based report data contract (Shape B)."""
    meta: ReportMeta = None
    colors: ReportColors = None
    value_columns: List[Dict[str, str]] = field(default_factory=list)
    sections: List[HierarchyNode] = field(default_factory=list)
    net_result: Optional[HierarchyNode] = None


# ============================================================================
# Shape C — Matrix/Table-Based Reports
# ============================================================================

@dataclass
class ColumnDef:
    """Dynamic column definition for Shape C reports."""
    key: str              # Dict key in row values
    label: str            # Header display text
    col_type: str = 'string'  # 'string' | 'number' | 'currency' | 'date' | 'percentage'
    width: int = 0        # Relative width hint (0 = auto)
    align: str = 'left'   # 'left' | 'center' | 'right'
    subtotal: bool = False # Include in subtotals


@dataclass
class MatrixRow:
    """Single row in a matrix report (Shape C)."""
    level: int = 0        # For indentation / grouping
    style: str = 'detail' # 'header' | 'detail' | 'subtotal' | 'total' | 'grand_total'
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShapeCReport:
    """Complete matrix/table-based report data contract (Shape C)."""
    meta: ReportMeta = None
    colors: ReportColors = None
    columns: List[ColumnDef] = field(default_factory=list)
    rows: List[MatrixRow] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Helper Functions
# ============================================================================

def build_report_meta(wizard, report_type, report_title, shape):
    """Build standard ReportMeta from any wizard instance.

    Dynamically inspects the wizard for filter fields and extracts
    company/currency info.

    Args:
        wizard: Report wizard recordset (single record)
        report_type: Short code ('gl', 'tb', 'pl', etc.)
        report_title: Human-readable title
        shape: 'lines', 'hierarchy', or 'matrix'

    Returns:
        ReportMeta dataclass instance
    """
    company = wizard.company_id
    currency = company.currency_id

    # Build filter dict dynamically from wizard fields
    filters = {}
    filter_fields = [
        ('branch_ids', 'branches', 'name'),
        ('business_unit_ids', 'business_units', 'name'),
        ('journal_ids', 'journals', 'name'),
        ('account_ids', 'accounts', 'display_name'),
        ('partner_ids', 'partners', 'name'),
        ('warehouse_ids', 'warehouses', 'name'),
        ('product_category_ids', 'product_categories', 'display_name'),
    ]
    for field_name, filter_key, mapped_attr in filter_fields:
        if hasattr(wizard, field_name):
            field_val = getattr(wizard, field_name)
            if field_val:
                filters[filter_key] = field_val.mapped(mapped_attr)

    if hasattr(wizard, 'target_move') and wizard.target_move:
        filters['target_move'] = 'All Entries' if wizard.target_move == 'all' else 'Posted Only'
    if hasattr(wizard, 'partner_type') and wizard.partner_type:
        filters['partner_type'] = wizard.partner_type

    # Date fields
    date_from = None
    date_to = None
    as_of_date = None

    if hasattr(wizard, 'date_from') and wizard.date_from:
        date_from = str(wizard.date_from)
    if hasattr(wizard, 'date_to') and wizard.date_to:
        date_to = str(wizard.date_to)
    if hasattr(wizard, 'as_of_date') and wizard.as_of_date:
        as_of_date = str(wizard.as_of_date)

    # Company logo
    company_logo = ''
    if company.logo:
        company_logo = company.logo.decode('utf-8') if isinstance(company.logo, bytes) else str(company.logo)

    return ReportMeta(
        report_type=report_type,
        report_title=report_title,
        shape=shape,
        company_name=company.name or '',
        company_vat=company.vat or '',
        company_logo=company_logo,
        currency_symbol=currency.symbol or '',
        currency_name=currency.name or '',
        currency_position=currency.position or 'before',
        date_from=date_from,
        date_to=date_to,
        as_of_date=as_of_date,
        generated_at=odoo_fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        generated_by=wizard.env.user.name or '',
        filters=filters,
    )


def build_report_colors(company):
    """Build ReportColors from company report color settings.

    Reads ops_report_primary_color, ops_report_text_on_primary, and
    ops_report_body_text_color from the company, then computes derived
    light/dark variants.

    Args:
        company: res.company recordset (single record)

    Returns:
        ReportColors dataclass instance
    """
    primary = (getattr(company, 'ops_report_primary_color', None) or '#5B6BBB').strip()

    # Get derived colors with safe fallbacks
    try:
        primary_dark = company.get_report_primary_dark()
    except Exception:
        primary_dark = '#44508c'

    try:
        primary_light = company.get_report_primary_light()
    except Exception:
        primary_light = '#edeef5'

    text_on_primary = (getattr(company, 'ops_report_text_on_primary', None) or '#FFFFFF').strip()
    body_text = (getattr(company, 'ops_report_body_text_color', None) or '#1a1a1a').strip()

    return ReportColors(
        primary=primary,
        primary_dark=primary_dark,
        primary_light=primary_light,
        text_on_primary=text_on_primary,
        body_text=body_text,
    )


def to_dict(dataclass_instance):
    """Convert a dataclass instance to a plain dict for QWeb consumption.

    Wrapper around ``dataclasses.asdict()`` that handles None values cleanly.
    QWeb templates cannot consume Python dataclass objects directly — they need
    plain dicts.

    Args:
        dataclass_instance: Any dataclass instance (ShapeAReport, etc.)

    Returns:
        dict: Plain nested dict matching the dataclass structure
    """
    if dataclass_instance is None:
        return {}
    return asdict(dataclass_instance)
