/** @odoo-module **/
/**
 * OPS Theme - Live Preview for Settings Page
 * =============================================
 * Reads unsaved color values from the settings form and applies them
 * as CSS custom properties on :root for instant visual feedback.
 *
 * Preview is temporary — only CSS variables are overridden.
 * Saving the form persists to the database; refreshing restores originals.
 */

const OPS_COLOR_FIELDS = [
    { field: 'ops_primary_color',   varName: '--ops-primary' },
    { field: 'ops_secondary_color', varName: '--ops-secondary' },
    { field: 'ops_success_color',   varName: '--ops-success' },
    { field: 'ops_warning_color',   varName: '--ops-warning' },
    { field: 'ops_danger_color',    varName: '--ops-danger' },
];

/**
 * Read a color field value from the settings form DOM.
 * Odoo 19 color widget stores the value in a hidden input.
 */
function readColorField(fieldName) {
    // Try the color widget's actual input
    const wrapper = document.querySelector(`[name="${fieldName}"]`);
    if (!wrapper) return null;

    // Look for the color input inside the widget
    const colorInput = wrapper.querySelector('input[type="color"]');
    if (colorInput && colorInput.value) return colorInput.value;

    // Fallback: text input
    const textInput = wrapper.querySelector('input[type="text"]');
    if (textInput && textInput.value) return textInput.value;

    // Fallback: any input
    const anyInput = wrapper.querySelector('input');
    if (anyInput && anyInput.value && anyInput.value.startsWith('#')) return anyInput.value;

    return null;
}

/**
 * Convert hex color to RGB string for CSS rgba() usage.
 */
function hexToRgb(hex) {
    hex = hex.replace('#', '');
    if (hex.length !== 6) return '0, 0, 0';
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    return `${r}, ${g}, ${b}`;
}

/**
 * Darken a hex color by a factor.
 */
function darkenColor(hex, factor = 0.85) {
    hex = hex.replace('#', '');
    if (hex.length !== 6) return '#000000';
    const r = Math.round(parseInt(hex.substring(0, 2), 16) * factor);
    const g = Math.round(parseInt(hex.substring(2, 4), 16) * factor);
    const b = Math.round(parseInt(hex.substring(4, 6), 16) * factor);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/**
 * Apply preview: read form values, set CSS variables.
 */
window.opsPreviewTheme = function () {
    const root = document.documentElement;
    let applied = 0;

    for (const { field, varName } of OPS_COLOR_FIELDS) {
        const value = readColorField(field);
        if (value) {
            root.style.setProperty(varName, value);
            root.style.setProperty(`${varName}-rgb`, hexToRgb(value));
            if (varName === '--ops-secondary' || varName === '--ops-primary') {
                root.style.setProperty(`${varName}-hover`, darkenColor(value));
            }
            applied++;
        }
    }

    // Apply primary as navbar bg if dark/primary style
    const primary = readColorField('ops_primary_color');
    if (primary) {
        root.style.setProperty('--ops-navbar-bg', primary);
        root.style.setProperty('--ops-bg-navbar', primary);
        root.style.setProperty('--ops-report-header-bg', primary);
    }

    // Visual feedback
    if (applied > 0) {
        // Add a subtle indicator bar
        let indicator = document.getElementById('ops-preview-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'ops-preview-indicator';
            indicator.style.cssText = `
                position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
                background: linear-gradient(90deg, var(--ops-primary, #1e293b), var(--ops-secondary, #3b82f6));
                color: #fff; text-align: center; padding: 6px 16px;
                font-size: 13px; font-weight: 500;
                box-shadow: 0 -2px 8px rgba(0,0,0,0.15);
                transition: opacity 0.3s ease;
            `;
            indicator.textContent = 'Previewing theme changes \u2014 Save to make permanent';
            document.body.appendChild(indicator);
        }
    }
};

/**
 * Reset preview: remove all inline CSS variable overrides.
 */
window.opsResetPreview = function () {
    const root = document.documentElement;

    for (const { varName } of OPS_COLOR_FIELDS) {
        root.style.removeProperty(varName);
        root.style.removeProperty(`${varName}-rgb`);
        root.style.removeProperty(`${varName}-hover`);
    }
    root.style.removeProperty('--ops-navbar-bg');
    root.style.removeProperty('--ops-bg-navbar');
    root.style.removeProperty('--ops-report-header-bg');

    // Remove indicator
    const indicator = document.getElementById('ops-preview-indicator');
    if (indicator) {
        indicator.style.opacity = '0';
        setTimeout(() => indicator.remove(), 300);
    }
};
