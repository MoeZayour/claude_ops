# -*- coding: utf-8 -*-
"""
OPS Theme - Report Helpers
===========================
Shared helper methods for OPS external document templates.
Provides amount-to-words conversion with currency support (EN + AR).
"""

from odoo import models

# ===========================================================================
# Number-to-Words Data
# ===========================================================================
ONES_EN = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
    'Seventeen', 'Eighteen', 'Nineteen',
]
TENS_EN = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
SCALES_EN = ['', 'Thousand', 'Million', 'Billion', 'Trillion']

ONES_AR = [
    '', '\u0648\u0627\u062d\u062f', '\u0627\u062b\u0646\u0627\u0646',
    '\u062b\u0644\u0627\u062b\u0629', '\u0623\u0631\u0628\u0639\u0629',
    '\u062e\u0645\u0633\u0629', '\u0633\u062a\u0629', '\u0633\u0628\u0639\u0629',
    '\u062b\u0645\u0627\u0646\u064a\u0629', '\u062a\u0633\u0639\u0629',
    '\u0639\u0634\u0631\u0629',
    '\u0623\u062d\u062f \u0639\u0634\u0631', '\u0627\u062b\u0646\u0627 \u0639\u0634\u0631',
    '\u062b\u0644\u0627\u062b\u0629 \u0639\u0634\u0631', '\u0623\u0631\u0628\u0639\u0629 \u0639\u0634\u0631',
    '\u062e\u0645\u0633\u0629 \u0639\u0634\u0631', '\u0633\u062a\u0629 \u0639\u0634\u0631',
    '\u0633\u0628\u0639\u0629 \u0639\u0634\u0631', '\u062b\u0645\u0627\u0646\u064a\u0629 \u0639\u0634\u0631',
    '\u062a\u0633\u0639\u0629 \u0639\u0634\u0631',
]
TENS_AR = [
    '', '', '\u0639\u0634\u0631\u0648\u0646', '\u062b\u0644\u0627\u062b\u0648\u0646',
    '\u0623\u0631\u0628\u0639\u0648\u0646', '\u062e\u0645\u0633\u0648\u0646',
    '\u0633\u062a\u0648\u0646', '\u0633\u0628\u0639\u0648\u0646',
    '\u062b\u0645\u0627\u0646\u0648\u0646', '\u062a\u0633\u0639\u0648\u0646',
]
SCALES_AR = ['', '\u0623\u0644\u0641', '\u0645\u0644\u064a\u0648\u0646', '\u0645\u0644\u064a\u0627\u0631']

# Currency name mappings
CURRENCY_NAMES = {
    'QAR': {'en': ('Qatari Riyals', 'Dirhams'), 'ar': ('\u0631\u064a\u0627\u0644 \u0642\u0637\u0631\u064a', '\u062f\u0631\u0647\u0645\u0627\u064b')},
    'SAR': {'en': ('Saudi Riyals', 'Halalas'), 'ar': ('\u0631\u064a\u0627\u0644 \u0633\u0639\u0648\u062f\u064a', '\u0647\u0644\u0644\u0629')},
    'AED': {'en': ('UAE Dirhams', 'Fils'), 'ar': ('\u062f\u0631\u0647\u0645 \u0625\u0645\u0627\u0631\u0627\u062a\u064a', '\u0641\u0644\u0633')},
    'USD': {'en': ('US Dollars', 'Cents'), 'ar': ('\u062f\u0648\u0644\u0627\u0631 \u0623\u0645\u0631\u064a\u0643\u064a', '\u0633\u0646\u062a')},
    'EUR': {'en': ('Euros', 'Cents'), 'ar': ('\u064a\u0648\u0631\u0648', '\u0633\u0646\u062a')},
    'GBP': {'en': ('British Pounds', 'Pence'), 'ar': ('\u062c\u0646\u064a\u0647 \u0625\u0633\u062a\u0631\u0644\u064a\u0646\u064a', '\u0628\u0646\u0633')},
    'KWD': {'en': ('Kuwaiti Dinars', 'Fils'), 'ar': ('\u062f\u064a\u0646\u0627\u0631 \u0643\u0648\u064a\u062a\u064a', '\u0641\u0644\u0633')},
    'BHD': {'en': ('Bahraini Dinars', 'Fils'), 'ar': ('\u062f\u064a\u0646\u0627\u0631 \u0628\u062d\u0631\u064a\u0646\u064a', '\u0641\u0644\u0633')},
    'OMR': {'en': ('Omani Rials', 'Baisa'), 'ar': ('\u0631\u064a\u0627\u0644 \u0639\u0645\u0627\u0646\u064a', '\u0628\u064a\u0633\u0629')},
    'JOD': {'en': ('Jordanian Dinars', 'Fils'), 'ar': ('\u062f\u064a\u0646\u0627\u0631 \u0623\u0631\u062f\u0646\u064a', '\u0641\u0644\u0633')},
    'EGP': {'en': ('Egyptian Pounds', 'Piasters'), 'ar': ('\u062c\u0646\u064a\u0647 \u0645\u0635\u0631\u064a', '\u0642\u0631\u0634')},
}


