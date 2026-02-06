# -*- coding: utf-8 -*-
"""
OPS Theme - Amount to Words
============================
Convert monetary amounts to words in multiple languages.
"""

from odoo import models

ONES = {
    'en': ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
           'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
           'seventeen', 'eighteen', 'nineteen'],
    'ar': ['', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة',
           'عشرة', 'أحد عشر', 'اثنا عشر', 'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر', 'ستة عشر',
           'سبعة عشر', 'ثمانية عشر', 'تسعة عشر'],
}

TENS = {
    'en': ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'],
    'ar': ['', '', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون'],
}

SCALES = {
    'en': ['', 'thousand', 'million', 'billion'],
    'ar': ['', 'ألف', 'مليون', 'مليار'],
}


class ResCompanyAmountWords(models.Model):
    """Add amount_to_words method to res.company."""

    _inherit = 'res.company'

    def amount_to_words(self, amount, currency=None):
        """Convert amount to words using company's language setting."""
        self.ensure_one()
        lang = self.ops_amount_words_lang or 'en'

        if lang not in ONES:
            lang = 'en'

        if amount == 0:
            return 'zero' if lang == 'en' else 'صفر'

        try:
            return self._convert_number(int(amount), lang)
        except Exception:
            return str(amount)

    def _convert_number(self, n, lang):
        """Convert integer to words."""
        if n < 20:
            return ONES[lang][n]
        elif n < 100:
            tens, ones = divmod(n, 10)
            if ones:
                if lang == 'en':
                    return f"{TENS[lang][tens]}-{ONES[lang][ones]}"
                else:
                    return f"{ONES[lang][ones]} و{TENS[lang][tens]}"
            return TENS[lang][tens]
        elif n < 1000:
            hundreds, remainder = divmod(n, 100)
            if lang == 'en':
                result = f"{ONES[lang][hundreds]} hundred"
            else:
                result = f"{ONES[lang][hundreds]} مائة"
            if remainder:
                if lang == 'en':
                    result += f" and {self._convert_number(remainder, lang)}"
                else:
                    result += f" و{self._convert_number(remainder, lang)}"
            return result
        else:
            for i, scale in enumerate(SCALES[lang]):
                if n < 1000 ** (i + 1):
                    break

            divisor = 1000 ** i
            quotient, remainder = divmod(n, divisor)

            result = f"{self._convert_number(quotient, lang)} {SCALES[lang][i]}"
            if remainder:
                if lang == 'en':
                    result += f" {self._convert_number(remainder, lang)}"
                else:
                    result += f" و{self._convert_number(remainder, lang)}"
            return result
