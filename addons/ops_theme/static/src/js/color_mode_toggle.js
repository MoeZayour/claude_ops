/** @odoo-module **/
/**
 * OPS Theme - Color Mode Toggle
 * =============================
 * Handles light/dark mode switching with proper defaults.
 *
 * ARCHITECTURE:
 * - Default: LIGHT mode (professional ERP default)
 * - User preference stored in localStorage AND database
 * - Applies [data-color-mode="light|dark"] on <html> element
 * - CSS variables in _variables.scss respond to this attribute
 */

// =============================================================================
// EARLY INITIALIZATION (runs before DOM ready to prevent flash)
// =============================================================================

(function() {
    'use strict';

    // Get stored preference, default to 'light'
    const storedMode = localStorage.getItem('ops_color_mode');
    const effectiveMode = storedMode || 'light';

    // Apply immediately to prevent flash of wrong theme
    document.documentElement.setAttribute('data-color-mode', effectiveMode);

    // Also set class for any legacy CSS that uses .ops-dark-mode class
    if (effectiveMode === 'dark') {
        document.documentElement.classList.add('ops-dark-mode');
    } else {
        document.documentElement.classList.remove('ops-dark-mode');
    }
})();

// =============================================================================
// COLOR MODE API
// =============================================================================

/**
 * Set the color mode and persist preference.
 * @param {string} mode - 'light' or 'dark'
 */
window.setOpsColorMode = function(mode) {
    const validModes = ['light', 'dark'];
    if (!validModes.includes(mode)) {
        console.warn('OPS Theme: Invalid color mode:', mode);
        mode = 'light';
    }

    // Apply to DOM
    document.documentElement.setAttribute('data-color-mode', mode);

    // Toggle class for legacy support
    if (mode === 'dark') {
        document.documentElement.classList.add('ops-dark-mode');
    } else {
        document.documentElement.classList.remove('ops-dark-mode');
    }

    // Persist to localStorage
    localStorage.setItem('ops_color_mode', mode);

    // If Odoo session available, save to user preferences
    if (window.odoo && window.odoo.session_info && window.odoo.session_info.user_id) {
        // Fire and forget - don't block UI for this
        fetch('/web/dataset/call_kw/res.users/write', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: 'res.users',
                    method: 'write',
                    args: [[window.odoo.session_info.user_id], { ops_color_mode: mode }],
                    kwargs: {},
                },
                id: Math.floor(Math.random() * 1000000),
            }),
        }).catch(err => console.warn('OPS Theme: Could not save color mode preference:', err));
    }

    console.log('OPS Theme: Color mode set to', mode);
};

/**
 * Get current color mode.
 * @returns {string} 'light' or 'dark'
 */
window.getOpsColorMode = function() {
    return document.documentElement.getAttribute('data-color-mode') || 'light';
};

/**
 * Toggle between light and dark mode.
 */
window.toggleOpsColorMode = function() {
    const current = window.getOpsColorMode();
    window.setOpsColorMode(current === 'light' ? 'dark' : 'light');
};

// =============================================================================
// SYNC WITH SERVER ON PAGE LOAD
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // If Odoo session has color mode preference, use it
    if (window.odoo && window.odoo.session_info && window.odoo.session_info.color_mode) {
        const serverMode = window.odoo.session_info.color_mode;
        const localMode = localStorage.getItem('ops_color_mode');

        // Server preference takes precedence if different
        if (serverMode && serverMode !== localMode) {
            window.setOpsColorMode(serverMode);
        }
    }
});
