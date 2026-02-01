# -*- coding: utf-8 -*-
from odoo import models, api


class OpsFinancialReportParser(models.AbstractModel):
    """Financial Report Parser - Fixed for Odoo 19 CE.

    v19.4.0: Added dynamic company color support for branded reports.
    Colors are derived from res.company primary_color and secondary_color fields,
    allowing each company to have their branded financial reports.
    """
    _name = 'report.ops_matrix_accounting.report_ops_financial_document'
    _description = 'Financial Report Parser'

    # ============================================
    # MERIDIAN DESIGN SYSTEM COLOR TOKENS
    # ============================================
    # The "Meridian Standard" - Management Consulting aesthetic
    # High contrast, executive-grade color palette
    MERIDIAN_COLORS = {
        # Primary Colors
        'gold': '#C9A962',          # Executive Gold - Brand accent
        'black': '#1A1A1A',         # Primary Black - Text & headers
        'red': '#DA291C',           # Corporate Red - Negatives & alerts

        # Semantic Colors
        'success': '#059669',       # Emerald green - Positive values
        'danger': '#DA291C',        # Red - Negative values
        'warning': '#d97706',       # Amber - Warnings
        'info': '#2563eb',          # Blue - Information

        # Neutral Palette
        'muted': '#FAFAFA',         # Muted Grey - Backgrounds
        'zero': '#cccccc',          # Light Grey - Zero values
        'border': '#e5e7eb',        # Border color
        'text': '#1A1A1A',          # Primary text
        'text_secondary': '#6b7280', # Secondary text

        # Section Colors (Balance Sheet/P&L)
        'asset': '#2563eb',         # Blue - Assets
        'liability': '#d97706',     # Orange - Liabilities
        'equity': '#059669',        # Green - Equity
        'revenue': '#059669',       # Green - Revenue
        'expense': '#DA291C',       # Red - Expenses
    }

    def _get_company_colors(self, company):
        """
        Get company branding colors with intelligent fallbacks.

        MERIDIAN STANDARD: If no company color is set, defaults to
        Executive Gold (#C9A962) as the primary brand accent.

        Returns a dict with:
        - primary: Main brand color (used for headers, titles)
        - secondary: Accent color (used for highlights)
        - success: Green for positive values
        - danger: Red for negative values
        - muted: Gray for zero/neutral values
        - text: Primary text color
        - text_secondary: Secondary text color
        - border: Border color
        - background: Background color
        """
        # MERIDIAN STANDARD - Professional color palette
        # Default to Executive Gold (#C9A962) for brand accent
        colors = {
            'primary': '#C9A962',        # MERIDIAN GOLD - Executive accent
            'secondary': '#1A1A1A',      # Primary Black - Headers
            'success': '#059669',        # Emerald green - Positive values
            'danger': '#DA291C',         # Corporate Red - Negatives
            'warning': '#d97706',        # Amber - Warning
            'muted': '#cccccc',          # Light Grey - Zero values
            'zero': '#cccccc',           # Light Grey - Zero values (explicit)
            'text': '#1A1A1A',           # Primary Black - Text
            'text_secondary': '#6b7280', # Secondary text
            'border': '#e5e7eb',         # Border color
            'background': '#FAFAFA',     # Muted Grey - Backgrounds
            'white': '#ffffff',
            # Section colors for financial reports
            'asset': '#2563eb',          # Blue - Assets
            'liability': '#d97706',      # Orange - Liabilities
            'equity': '#059669',         # Green - Equity
            'revenue': '#059669',        # Green - Revenue
            'expense': '#DA291C',        # Red - Expenses
        }

        if company:
            # Get company primary/secondary colors (optional branding override)
            primary = company.primary_color
            secondary = company.secondary_color

            if primary:
                # Company has custom branding - use it
                colors['primary'] = primary
                colors['primary_dark'] = self._darken_color(primary, 0.2)
            else:
                # MERIDIAN DEFAULT: Executive Gold with dark variant
                colors['primary_dark'] = '#9A7A42'  # Darker gold

            if secondary:
                colors['secondary'] = secondary
            # Else keep Meridian Black as secondary
        else:
            # No company - use full Meridian defaults
            colors['primary_dark'] = '#9A7A42'  # Darker gold

        # Always include Meridian constants for template access
        colors['meridian_gold'] = '#C9A962'
        colors['meridian_black'] = '#1A1A1A'
        colors['meridian_red'] = '#DA291C'

        return colors

    def _darken_color(self, hex_color, factor=0.2):
        """Darken a hex color by a factor (0-1)."""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            return f'#{r:02x}{g:02x}{b:02x}'
        except (ValueError, IndexError):
            return '#0a1628'  # Fallback to dark navy

    def _lighten_color(self, hex_color, factor=0.2):
        """Lighten a hex color by a factor (0-1)."""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            return f'#{r:02x}{g:02x}{b:02x}'
        except (ValueError, IndexError):
            return '#f8fafc'  # Fallback to light gray

    def _format_value(self, value, include_sign=True, decimals=2):
        """
        Format a numeric value according to the Meridian Standard.

        MERIDIAN VALUE DISPLAY RULES:
        - Zeros: Display as "0.00" with color class 'zero'
        - Negatives: Red (#DA291C) with parentheses, e.g., "(1,234.56)"
        - Positives: Black (#1A1A1A), e.g., "1,234.56"

        Returns a dict with:
        - formatted: The formatted string
        - css_class: CSS class to apply (zero, negative, positive)
        - raw: Original numeric value (passed through, never filtered)
        """
        # CRITICAL: Never filter out zero values - pass them through
        if value is None:
            value = 0.0

        format_str = f"{{:,.{decimals}f}}"

        if value == 0:
            return {
                'formatted': format_str.format(0),
                'css_class': 'ops-value-zero',
                'color': '#cccccc',
                'raw': 0.0,
                'is_zero': True,
            }
        elif value < 0:
            if include_sign:
                formatted = f"({format_str.format(abs(value))})"
            else:
                formatted = format_str.format(abs(value))
            return {
                'formatted': formatted,
                'css_class': 'ops-value-negative',
                'color': '#DA291C',
                'raw': value,
                'is_zero': False,
            }
        else:
            return {
                'formatted': format_str.format(value),
                'css_class': 'ops-value-positive',
                'color': '#000000',
                'raw': value,
                'is_zero': False,
            }

    def _calculate_variance(self, current, prior):
        """
        Calculate variance between current and prior period values.

        MERIDIAN VARIANCE DISPLAY:
        - Positive variance (improvement): Green with up arrow
        - Negative variance (decline): Red with down arrow
        - Zero/minimal change: Grey

        Returns dict with:
        - amount: Absolute variance
        - percentage: Percentage change
        - direction: 'up', 'down', or 'flat'
        - css_class: Styling class
        """
        if prior is None:
            prior = 0.0
        if current is None:
            current = 0.0

        variance_amount = current - prior

        # Calculate percentage (handle division by zero)
        if prior != 0:
            variance_pct = ((current - prior) / abs(prior)) * 100
        elif current != 0:
            variance_pct = 100.0  # New value from zero
        else:
            variance_pct = 0.0

        # Determine direction
        if abs(variance_pct) < 0.5:  # Less than 0.5% = flat
            direction = 'flat'
            css_class = 'ops-variance-neutral'
        elif variance_amount > 0:
            direction = 'up'
            css_class = 'ops-variance-positive'
        else:
            direction = 'down'
            css_class = 'ops-variance-negative'

        return {
            'amount': variance_amount,
            'formatted_amount': self._format_value(variance_amount),
            'percentage': variance_pct,
            'formatted_pct': f"{variance_pct:+.1f}%",
            'direction': direction,
            'css_class': css_class,
            'trend_class': f"ops-trend-{direction}",
        }

    def _calculate_ratio(self, numerator, denominator, as_percentage=True):
        """
        Calculate a financial ratio with proper handling.

        MERIDIAN RATIO DISPLAY:
        - Formatted with appropriate precision
        - Color-coded based on threshold brackets
        """
        if denominator is None or denominator == 0:
            return {
                'value': 0.0,
                'formatted': 'N/A',
                'css_class': 'ops-variance-neutral',
            }

        ratio = (numerator or 0) / denominator
        if as_percentage:
            ratio *= 100
            formatted = f"{ratio:.1f}%"
        else:
            formatted = f"{ratio:.2f}"

        # Determine status based on value
        if ratio >= 20:
            css_class = 'ops-variance-positive'
            status = 'excellent'
        elif ratio >= 10:
            css_class = 'ops-variance-positive'
            status = 'healthy'
        elif ratio >= 5:
            css_class = 'ops-variance-neutral'
            status = 'acceptable'
        elif ratio >= 0:
            css_class = 'ops-variance-neutral'
            status = 'low'
        else:
            css_class = 'ops-variance-negative'
            status = 'loss'

        return {
            'value': ratio,
            'formatted': formatted,
            'css_class': css_class,
            'status': status,
        }

    def _get_aging_buckets(self, days_overdue):
        """
        Categorize a value into aging buckets.

        MERIDIAN AGING BUCKETS:
        - Current (0-30 days): Green
        - 31-60 days: Blue
        - 61-90 days: Yellow/Warning
        - 91-120 days: Orange
        - Over 120 days: Red/Critical
        """
        if days_overdue <= 0:
            return {'bucket': 'current', 'label': 'Current', 'css_class': 'ops-aging-current'}
        elif days_overdue <= 30:
            return {'bucket': '1-30', 'label': '1-30 Days', 'css_class': 'ops-aging-current'}
        elif days_overdue <= 60:
            return {'bucket': '31-60', 'label': '31-60 Days', 'css_class': 'ops-aging-30'}
        elif days_overdue <= 90:
            return {'bucket': '61-90', 'label': '61-90 Days', 'css_class': 'ops-aging-60'}
        elif days_overdue <= 120:
            return {'bucket': '91-120', 'label': '91-120 Days', 'css_class': 'ops-aging-90'}
        else:
            return {'bucket': 'over120', 'label': '120+ Days', 'css_class': 'ops-aging-over'}

    def _get_margin_status(self, margin_pct):
        """
        Get margin status classification for display.

        MERIDIAN MARGIN THRESHOLDS:
        - >= 20%: Excellent (Green)
        - >= 10%: Healthy (Blue)
        - >= 5%: Acceptable (Grey)
        - >= 0%: Low (Warning)
        - < 0%: Loss (Red)
        """
        if margin_pct >= 20:
            return {
                'status': 'excellent',
                'label': 'Excellent',
                'css_class': 'ops-status-pill excellent',
                'color': '#059669',
                'bg_color': '#d1fae5',
                'border_color': '#059669',
            }
        elif margin_pct >= 10:
            return {
                'status': 'healthy',
                'label': 'Healthy',
                'css_class': 'ops-status-pill healthy',
                'color': '#2563eb',
                'bg_color': '#dbeafe',
                'border_color': '#2563eb',
            }
        elif margin_pct >= 5:
            return {
                'status': 'acceptable',
                'label': 'Acceptable',
                'css_class': 'ops-status-pill acceptable',
                'color': '#4b5563',
                'bg_color': '#f3f4f6',
                'border_color': '#6b7280',
            }
        elif margin_pct >= 0:
            return {
                'status': 'low',
                'label': 'Low',
                'css_class': 'ops-status-pill warning',
                'color': '#d97706',
                'bg_color': '#fef3c7',
                'border_color': '#d97706',
            }
        else:
            return {
                'status': 'loss',
                'label': 'Loss',
                'css_class': 'ops-status-pill loss',
                'color': '#DA291C',
                'bg_color': '#fee2e2',
                'border_color': '#DA291C',
            }

    def _get_balance_sheet_equation(self, assets, liabilities, equity):
        """
        Validate the accounting equation: Assets = Liabilities + Equity

        MERIDIAN STANDARD: The Balance Sheet MUST balance.
        Returns a dict with verification status and display values.
        """
        # Ensure proper sign handling (liabilities and equity are typically credit balances)
        liab_equity_total = abs(liabilities) + abs(equity)
        difference = assets - liab_equity_total
        is_balanced = abs(difference) < 0.01  # Allow for rounding

        return {
            'assets': assets,
            'liabilities': abs(liabilities),
            'equity': abs(equity),
            'liab_plus_equity': liab_equity_total,
            'difference': difference,
            'is_balanced': is_balanced,
            'status_class': 'balanced' if is_balanced else 'unbalanced',
            'status_text': 'Balanced' if is_balanced else f'Difference: {difference:,.2f}',
            'status_icon': '✓' if is_balanced else '✗',
        }

    def _get_pnl_kpis(self, revenue, cogs, expenses, net_profit):
        """
        Calculate P&L KPIs for the Meridian Standard reports.

        Returns a dict with:
        - Gross margin %
        - Operating margin %
        - Net profit margin %
        - Status indicators
        """
        gross_profit = revenue - cogs if cogs else revenue
        operating_profit = gross_profit - (expenses - cogs) if cogs else revenue - expenses

        # Calculate margins
        gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
        operating_margin = (operating_profit / revenue * 100) if revenue > 0 else 0
        net_margin = (net_profit / revenue * 100) if revenue > 0 else 0

        return {
            'revenue': self._format_value(revenue),
            'gross_profit': self._format_value(gross_profit),
            'operating_profit': self._format_value(operating_profit),
            'net_profit': self._format_value(net_profit),
            'gross_margin': {
                'value': gross_margin,
                'formatted': f'{gross_margin:.1f}%',
                'status': self._get_margin_status(gross_margin),
            },
            'operating_margin': {
                'value': operating_margin,
                'formatted': f'{operating_margin:.1f}%',
                'status': self._get_margin_status(operating_margin),
            },
            'net_margin': {
                'value': net_margin,
                'formatted': f'{net_margin:.1f}%',
                'status': self._get_margin_status(net_margin),
            },
        }

    def _get_cash_flow_summary(self, operating, investing, financing, opening_cash=0):
        """
        Calculate Cash Flow summary for the Meridian Standard 3-section layout.

        Returns a dict with section totals and overall cash position.
        """
        net_change = operating + investing + financing
        closing_cash = opening_cash + net_change

        # Determine cash flow health
        if net_change > 0:
            status = 'positive'
            status_class = 'ops-variance-positive'
        elif net_change < 0:
            status = 'negative'
            status_class = 'ops-variance-negative'
        else:
            status = 'neutral'
            status_class = 'ops-variance-neutral'

        return {
            'operating_net': self._format_value(operating),
            'investing_net': self._format_value(investing),
            'financing_net': self._format_value(financing),
            'net_change': self._format_value(net_change),
            'opening_cash': self._format_value(opening_cash),
            'closing_cash': self._format_value(closing_cash),
            'status': status,
            'status_class': status_class,
            'raw': {
                'operating': operating,
                'investing': investing,
                'financing': financing,
                'net_change': net_change,
                'opening_cash': opening_cash,
                'closing_cash': closing_cash,
            },
        }

    def _build_hierarchy(self, lines, parent_field='parent_id', sort_by='code'):
        """
        Build hierarchical structure from flat account list.

        Used for Chart of Accounts display with proper indentation.
        Returns list of dicts with 'level' field indicating depth.
        """
        if not lines:
            return []

        # Group by parent
        by_parent = {}
        root_items = []

        for line in lines:
            parent_id = line.get(parent_field)
            if parent_id:
                if parent_id not in by_parent:
                    by_parent[parent_id] = []
                by_parent[parent_id].append(line)
            else:
                root_items.append(line)

        # Sort root items
        if sort_by:
            root_items.sort(key=lambda x: x.get(sort_by, ''))

        # Build flattened hierarchy
        result = []

        def add_with_children(item, level=0):
            item['level'] = level
            item['row_class'] = f"level-{level}"
            result.append(item)

            # Add children
            item_id = item.get('id') or item.get('account_id')
            if item_id and item_id in by_parent:
                children = by_parent[item_id]
                if sort_by:
                    children.sort(key=lambda x: x.get(sort_by, ''))
                for child in children:
                    add_with_children(child, level + 1)

        for root in root_items:
            add_with_children(root)

        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        # If data contains report data directly (from enhanced wizard), use it
        if data and isinstance(data, dict) and 'report_type' in data:
            # Data was passed directly - transform it for the template
            report_data = self._transform_enhanced_data(None, data)
            # Get wizard for docs - try multiple sources
            active_model = self.env.context.get('active_model', 'ops.general.ledger.wizard.enhanced')
            wizard = None

            # Try docids first
            if docids:
                if active_model == 'ops.general.ledger.wizard.enhanced':
                    wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
                else:
                    wizard = self.env['ops.financial.report.wizard'].browse(docids)

            # If no wizard from docids, try active_id from context
            if not wizard or not wizard.exists():
                active_id = self.env.context.get('active_id')
                active_ids = self.env.context.get('active_ids', [])
                if active_id:
                    wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(active_id)
                elif active_ids:
                    wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(active_ids[0])

            # If still no wizard, try wizard_id from data
            if (not wizard or not wizard.exists()) and data.get('wizard_id'):
                wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(data.get('wizard_id'))

            # Create a dummy wizard context if all else fails - the template needs docs for iteration
            if not wizard or not wizard.exists():
                # Create a mock object for template iteration with report_type from data
                class MockWizard:
                    def __init__(self, report_type):
                        self.report_type = report_type
                        self.id = False
                mock_wizard = MockWizard(data.get('report_type', 'gl'))
                return {
                    'doc_ids': docids or [],
                    'doc_model': active_model,
                    'docs': [mock_wizard],  # List with one element for template iteration
                    'report_data': report_data,
                }

            return {
                'doc_ids': docids,
                'doc_model': active_model,
                'docs': wizard,
                'report_data': report_data,
            }

        # Detect which wizard model to use based on context
        active_model = self.env.context.get('active_model', 'ops.financial.report.wizard')

        # Try enhanced wizard first if indicated
        if active_model == 'ops.general.ledger.wizard.enhanced':
            wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
            if wizard.exists():
                return self._get_enhanced_wizard_values(wizard, docids, data)

        # Fall back to original wizard
        wizard = self.env['ops.financial.report.wizard'].browse(docids)
        if not wizard.exists():
            wizard = self.env['ops.financial.report.wizard'].browse(
                self.env.context.get('active_id')
            )

        # If still no wizard found, try enhanced wizard
        if not wizard.exists():
            wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
            if wizard.exists():
                return self._get_enhanced_wizard_values(wizard, docids, data)

        # If no wizard found at all, return empty data
        if not wizard.exists():
            return {
                'doc_ids': docids,
                'doc_model': active_model,
                'docs': wizard,
                'report_data': {},
            }

        report_data = self._get_report_data(wizard)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.financial.report.wizard',
            'docs': wizard,
            'report_data': report_data,
        }

    def _get_enhanced_wizard_values(self, wizard, docids, data=None):
        """Get report values for the enhanced wizard."""
        # If data was passed, use it; otherwise generate from wizard
        if data and isinstance(data, dict) and 'report_type' in data:
            raw_data = data
        else:
            raw_data = wizard._get_report_data()

        # Transform to template format
        report_data = self._transform_enhanced_data(wizard, raw_data)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.general.ledger.wizard.enhanced',
            'docs': wizard,
            'report_data': report_data,
        }

    def _transform_enhanced_data(self, wizard, data):
        """Transform enhanced wizard data to template format."""
        if not data:
            return {}

        report_type = data.get('report_type', 'gl')

        # Get company for colors
        company = None
        if wizard and hasattr(wizard, 'company_id') and wizard.company_id:
            company = wizard.company_id
        else:
            company = self.env.company

        # Get dynamic company colors
        colors = self._get_company_colors(company)

        result = {
            'title': data.get('report_title', 'Financial Report'),
            'company': data.get('company_name', '') or (company.name if company else ''),
            'branch': ', '.join(data.get('filters', {}).get('branch_names', [])) or 'All Branches',
            'user': self.env.user.name,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
            'target_move': data.get('filters', {}).get('target_move', 'posted'),
            'currency_symbol': company.currency_id.symbol if company else '',
            # Dynamic company colors
            'colors': colors,
        }

        if report_type == 'gl':
            result.update(self._transform_gl_from_enhanced(data))
        elif report_type == 'pl':
            result.update(self._transform_pl_from_enhanced(data))
        elif report_type == 'bs':
            result.update(self._transform_bs_from_enhanced(data))
        elif report_type == 'tb':
            result.update(self._transform_tb_from_enhanced(data))
        elif report_type == 'cf':
            result.update(self._transform_cf_from_enhanced(data))
        elif report_type == 'aged':
            result.update(self._transform_aged_from_enhanced(data))
        elif report_type in ('partner', 'soa'):
            result.update(self._transform_partner_from_enhanced(data))

        return result

    def _transform_gl_from_enhanced(self, data):
        """Transform GL data from enhanced wizard."""
        lines = []
        report_data = data.get('data', [])
        if isinstance(report_data, dict):
            detailed = report_data.get('detailed', report_data.get('summary', []))
        else:
            detailed = report_data

        for line in detailed:
            lines.append({
                'date': line.get('date', ''),
                'move_name': line.get('move_name', ''),
                'move_id': line.get('move_id'),
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'partner': line.get('partner_name', ''),
                'label': line.get('name', ''),
                'debit': line.get('debit', 0),
                'credit': line.get('credit', 0),
                'balance': line.get('balance', 0),
            })
        return {'headers': ['Date', 'Entry', 'Account', 'Partner', 'Label', 'Debit', 'Credit', 'Balance'], 'lines': lines}

    def _transform_pl_from_enhanced(self, data):
        """
        Transform P&L data from enhanced wizard.
        Phase 14: Now supports hierarchical CoA structure for audit-grade reports.
        """
        # Check if hierarchical data is available (Phase 14)
        hierarchy = data.get('hierarchy', {})
        use_hierarchy = data.get('use_hierarchy', False)

        if use_hierarchy and hierarchy:
            # Phase 14: Return hierarchical structure
            income_hierarchy = hierarchy.get('income_hierarchy', [])
            expense_hierarchy = hierarchy.get('expense_hierarchy', [])

            # Also build flat lists for backward compatibility
            income_lines = []
            expense_lines = []

            for line in income_hierarchy:
                if line.get('type') == 'account':
                    income_lines.append({
                        'account': f"{line.get('code', '')} - {line.get('name', '')}",
                        'amount': abs(line.get('balance', 0)),
                    })

            for line in expense_hierarchy:
                if line.get('type') == 'account':
                    expense_lines.append({
                        'account': f"{line.get('code', '')} - {line.get('name', '')}",
                        'amount': abs(line.get('balance', 0)),
                    })

            summary = data.get('summary', {})
            total_income = summary.get('total_income', hierarchy.get('income_total', 0))
            total_expense = summary.get('total_expense', hierarchy.get('expense_total', 0))
            cogs_total = summary.get('cogs_total', 0)
            net_profit = summary.get('net_income', hierarchy.get('net_profit', 0))

            # Calculate margin and get status
            margin_pct = (net_profit / total_income * 100) if total_income > 0 else 0
            margin_status = self._get_margin_status(margin_pct)

            # Get P&L KPIs using the helper
            pnl_kpis = self._get_pnl_kpis(total_income, cogs_total, total_expense, net_profit)

            return {
                'headers': ['Code', 'Account', 'Amount'],
                # Phase 14: Hierarchical data for audit-grade rendering
                'income_hierarchy': income_hierarchy,
                'expense_hierarchy': expense_hierarchy,
                'use_hierarchy': True,
                # Flat lines for backward compatibility
                'income_lines': income_lines,
                'expense_lines': expense_lines,
                'income_total': total_income,
                'expense_total': total_expense,
                'cogs_total': cogs_total,
                'gross_profit': summary.get('gross_profit', 0),
                'net_profit': net_profit,
                'lines': income_lines + expense_lines,
                # Meridian Standard: Margin analysis
                'margin_pct': margin_pct,
                'margin_status': margin_status,
                'margin_formatted': self._format_value(net_profit),
                'pnl_kpis': pnl_kpis,
            }

        # Original flat structure (backward compatibility)
        income_lines, expense_lines = [], []
        income_total, expense_total, cogs_total = 0, 0, 0

        for section in data.get('sections', []):
            section_type = section.get('type', '')
            for acc in section.get('accounts', []):
                line = {
                    'account': f"{acc.get('account_code', '')} - {acc.get('account_name', '')}",
                    'account_id': acc.get('account_id'),
                    'amount': abs(acc.get('balance', 0)),
                }
                if 'income' in section_type:
                    income_lines.append(line)
                    income_total += line['amount']
                elif 'expense' in section_type:
                    expense_lines.append(line)
                    expense_total += line['amount']
                    if 'direct_cost' in section_type:
                        cogs_total += line['amount']

        summary = data.get('summary', {})
        net_profit = summary.get('net_income', income_total - expense_total)
        total_income = summary.get('total_income', income_total)
        total_expense = summary.get('total_expense', expense_total)

        # Calculate margin and get status
        margin_pct = (net_profit / total_income * 100) if total_income > 0 else 0
        margin_status = self._get_margin_status(margin_pct)

        # Get P&L KPIs using the helper
        pnl_kpis = self._get_pnl_kpis(total_income, cogs_total, total_expense, net_profit)

        return {
            'headers': ['Account', 'Amount'],
            'income_lines': income_lines,
            'expense_lines': expense_lines,
            'income_total': total_income,
            'expense_total': total_expense,
            'cogs_total': cogs_total,
            'gross_profit': total_income - cogs_total,
            'net_profit': net_profit,
            'lines': income_lines + expense_lines,
            'use_hierarchy': False,
            # Meridian Standard: Margin analysis
            'margin_pct': margin_pct,
            'margin_status': margin_status,
            'margin_formatted': self._format_value(net_profit),
            'pnl_kpis': pnl_kpis,
        }

    def _transform_bs_from_enhanced(self, data):
        """
        Transform Balance Sheet data from enhanced wizard.
        Phase 14: Now supports hierarchical CoA structure for audit-grade reports.
        """
        # Check if hierarchical data is available (Phase 14)
        hierarchy = data.get('hierarchy', {})
        use_hierarchy = data.get('use_hierarchy', False)

        if use_hierarchy and hierarchy:
            # Phase 14: Return hierarchical structure
            asset_hierarchy = hierarchy.get('asset_hierarchy', [])
            liability_hierarchy = hierarchy.get('liability_hierarchy', [])
            equity_hierarchy = hierarchy.get('equity_hierarchy', [])

            # Also build flat lists for backward compatibility
            asset_lines, liability_lines, equity_lines = [], [], []

            for line in asset_hierarchy:
                if line.get('type') == 'account':
                    asset_lines.append({
                        'account': f"{line.get('code', '')} - {line.get('name', '')}",
                        'amount': line.get('balance', 0),
                    })

            for line in liability_hierarchy:
                if line.get('type') == 'account':
                    liability_lines.append({
                        'account': f"{line.get('code', '')} - {line.get('name', '')}",
                        'amount': abs(line.get('balance', 0)),
                    })

            for line in equity_hierarchy:
                if line.get('type') == 'account':
                    equity_lines.append({
                        'account': f"{line.get('code', '')} - {line.get('name', '')}",
                        'amount': abs(line.get('balance', 0)),
                    })

            summary = data.get('summary', {})
            asset_total = summary.get('total_assets', hierarchy.get('asset_total', 0))
            liability_total = summary.get('total_liabilities', hierarchy.get('liability_total', 0))
            equity_total = summary.get('total_equity', hierarchy.get('equity_total', 0))

            # Meridian Standard: Accounting equation check
            # Assets = Liabilities + Equity
            balance_check = asset_total - (abs(liability_total) + abs(equity_total))
            is_balanced = abs(balance_check) < 0.01

            # Get equation verification using the helper
            equation = self._get_balance_sheet_equation(asset_total, liability_total, equity_total)

            return {
                'headers': ['Code', 'Account', 'Amount'],
                # Phase 14: Hierarchical data for audit-grade rendering
                'asset_hierarchy': asset_hierarchy,
                'liability_hierarchy': liability_hierarchy,
                'equity_hierarchy': equity_hierarchy,
                'use_hierarchy': True,
                # Flat lines for backward compatibility
                'asset_lines': asset_lines,
                'liability_lines': liability_lines,
                'equity_lines': equity_lines,
                'asset_total': asset_total,
                'liability_total': liability_total,
                'equity_total': equity_total,
                'lines': asset_lines + liability_lines + equity_lines,
                # Meridian Standard: Balance verification
                'equation': equation,
                'balance_check': equation['difference'],
                'is_balanced': equation['is_balanced'],
                'liab_plus_equity': equation['liab_plus_equity'],
            }

        # Original flat structure (backward compatibility)
        asset_lines, liability_lines, equity_lines = [], [], []

        for section in data.get('sections', []):
            section_type = section.get('type', '')
            for acc in section.get('accounts', []):
                line = {
                    'account': f"{acc.get('account_code', '')} - {acc.get('account_name', '')}",
                    'amount': acc.get('balance', 0)
                }
                if section_type.startswith('asset'):
                    asset_lines.append(line)
                elif section_type.startswith('liability'):
                    liability_lines.append(line)
                elif section_type.startswith('equity'):
                    equity_lines.append(line)

        summary = data.get('summary', {})
        asset_total = summary.get('total_assets', 0)
        liability_total = summary.get('total_liabilities', 0)
        equity_total = summary.get('total_equity', 0)

        # Meridian Standard: Accounting equation check using helper
        equation = self._get_balance_sheet_equation(asset_total, liability_total, equity_total)

        return {
            'headers': ['Account', 'Amount'],
            'asset_lines': asset_lines,
            'liability_lines': liability_lines,
            'equity_lines': equity_lines,
            'asset_total': asset_total,
            'liability_total': liability_total,
            'equity_total': equity_total,
            'lines': asset_lines + liability_lines + equity_lines,
            'use_hierarchy': False,
            # Meridian Standard: Balance verification
            'equation': equation,
            'balance_check': equation['difference'],
            'is_balanced': equation['is_balanced'],
            'liab_plus_equity': equation['liab_plus_equity'],
        }

    def _transform_tb_from_enhanced(self, data):
        """Transform Trial Balance data from enhanced wizard."""
        lines = []
        total_debit, total_credit = 0, 0
        for line in data.get('data', []):
            lines.append({
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'debit': line.get('ending_debit', 0),
                'credit': line.get('ending_credit', 0),
                'balance': line.get('ending_balance', 0),
            })
            total_debit += line.get('ending_debit', 0)
            total_credit += line.get('ending_credit', 0)
        totals = data.get('totals', {})
        return {
            'headers': ['Account', 'Debit', 'Credit', 'Balance'], 'lines': lines,
            'total_debit': totals.get('ending_debit', total_debit),
            'total_credit': totals.get('ending_credit', total_credit),
        }

    def _transform_cf_from_enhanced(self, data):
        """
        Transform Cash Flow data from enhanced wizard.

        MERIDIAN STANDARD: 3-Section Cash Flow Statement
        - Operating Activities (core business cash flows)
        - Investing Activities (asset purchases/sales)
        - Financing Activities (debt/equity transactions)
        """
        operating_lines = []
        investing_lines = []
        financing_lines = []
        all_lines = []

        sections = data.get('sections', {})

        # Process Operating section
        operating_data = sections.get('operating', {})
        for line in operating_data.get('lines', []):
            line_data = {
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'name': line.get('name', line.get('account_name', '')),
                'inflow': line.get('inflow', 0),
                'outflow': line.get('outflow', 0),
                'net': line.get('net', 0),
            }
            operating_lines.append(line_data)
            all_lines.append(line_data)

        # Process Investing section
        investing_data = sections.get('investing', {})
        for line in investing_data.get('lines', []):
            line_data = {
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'name': line.get('name', line.get('account_name', '')),
                'inflow': line.get('inflow', 0),
                'outflow': line.get('outflow', 0),
                'net': line.get('net', 0),
            }
            investing_lines.append(line_data)
            all_lines.append(line_data)

        # Process Financing section
        financing_data = sections.get('financing', {})
        for line in financing_data.get('lines', []):
            line_data = {
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'name': line.get('name', line.get('account_name', '')),
                'inflow': line.get('inflow', 0),
                'outflow': line.get('outflow', 0),
                'net': line.get('net', 0),
            }
            financing_lines.append(line_data)
            all_lines.append(line_data)

        # If no sections, fall back to flat lines
        if not all_lines:
            for section_data in sections.values() if isinstance(sections, dict) else []:
                for line in section_data.get('lines', []) if isinstance(section_data, dict) else []:
                    line_data = {
                        'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                        'name': line.get('name', line.get('account_name', '')),
                        'inflow': line.get('inflow', 0),
                        'outflow': line.get('outflow', 0),
                        'net': line.get('net', 0),
                    }
                    operating_lines.append(line_data)  # Default to operating
                    all_lines.append(line_data)

        summary = data.get('summary', {})
        operating_net = summary.get('total_operating', operating_data.get('total', 0))
        investing_net = summary.get('total_investing', investing_data.get('total', 0))
        financing_net = summary.get('total_financing', financing_data.get('total', 0))
        opening_cash = summary.get('opening_cash', 0)

        # Get Cash Flow summary using the helper
        cf_summary = self._get_cash_flow_summary(
            operating_net, investing_net, financing_net, opening_cash
        )

        return {
            'headers': ['Account', 'Inflow', 'Outflow', 'Net'],
            # Section-based lines (Meridian Standard)
            'operating_lines': operating_lines,
            'investing_lines': investing_lines,
            'financing_lines': financing_lines,
            # Section totals
            'operating_net': operating_net,
            'investing_net': investing_net,
            'financing_net': financing_net,
            # Overall totals
            'lines': all_lines,
            'total_inflow': summary.get('total_inflow', 0),
            'total_outflow': summary.get('total_outflow', 0),
            'net_cash_flow': cf_summary['raw']['net_change'],
            # Cash position
            'opening_cash': opening_cash,
            'closing_cash': cf_summary['raw']['closing_cash'],
            # Meridian Standard: Formatted summary
            'cf_summary': cf_summary,
        }

    def _transform_aged_from_enhanced(self, data):
        """Transform Aged data from enhanced wizard."""
        lines = []
        for line in data.get('data', []):
            lines.append({
                'partner': line.get('partner_name', ''),
                'debit': line.get('total', 0) if line.get('total', 0) > 0 else 0,
                'credit': abs(line.get('total', 0)) if line.get('total', 0) < 0 else 0,
                'balance': line.get('total', 0),
            })
        return {'headers': ['Partner', 'Debit', 'Credit', 'Balance'], 'lines': lines}

    def _transform_partner_from_enhanced(self, data):
        """Transform Partner Ledger/SoA data from enhanced wizard."""
        lines = []
        for partner_data in data.get('data', data.get('statements', [])):
            for line in partner_data.get('lines', []):
                lines.append({
                    'partner': partner_data.get('partner_name', ''), 'date': line.get('date', ''),
                    'move_name': line.get('move_name', ''), 'debit': line.get('debit', 0),
                    'credit': line.get('credit', 0), 'balance': line.get('balance', 0),
                })
        return {'headers': ['Partner', 'Date', 'Entry', 'Debit', 'Credit', 'Balance'], 'lines': lines}

    def _get_report_data(self, wizard):
        wizard.ensure_one()
        domain = wizard._get_domain()

        # Get base report data based on type
        if wizard.report_type == 'pl':
            report_data = self._process_pl_data(wizard, domain)
        elif wizard.report_type == 'bs':
            report_data = self._process_bs_data(wizard, domain)
        elif wizard.report_type == 'gl':
            report_data = self._process_gl_data(wizard, domain)
        elif wizard.report_type == 'aged':
            report_data = self._process_aged_data(wizard, domain)
        elif wizard.report_type == 'tb':
            report_data = self._process_tb_data(wizard, domain)
        elif wizard.report_type == 'cf':
            report_data = self._process_cf_data(wizard, domain)
        else:
            report_data = {}

        # Add company colors to all reports
        company = wizard.company_id if wizard.company_id else self.env.company
        report_data['colors'] = self._get_company_colors(company)
        report_data['currency_symbol'] = company.currency_id.symbol if company else ''

        return report_data

    def _process_gl_data(self, wizard, domain):
        lines_data = self.env['account.move.line'].search_read(
            domain,
            ['date', 'move_id', 'account_id', 'partner_id', 'name', 'debit', 'credit', 'balance'],
            order='date, account_id, move_id',
            limit=10000
        )
        lines = []
        account_totals = {}
        for line_dict in lines_data:
            account = self.env['account.account'].browse(
                line_dict['account_id'][0]
            ) if line_dict.get('account_id') else False
            account_code = account.code if account else ''
            account_name = account.name if account else ''
            account_key = f"{account_code} - {account_name}"
            if account_key not in account_totals:
                account_totals[account_key] = {'debit': 0.0, 'credit': 0.0, 'balance': 0.0}
            account_totals[account_key]['debit'] += line_dict['debit']
            account_totals[account_key]['credit'] += line_dict['credit']
            account_totals[account_key]['balance'] += line_dict['balance']
            lines.append({
                'date': line_dict['date'],
                'move_name': line_dict['move_id'][1] if line_dict.get('move_id') else '',
                'move_id': line_dict['move_id'][0] if line_dict.get('move_id') else False,
                'account': account_key,
                'account_id': account.id if account else False,
                'partner': line_dict['partner_id'][1] if line_dict.get('partner_id') else '',
                'label': line_dict['name'] or '',
                'debit': line_dict['debit'],
                'credit': line_dict['credit'],
                'balance': line_dict['balance'],
            })
        return {
            'title': 'General Ledger',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Date', 'Entry', 'Account', 'Partner', 'Label', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
            'account_totals': account_totals,
        }

    def _process_pl_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        income_lines = []
        expense_lines = []
        income_total = 0.0
        expense_total = 0.0
        cogs_total = 0.0
        for result in grouped_data:
            account = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            if not account:
                continue
            account_key = f"{account.code} - {account.name}"
            account_type = account.account_type
            if account_type in ['income', 'income_other']:
                amount = (credit_sum or 0.0) - (debit_sum or 0.0)
                income_total += amount
                income_lines.append({'account': account_key, 'account_id': account.id, 'amount': amount})
            elif account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
                amount = (debit_sum or 0.0) - (credit_sum or 0.0)
                expense_total += amount
                if account_type == 'expense_direct_cost':
                    cogs_total += amount
                expense_lines.append({'account': account_key, 'account_id': account.id, 'amount': amount})
        gross_profit = income_total - cogs_total
        net_profit = income_total - expense_total
        return {
            'title': 'Profit & Loss',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Amount'],
            'income_lines': income_lines,
            'expense_lines': expense_lines,
            'income_total': income_total,
            'expense_total': expense_total,
            'cogs_total': cogs_total,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'lines': income_lines + expense_lines,
        }

    def _process_bs_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        asset_lines, liability_lines, equity_lines = [], [], []
        asset_total, liability_total, equity_total = 0.0, 0.0, 0.0
        for result in grouped_data:
            account = result[0] if result else None
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not account:
                continue
            account_key = f"{account.code} - {account.name}"
            account_type = account.account_type
            balance = balance_sum or 0.0
            if account_type in ['asset_receivable', 'asset_cash', 'asset_current',
                               'asset_prepayments', 'asset_fixed', 'asset_non_current']:
                asset_total += balance
                asset_lines.append({'account': account_key, 'amount': balance})
            elif account_type in ['liability_payable', 'liability_current', 'liability_non_current']:
                liability_total += balance
                liability_lines.append({'account': account_key, 'amount': balance})
            elif account_type == 'equity':
                equity_total += balance
                equity_lines.append({'account': account_key, 'amount': balance})
        return {
            'title': 'Balance Sheet',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Amount'],
            'asset_lines': asset_lines,
            'liability_lines': liability_lines,
            'equity_lines': equity_lines,
            'asset_total': asset_total,
            'liability_total': liability_total,
            'equity_total': equity_total,
            'lines': asset_lines + liability_lines + equity_lines,
        }

    def _process_aged_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['partner_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        lines = []
        for result in grouped_data:
            partner = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not partner:
                continue
            lines.append({
                'partner': partner.name,
                'debit': debit_sum or 0.0,
                'credit': credit_sum or 0.0,
                'balance': balance_sum or 0.0,
            })
        return {
            'title': 'Aged Partner Report',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Partner', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
        }

    def _process_tb_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        lines = []
        total_debit = 0.0
        total_credit = 0.0
        for result in grouped_data:
            account = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not account:
                continue
            lines.append({
                'account': f"{account.code} - {account.name}",
                'debit': debit_sum or 0.0,
                'credit': credit_sum or 0.0,
                'balance': balance_sum or 0.0,
            })
            total_debit += debit_sum or 0.0
            total_credit += credit_sum or 0.0
        return {
            'title': 'Trial Balance',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
            'total_debit': total_debit,
            'total_credit': total_credit,
        }

    def _process_cf_data(self, wizard, domain):
        """
        Process Cash Flow data.

        MERIDIAN STANDARD: 3-Section Cash Flow Statement
        - Operating: Cash from core business (cash accounts)
        - Investing: Asset purchases/sales (fixed asset accounts)
        - Financing: Debt/equity transactions (liability/equity related)
        """
        MoveLine = self.env['account.move.line']

        # Operating Activities - Cash accounts
        cf_operating_domain = domain + [('account_id.account_type', '=', 'asset_cash')]
        operating_data = MoveLine._read_group(
            domain=cf_operating_domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )

        operating_lines = []
        operating_inflow = 0.0
        operating_outflow = 0.0

        for result in operating_data:
            account = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not account:
                continue
            operating_lines.append({
                'account': f"{account.code} - {account.name}",
                'name': account.name,
                'inflow': debit_sum or 0.0,
                'outflow': credit_sum or 0.0,
                'net': balance_sum or 0.0,
            })
            operating_inflow += debit_sum or 0.0
            operating_outflow += credit_sum or 0.0

        operating_net = operating_inflow - operating_outflow

        # For now, investing and financing are empty (requires more complex logic)
        # In a full implementation, these would query fixed asset and financing accounts
        investing_lines = []
        investing_net = 0.0

        financing_lines = []
        financing_net = 0.0

        # Calculate totals
        total_inflow = operating_inflow
        total_outflow = operating_outflow
        net_cash_flow = operating_net + investing_net + financing_net

        # All lines combined for backward compatibility
        all_lines = operating_lines + investing_lines + financing_lines

        return {
            'title': 'Cash Flow Statement',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Inflow', 'Outflow', 'Net'],
            # Section-based lines (Meridian Standard)
            'operating_lines': operating_lines,
            'investing_lines': investing_lines,
            'financing_lines': financing_lines,
            # Section totals
            'operating_net': operating_net,
            'investing_net': investing_net,
            'financing_net': financing_net,
            # Overall totals
            'lines': all_lines,
            'total_inflow': total_inflow,
            'total_outflow': total_outflow,
            'net_cash_flow': net_cash_flow,
            # Cash position (would need opening balance calculation in full implementation)
            'opening_cash': 0.0,
            'closing_cash': net_cash_flow,
        }


class OpsFinancialMinimalReportParser(models.AbstractModel):
    """
    Report parser for the MINIMAL Financial Reports template.

    This parser provides the `report_data` variable to the
    `ops_matrix_accounting.report_ops_financial_minimal` QWeb template.

    v19.0.1.0: Created to fix white page issue - template needs parser
    """
    _name = 'report.ops_matrix_accounting.report_ops_financial_minimal'
    _inherit = 'report.ops_matrix_accounting.report_ops_financial_document'
    _description = 'Financial Report (Minimal) Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Get report values for the Minimal Financial Report template.

        Delegates to the parent parser but ensures proper data structure
        for the minimal template which expects `report_data` with specific keys.
        """
        # Get base values from parent parser
        values = super()._get_report_values(docids, data)

        # Ensure the minimal template has what it needs
        report_data = values.get('report_data', {})

        # The minimal template expects these specific keys at root level
        if not report_data:
            # Try to generate from wizard if no data
            wizard = None
            if docids:
                wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
            if not wizard or not wizard.exists():
                active_id = self.env.context.get('active_id')
                if active_id:
                    wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(active_id)

            if wizard and wizard.exists():
                raw_data = wizard._get_report_data()
                report_data = self._transform_enhanced_data(wizard, raw_data)

        # Ensure all required keys exist for minimal template
        company = self.env.company
        if values.get('docs') and hasattr(values['docs'], 'company_id'):
            company = values['docs'].company_id or self.env.company

        # Add company colors if not present
        if 'colors' not in report_data:
            report_data['colors'] = self._get_company_colors(company)

        # Ensure date fields exist
        if 'date_from' not in report_data:
            report_data['date_from'] = ''
        if 'date_to' not in report_data:
            report_data['date_to'] = ''

        # Ensure company/title exist
        if 'company' not in report_data:
            report_data['company'] = company.name if company else ''
        if 'title' not in report_data:
            report_data['title'] = 'Financial Report'
        if 'currency_symbol' not in report_data:
            report_data['currency_symbol'] = company.currency_id.symbol if company else ''
        if 'target_move' not in report_data:
            report_data['target_move'] = 'Posted'

        values['report_data'] = report_data
        return values
