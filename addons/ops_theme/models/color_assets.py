# -*- coding: utf-8 -*-
"""
OPS Theme — Compile-Time Color Asset Management
=================================================
Manages SCSS color files through ir.asset (directive='replace') and
ir.attachment. Light-only — dark mode support removed.

When admin changes colors in Settings, this model:
1. Reads the current SCSS content (from attachment or filesystem)
2. Replaces $ops_color_* variable values via regex
3. Writes back to ir.attachment + creates ir.asset with directive='replace'
4. Clears Odoo's asset cache to force CSS recompilation
"""

import re
import base64
import logging

from odoo import models, api
from odoo.tools import misc
from odoo.addons.base.models.assetsbundle import EXTENSIONS

_logger = logging.getLogger(__name__)

# SCSS file and bundle (light only)
LIGHT_URL = '/ops_theme/static/src/scss/_colors_light.scss'
LIGHT_BUNDLE = 'web._assets_primary_variables'

# Color variable names (without the $ops_color_ prefix)
COLOR_FIELDS = [
    'brand',
    'primary',
    'success',
    'info',
    'warning',
    'danger',
    'bg',
    'surface',
    'text',
    'border',
]


class OPSColorAssets(models.AbstractModel):
    """Manage OPS theme SCSS color assets at compile time."""

    _name = 'ops_theme.color_assets'
    _description = 'OPS Color Assets Editor'

    # ----------------------------------------------------------
    # Private Helpers
    # ----------------------------------------------------------

    @api.model
    def _custom_url(self, url, bundle):
        """Generate custom URL for the replacement attachment."""
        return f'/_custom/{bundle}{url}'

    @api.model
    def _find_attachment(self, custom_url):
        """Find an existing custom attachment by URL."""
        return self.env['ir.attachment'].search([
            ('url', '=', custom_url)
        ], limit=1)

    @api.model
    def _find_asset(self, url):
        """Find an existing ir.asset record for a URL."""
        asset_url = url.lstrip('/')
        return self.env['ir.asset'].search([
            ('path', 'like', asset_url)
        ], limit=1)

    @api.model
    def _clear_compiled_bundles(self, bundle):
        """Delete compiled CSS/JS bundles to force recompilation."""
        bundle_patterns = [
            f'%{bundle}%',
        ]

        if bundle == 'web._assets_primary_variables':
            bundle_patterns.extend([
                '%web.assets_web%',
                '%web.assets_backend%',
            ])

        for pattern in bundle_patterns:
            compiled = self.env['ir.attachment'].search([
                ('name', 'like', pattern),
                '|',
                ('name', 'like', '%.min.css'),
                ('name', 'like', '%.min.js'),
            ])
            if compiled:
                count = len(compiled)
                compiled.unlink()
                _logger.info("OPS Theme: Deleted %d compiled bundles for pattern '%s'",
                           count, pattern)

    @api.model
    def _read_scss(self, url, bundle):
        """Read current SCSS content — from custom attachment or filesystem."""
        custom_url = self._custom_url(url, bundle)
        attachment = self._find_attachment(custom_url)
        if attachment:
            return base64.b64decode(attachment.datas).decode('utf-8')
        try:
            with misc.file_open(url.strip('/'), 'rb', filter_ext=EXTENSIONS) as f:
                return f.read().decode('utf-8')
        except FileNotFoundError:
            _logger.warning("OPS Theme: SCSS file not found: %s", url)
            return ''

    @api.model
    def _get_variable(self, content, var_name):
        """Extract a single $ops_color_{var_name} value from SCSS content."""
        match = re.search(
            rf'\$ops_color_{var_name}\s*:\s*(.*?)\s*;',
            content
        )
        return match.group(1).strip() if match else None

    @api.model
    def _replace_variables(self, content, variables):
        """Replace $ops_color_{name} values in SCSS content."""
        for var in variables:
            content = re.sub(
                rf'(\$ops_color_{var["name"]}\s*:\s*).*?(\s*;)',
                rf'\g<1>{var["value"]}\2',
                content
            )
        return content

    @api.model
    def _save_scss(self, url, bundle, content):
        """Save modified SCSS content via ir.attachment + ir.asset."""
        custom_url = self._custom_url(url, bundle)
        datas = base64.b64encode((content or '\n').encode('utf-8'))

        attachment = self._find_attachment(custom_url)
        if attachment:
            attachment.write({'datas': datas})
            _logger.info("OPS Theme: Updated color asset %s", custom_url)
        else:
            self.env['ir.attachment'].create({
                'name': url.split('/')[-1],
                'type': 'binary',
                'mimetype': 'text/scss',
                'datas': datas,
                'url': custom_url,
            })

            target_asset = self._find_asset(url)
            asset_values = {
                'path': custom_url,
                'target': url,
                'directive': 'replace',
            }
            if target_asset:
                asset_values['name'] = f'{target_asset.name} override'
                asset_values['bundle'] = target_asset.bundle
                asset_values['sequence'] = target_asset.sequence
            else:
                asset_values['name'] = f'{bundle}: replace {custom_url.split("/")[-1]}'
                asset_values['bundle'] = self.env['ir.asset']._get_related_bundle(
                    url, bundle
                )

            self.env['ir.asset'].create(asset_values)
            _logger.info("OPS Theme: Created color asset %s", custom_url)

        self._clear_compiled_bundles(bundle)
        self.env.registry.clear_cache('assets')

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def get_colors(self, url, bundle):
        """Read current $ops_color_* values from SCSS."""
        content = self._read_scss(url, bundle)
        return {
            name: self._get_variable(content, name)
            for name in COLOR_FIELDS
        }

    def set_colors(self, url, bundle, color_values):
        """Write $ops_color_* values to SCSS via ir.asset."""
        content = self._read_scss(url, bundle)
        variables = [
            {'name': name, 'value': value}
            for name, value in color_values.items()
            if value
        ]
        if variables:
            new_content = self._replace_variables(content, variables)
            self._save_scss(url, bundle, new_content)

    def reset_colors(self, url, bundle):
        """Remove custom override, reverting to the module's original SCSS."""
        custom_url = self._custom_url(url, bundle)
        self._find_attachment(custom_url).unlink()
        self.env['ir.asset'].search([
            ('path', '=', custom_url)
        ]).unlink()
        self._clear_compiled_bundles(bundle)
        self.env.registry.clear_cache('assets')
        _logger.info("OPS Theme: Reset color asset %s to defaults", url)

    # ----------------------------------------------------------
    # Convenience: Light only
    # ----------------------------------------------------------

    def get_light_colors(self):
        """Read light mode color values."""
        return self.get_colors(LIGHT_URL, LIGHT_BUNDLE)

    def set_light_colors(self, color_values):
        """Write light mode color values."""
        self.set_colors(LIGHT_URL, LIGHT_BUNDLE, color_values)

    def reset_all(self):
        """Reset light colors to module defaults."""
        self.reset_colors(LIGHT_URL, LIGHT_BUNDLE)
