# -*- coding: utf-8 -*-
"""
OPS Framework - Report Helper Functions
========================================
Version: 1.0.0
Reference: OPS_REPORT_BRANDING_GUIDE_v1.0.0

Provides shared utility functions for all OPS corporate reports:
- Color scheme generation from company primary color
- Number formatting with thousands separators
- Percentage formatting
- Value classification (positive/negative/zero)
- Aging bucket classification
- Report context preparation
"""

from odoo import models, api
from datetime import datetime
import colorsys
import logging

_logger = logging.getLogger(__name__)


class OpsReportHelpers(models.AbstractModel):
    """Abstract model providing helper functions for OPS corporate reports"""

    _name = 'ops.report.helpers'
    _description = 'OPS Report Helper Functions'

    # =========================================================================
    # AMOUNT TO WORDS
    # =========================================================================

    @api.model
    def amount_to_words(self, amount, currency=None, lang='en'):
        """Convert numeric amount to words with currency.

        Args:
            amount: Numeric amount
            currency: res.currency record (optional)
            lang: 'en', 'ar', or 'both'

        Returns:
            dict with 'en' and/or 'ar' keys
        """
        result = {}
        currency_name = currency.name if currency else 'Units'

        currency_map = {
            'QAR': {'main': 'Qatari Riyal', 'main_plural': 'Qatari Riyals', 'sub': 'Dirham', 'sub_plural': 'Dirhams'},
            'AED': {'main': 'UAE Dirham', 'main_plural': 'UAE Dirhams', 'sub': 'Fil', 'sub_plural': 'Fils'},
            'SAR': {'main': 'Saudi Riyal', 'main_plural': 'Saudi Riyals', 'sub': 'Halala', 'sub_plural': 'Halalas'},
            'USD': {'main': 'US Dollar', 'main_plural': 'US Dollars', 'sub': 'Cent', 'sub_plural': 'Cents'},
            'EUR': {'main': 'Euro', 'main_plural': 'Euros', 'sub': 'Cent', 'sub_plural': 'Cents'},
            'GBP': {'main': 'Pound Sterling', 'main_plural': 'Pounds Sterling', 'sub': 'Penny', 'sub_plural': 'Pence'},
        }
        curr_info = currency_map.get(currency_name, {
            'main': currency_name, 'main_plural': currency_name,
            'sub': 'Cent', 'sub_plural': 'Cents',
        })

        ar_currency_map = {
            'QAR': {'main': 'ريال قطري', 'sub': 'درهم'},
            'AED': {'main': 'درهم إماراتي', 'sub': 'فلس'},
            'SAR': {'main': 'ريال سعودي', 'sub': 'هللة'},
            'USD': {'main': 'دولار أمريكي', 'sub': 'سنت'},
            'EUR': {'main': 'يورو', 'sub': 'سنت'},
        }

        main_amount = int(amount)
        decimal_amount = int(round((amount - main_amount) * 100))

        try:
            from num2words import num2words as n2w

            if lang in ('en', 'both'):
                main_words = n2w(main_amount, lang='en').title()
                main_unit = curr_info['main'] if main_amount == 1 else curr_info['main_plural']
                if decimal_amount > 0:
                    dec_words = n2w(decimal_amount, lang='en').title()
                    sub_unit = curr_info['sub'] if decimal_amount == 1 else curr_info['sub_plural']
                    result['en'] = f"{main_words} {main_unit} and {dec_words} {sub_unit}"
                else:
                    result['en'] = f"{main_words} {main_unit}"

            if lang in ('ar', 'both'):
                try:
                    main_words_ar = n2w(main_amount, lang='ar')
                    ar_curr = ar_currency_map.get(currency_name, {'main': currency_name, 'sub': ''})
                    if decimal_amount > 0:
                        dec_words_ar = n2w(decimal_amount, lang='ar')
                        result['ar'] = f"{main_words_ar} {ar_curr['main']} و{dec_words_ar} {ar_curr['sub']}"
                    else:
                        result['ar'] = f"{main_words_ar} {ar_curr['main']}"
                except Exception as e:
                    _logger.warning("Arabic num2words failed: %s", e)

        except ImportError:
            _logger.warning("num2words not installed, falling back to numeric display")
            result['en'] = f"{amount:,.2f} {currency_name}"
        except Exception as e:
            _logger.error("amount_to_words error: %s", e)
            result['en'] = f"{amount:,.2f}"

        return result

    # =========================================================================
    # COLOR SCHEME GENERATION
    # =========================================================================

    @api.model
    def get_primary_light(self, primary_hex):
        """
        Generate light background from primary color (15% opacity with white).

        Args:
            primary_hex (str): Hex color code (e.g., '#5B6BBB')

        Returns:
            str: Light version of the color as hex
        """
        if not primary_hex:
            primary_hex = '#5B6BBB'  # Default OPS primary

        hex_color = primary_hex.lstrip('#')

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            return '#E8EAF6'  # Default fallback

        # Mix with white at 15% opacity
        opacity = 0.15
        light_r = int(r * opacity + 255 * (1 - opacity))
        light_g = int(g * opacity + 255 * (1 - opacity))
        light_b = int(b * opacity + 255 * (1 - opacity))

        return '#{:02x}{:02x}{:02x}'.format(light_r, light_g, light_b)

    @api.model
    def get_primary_dark(self, primary_hex):
        """
        Generate darker shade of primary color (70% of original brightness).

        Args:
            primary_hex (str): Hex color code

        Returns:
            str: Darker version of the color as hex
        """
        if not primary_hex:
            primary_hex = '#5B6BBB'

        hex_color = primary_hex.lstrip('#')

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            return '#3D4A8A'  # Default fallback

        # Multiply by 70% for darker shade
        factor = 0.7
        dark_r = int(r * factor)
        dark_g = int(g * factor)
        dark_b = int(b * factor)

        return '#{:02x}{:02x}{:02x}'.format(dark_r, dark_g, dark_b)

    @api.model
    def get_color_scheme(self, company=None):
        """
        Get complete color scheme for a company based on primary color.

        Args:
            company (res.company): Company record (defaults to current company)

        Returns:
            dict: Color scheme with primary, light, and dark variants
        """
        if not company:
            company = self.env.company

        primary = company.primary_color or '#5B6BBB'

        return {
            'primary': primary,
            'primary_light': self.get_primary_light(primary),
            'primary_dark': self.get_primary_dark(primary),
            'navy': '#1e293b',
            'success': '#16a34a',
            'danger': '#dc2626',
            'warning': '#f59e0b',
            'text': '#1a1a1a',
            'text_muted': '#64748b',
            'zero': '#94a3b8',
        }

    # =========================================================================
    # NUMBER FORMATTING
    # =========================================================================

    @api.model
    def format_amount(self, value, currency=None, precision=2):
        """
        Format monetary amount with thousands separator.

        Args:
            value (float): Amount to format
            currency (res.currency): Currency (optional, for future use)
            precision (int): Decimal places (default 2)

        Returns:
            str: Formatted amount (e.g., "1,234.56")
        """
        if value is None:
            return '0.00'
        return '{:,.{prec}f}'.format(value, prec=precision)

    @api.model
    def format_amount_with_sign(self, value, currency=None, precision=2):
        """
        Format amount with explicit + sign for positive values.

        Args:
            value (float): Amount to format
            currency (res.currency): Currency (optional)
            precision (int): Decimal places

        Returns:
            str: Formatted amount with sign (e.g., "+1,234.56" or "-1,234.56")
        """
        if value is None:
            return '0.00'

        formatted = self.format_amount(abs(value), currency, precision)

        if value > 0:
            return '+' + formatted
        elif value < 0:
            return '-' + formatted
        return formatted

    @api.model
    def format_percentage(self, value, precision=1):
        """
        Format percentage value.

        Args:
            value (float): Percentage to format (e.g., 25.5 for 25.5%)
            precision (int): Decimal places

        Returns:
            str: Formatted percentage (e.g., "25.5%")
        """
        if value is None:
            return '0.0%'
        return '{:,.{prec}f}%'.format(value, prec=precision)

    # =========================================================================
    # VALUE CLASSIFICATION
    # =========================================================================

    @api.model
    def get_value_class(self, value, threshold=0.01):
        """
        Return CSS class for value coloring based on sign.

        Args:
            value (float): Value to classify
            threshold (float): Values within +/- threshold are considered zero

        Returns:
            str: CSS class name ('positive', 'negative', or 'zero')
        """
        if value is None or abs(value) < threshold:
            return 'zero'
        elif value > 0:
            return 'positive'
        else:
            return 'negative'

    @api.model
    def get_value_color(self, value, threshold=0.01):
        """
        Return color code for value based on sign.

        Args:
            value (float): Value to classify
            threshold (float): Zero threshold

        Returns:
            str: Hex color code
        """
        value_class = self.get_value_class(value, threshold)

        color_map = {
            'positive': '#16a34a',  # Green
            'negative': '#dc2626',  # Red
            'zero': '#94a3b8',      # Gray
        }

        return color_map.get(value_class, '#1a1a1a')

    # =========================================================================
    # AGING CLASSIFICATION
    # =========================================================================

    @api.model
    def get_aging_class(self, days):
        """
        Return CSS class for aging bucket coloring.

        Args:
            days (int): Number of days aged

        Returns:
            str: CSS class name for the aging bucket
        """
        if days <= 0:
            return 'ops-aging-current'
        elif days <= 30:
            return 'ops-aging-30'
        elif days <= 60:
            return 'ops-aging-60'
        elif days <= 90:
            return 'ops-aging-90'
        else:
            return 'ops-aging-over'

    @api.model
    def get_aging_color(self, days):
        """
        Return color code for aging bucket.

        Args:
            days (int): Number of days aged

        Returns:
            str: Hex color code
        """
        if days <= 0:
            return '#16a34a'  # Green - Current
        elif days <= 30:
            return '#1a1a1a'  # Black - 1-30
        elif days <= 60:
            return '#f59e0b'  # Orange - 31-60
        elif days <= 90:
            return '#ea580c'  # Dark Orange - 61-90
        else:
            return '#dc2626'  # Red - Over 90

    # =========================================================================
    # REPORT CONTEXT PREPARATION
    # =========================================================================

    @api.model
    def get_report_context(self, wizard, report_data):
        """
        Build standard context for all reports with company branding and helpers.

        Args:
            wizard: Wizard record that generated the report
            report_data (dict): Report-specific data

        Returns:
            dict: Complete context for QWeb template rendering
        """
        company = wizard.company_id if hasattr(wizard, 'company_id') else self.env.company
        user = self.env.user

        # Get color scheme
        colors = self.get_color_scheme(company)

        return {
            # Company info
            'company': company,
            'company_name': company.name,
            'currency_name': company.currency_id.name,
            'currency_symbol': company.currency_id.symbol,

            # Branding colors
            'primary_color': colors['primary'],
            'primary_light': colors['primary_light'],
            'primary_dark': colors['primary_dark'],
            'color_scheme': colors,

            # Helper functions (callable from QWeb)
            'get_primary_light': self.get_primary_light,
            'get_primary_dark': self.get_primary_dark,
            'get_color_scheme': self.get_color_scheme,
            'format_amount': self.format_amount,
            'format_amount_with_sign': self.format_amount_with_sign,
            'format_percentage': self.format_percentage,
            'get_value_class': self.get_value_class,
            'get_value_color': self.get_value_color,
            'get_aging_class': self.get_aging_class,
            'get_aging_color': self.get_aging_color,

            # Meta info
            'print_date': datetime.now().strftime('%b %d, %Y %H:%M'),
            'print_date_short': datetime.now().strftime('%Y-%m-%d'),
            'printed_by': user.name,
            'printed_by_email': user.email,

            # Report data (merged from wizard)
            **report_data
        }

    # =========================================================================
    # CONDITIONAL FORMATTING
    # =========================================================================

    @api.model
    def get_variance_class(self, value, favorable_is_positive=True):
        """
        Classify variance as favorable or unfavorable.

        Args:
            value (float): Variance amount
            favorable_is_positive (bool): True if positive variance is good

        Returns:
            str: 'favorable' or 'unfavorable'
        """
        if value is None or abs(value) < 0.01:
            return 'neutral'

        is_positive = value > 0

        if favorable_is_positive:
            return 'favorable' if is_positive else 'unfavorable'
        else:
            return 'unfavorable' if is_positive else 'favorable'

    @api.model
    def format_variance(self, value, favorable_is_positive=True):
        """
        Format variance with color coding and +/- indicators.

        Args:
            value (float): Variance amount
            favorable_is_positive (bool): Determines color coding

        Returns:
            dict: {
                'value': formatted string,
                'class': CSS class,
                'color': hex color
            }
        """
        if value is None or abs(value) < 0.01:
            return {
                'value': '-',
                'class': 'neutral',
                'color': '#94a3b8',
            }

        variance_class = self.get_variance_class(value, favorable_is_positive)

        return {
            'value': self.format_amount_with_sign(value),
            'class': variance_class,
            'color': '#16a34a' if variance_class == 'favorable' else '#dc2626',
        }

    # =========================================================================
    # MARGIN ANALYSIS
    # =========================================================================

    @api.model
    def classify_margin(self, margin_pct, thresholds=None):
        """
        Classify profit margin as excellent/good/poor.

        Args:
            margin_pct (float): Margin percentage (e.g., 25.0 for 25%)
            thresholds (dict): Custom thresholds {excellent: 20, good: 10}

        Returns:
            str: 'excellent', 'good', 'fair', or 'poor'
        """
        if thresholds is None:
            thresholds = {
                'excellent': 20.0,
                'good': 10.0,
                'fair': 5.0,
            }

        if margin_pct >= thresholds['excellent']:
            return 'excellent'
        elif margin_pct >= thresholds['good']:
            return 'good'
        elif margin_pct >= thresholds['fair']:
            return 'fair'
        else:
            return 'poor'

    @api.model
    def get_margin_color(self, margin_pct, thresholds=None):
        """
        Get color for margin display.

        Args:
            margin_pct (float): Margin percentage
            thresholds (dict): Custom thresholds

        Returns:
            str: Hex color code
        """
        classification = self.classify_margin(margin_pct, thresholds)

        color_map = {
            'excellent': '#16a34a',  # Green
            'good': '#16a34a',       # Green
            'fair': '#f59e0b',       # Orange
            'poor': '#dc2626',       # Red
        }

        return color_map.get(classification, '#1a1a1a')

    # =========================================================================
    # DATE FORMATTING
    # =========================================================================

    @api.model
    def format_date(self, date_obj, format_str='%b %d, %Y'):
        """
        Format date object to string.

        Args:
            date_obj: Date or datetime object
            format_str (str): strftime format string

        Returns:
            str: Formatted date string
        """
        if not date_obj:
            return ''

        if isinstance(date_obj, str):
            # Try to parse string to date
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return date_obj

        try:
            return date_obj.strftime(format_str)
        except (AttributeError, ValueError):
            return str(date_obj)

    # =========================================================================
    # BALANCE VERIFICATION
    # =========================================================================

    @api.model
    def verify_balance(self, total_debit, total_credit, threshold=0.01):
        """
        Verify if debits and credits balance.

        Args:
            total_debit (float): Total debit amount
            total_credit (float): Total credit amount
            threshold (float): Acceptable difference threshold

        Returns:
            dict: {
                'balanced': bool,
                'difference': float,
                'message': str
            }
        """
        difference = abs(total_debit - total_credit)
        balanced = difference <= threshold

        return {
            'balanced': balanced,
            'difference': difference,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'message': 'Balanced' if balanced else f'Unbalanced by {self.format_amount(difference)}',
        }

    # =========================================================================
    # ACCOUNT HIERARCHY INDENTATION
    # =========================================================================

    @api.model
    def get_indent_class(self, level):
        """
        Get CSS class for account hierarchy indentation.

        Args:
            level (int): Hierarchy level (0-4)

        Returns:
            str: CSS class name
        """
        level = max(0, min(4, level))  # Clamp between 0 and 4
        return f'ops-indent-{level}'

    @api.model
    def get_indent_pixels(self, level):
        """
        Get padding-left pixels for indentation.

        Args:
            level (int): Hierarchy level

        Returns:
            int: Padding in pixels
        """
        return level * 15  # 15px per level

    # =========================================================================
    # STATUS BADGE HELPERS
    # =========================================================================

    @api.model
    def get_pdc_status_class(self, status):
        """
        Get CSS class for PDC status badge.

        Args:
            status (str): PDC status (draft, deposited, cleared, bounced, etc.)

        Returns:
            str: CSS class name
        """
        status_map = {
            'draft': 'ops-status-badge--draft',
            'registered': 'ops-status-badge--draft',
            'deposited': 'ops-status-badge--deposited',
            'presented': 'ops-status-badge--presented',
            'cleared': 'ops-status-badge--cleared',
            'bounced': 'ops-status-badge--bounced',
            'issued': 'ops-status-badge--issued',
        }

        return status_map.get(status, 'ops-status-badge--draft')

    @api.model
    def get_asset_status_class(self, status):
        """
        Get CSS class for asset status.

        Args:
            status (str): Asset status (active, disposed, fully_depreciated)

        Returns:
            str: CSS class name
        """
        status_map = {
            'draft': 'ops-asset-status--draft',
            'open': 'ops-asset-status--active',
            'close': 'ops-asset-status--disposed',
            'disposed': 'ops-asset-status--disposed',
        }

        return status_map.get(status, 'ops-asset-status--active')