def _chunk_to_words_en(n):
    """Convert number 0-999 to English words."""
    if n == 0:
        return ''
    parts = []
    if n >= 100:
        parts.append(ONES_EN[n // 100] + ' Hundred')
        n %= 100
    if n >= 20:
        word = TENS_EN[n // 10]
        if n % 10:
            word += '-' + ONES_EN[n % 10]
        parts.append(word)
    elif n > 0:
        parts.append(ONES_EN[n])
    return ' '.join(parts)


def _chunk_to_words_ar(n):
    """Convert number 0-999 to Arabic words."""
    if n == 0:
        return ''
    parts = []
    if n >= 100:
        h = n // 100
        if h == 1:
            parts.append('\u0645\u0627\u0626\u0629')
        elif h == 2:
            parts.append('\u0645\u0627\u0626\u062a\u0627\u0646')
        else:
            parts.append(ONES_AR[h] + ' \u0645\u0627\u0626\u0629')
        n %= 100
    if n >= 20:
        r = n % 10
        if r:
            parts.append(ONES_AR[r] + ' \u0648' + TENS_AR[n // 10])
        else:
            parts.append(TENS_AR[n // 10])
    elif n > 0:
        parts.append(ONES_AR[n])
    return ' \u0648'.join(parts) if len(parts) > 1 else (parts[0] if parts else '')


def _number_to_words_en(n):
    """Convert integer to English words."""
    if n == 0:
        return 'Zero'
    chunks = []
    temp = n
    while temp > 0:
        chunks.append(temp % 1000)
        temp //= 1000
    parts = []
    for i, chunk in enumerate(chunks):
        if chunk == 0:
            continue
        w = _chunk_to_words_en(chunk)
        if i < len(SCALES_EN) and SCALES_EN[i]:
            w += ' ' + SCALES_EN[i]
        parts.append(w)
    return ' '.join(reversed(parts))


def _number_to_words_ar(n):
    """Convert integer to Arabic words."""
    if n == 0:
        return '\u0635\u0641\u0631'
    chunks = []
    temp = n
    while temp > 0:
        chunks.append(temp % 1000)
        temp //= 1000
    parts = []
    for i, chunk in enumerate(chunks):
        if chunk == 0:
            continue
        w = _chunk_to_words_ar(chunk)
        if i > 0 and i < len(SCALES_AR):
            if chunk == 1:
                w = SCALES_AR[i]
            else:
                w += ' ' + SCALES_AR[i]
        parts.append(w)
    return ' \u0648'.join(reversed(parts))


def _amount_in_lang(amount, currency_code, lang):
    """Convert amount to words in a specific language.

    Returns string like "One Hundred Forty-Six Thousand Five Hundred Two Qatari Riyals and Eighty-Three Dirhams"
    """
    whole = int(amount)
    # Round to 2 decimal places to avoid float precision issues
    fraction = round((amount - whole) * 100)
    if fraction >= 100:
        whole += 1
        fraction = 0

    cur_info = CURRENCY_NAMES.get(currency_code, {}).get(lang)
    cur_name = cur_info[0] if cur_info else (currency_code or '')
    sub_name = cur_info[1] if cur_info else ''

    if lang == 'ar':
        main = _number_to_words_ar(whole) if whole else '\u0635\u0641\u0631'
        result = main
        if cur_name:
            result += ' ' + cur_name
        if fraction > 0:
            frac_words = _number_to_words_ar(fraction)
            result += ' \u0648' + frac_words
            if sub_name:
                result += ' ' + sub_name
        return result
    else:
        main = _number_to_words_en(whole) if whole else 'Zero'
        result = main
        if cur_name:
            result += ' ' + cur_name
        if fraction > 0:
            frac_words = _number_to_words_en(fraction)
            result += ' and ' + frac_words
            if sub_name:
                result += ' ' + sub_name
        return result


class OpsReportHelpers(models.AbstractModel):
    """Shared helper methods accessible from QWeb report templates.

    Usage in templates:
        env['ops.report.helpers'].amount_to_words(doc.amount_total, doc.currency_id, 'en')
    """

    _name = 'ops.report.helpers'
    _description = 'OPS Report Helper Methods'

    def amount_to_words(self, amount, currency=None, lang='en'):
        """Convert monetary amount to words.

        Args:
            amount: float amount (e.g., 146502.83)
            currency: res.currency record (optional)
            lang: 'en', 'ar', or 'both'

        Returns:
            dict: {'en': '...', 'ar': '...'} depending on lang
        """
        if not amount and amount != 0:
            return {}

        currency_code = currency.name if currency else ''
        result = {}

        if lang in ('en', 'both'):
            result['en'] = _amount_in_lang(abs(amount), currency_code, 'en')
        if lang in ('ar', 'both'):
            result['ar'] = _amount_in_lang(abs(amount), currency_code, 'ar')

        return result
