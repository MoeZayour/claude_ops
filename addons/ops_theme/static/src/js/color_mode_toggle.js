/** @odoo-module **/
/**
 * OPS Theme - Color Mode Toggle
 * =============================
 * Handles light/dark mode switching with server-side preference sync.
 *
 * Priority:
 * 1. HTML attribute (set by server via template)
 * 2. localStorage (for persistence)
 * 3. Default: 'light'
 */

// =============================================================================
// EARLY INITIALIZATION (before DOM ready to prevent flash)
// =============================================================================

(function() {
    'use strict';

    // First, check if server already set the attribute via template
    let serverMode = document.documentElement.getAttribute('data-color-mode');

    // If server set a valid mode, use it
    if (serverMode === 'light' || serverMode === 'dark') {
        localStorage.setItem('ops_color_mode', serverMode);
        applyColorMode(serverMode);
        return;
    }

    // Otherwise, try localStorage
    let effectiveMode = localStorage.getItem('ops_color_mode');

    // Default to light if nothing stored
    if (!effectiveMode || (effectiveMode !== 'light' && effectiveMode !== 'dark')) {
        effectiveMode = 'light';
    }

    // Apply immediately to prevent flash
    applyColorMode(effectiveMode);
})();

/**
 * Apply color mode to DOM
 */
function applyColorMode(mode) {
    if (mode !== 'light' && mode !== 'dark') {
        mode = 'light';
    }

    document.documentElement.setAttribute('data-color-mode', mode);

    // Legacy class support
    if (mode === 'dark') {
        document.documentElement.classList.add('ops-dark-mode');
        document.body?.classList.add('ops-dark-mode');
    } else {
        document.documentElement.classList.remove('ops-dark-mode');
        document.body?.classList.remove('ops-dark-mode');
    }
}

// =============================================================================
// SYNC WITH SERVER ON DOM READY
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Wait a tick for Odoo session to be available
    setTimeout(() => {
        if (window.odoo && window.odoo.session_info) {
            const serverMode = window.odoo.session_info.ops_color_mode;
            if (serverMode && (serverMode === 'light' || serverMode === 'dark')) {
                // Server preference takes precedence
                localStorage.setItem('ops_color_mode', serverMode);
                applyColorMode(serverMode);
                console.log('OPS Theme: Applied server color mode:', serverMode);
            }
        }
    }, 100);
});

// =============================================================================
// PUBLIC API
// =============================================================================

/**
 * Set the color mode and persist preference.
 * @param {string} mode - 'light' or 'dark'
 */
window.setOpsColorMode = function(mode) {
    if (mode !== 'light' && mode !== 'dark') {
        console.warn('OPS Theme: Invalid color mode:', mode, '- using light');
        mode = 'light';
    }

    // Apply to DOM
    applyColorMode(mode);

    // Persist to localStorage
    localStorage.setItem('ops_color_mode', mode);

    // Save to server if session available
    if (window.odoo && window.odoo.session_info && window.odoo.session_info.uid) {
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
                    args: [[window.odoo.session_info.uid], { ops_color_mode: mode }],
                    kwargs: {},
                },
                id: Math.floor(Math.random() * 1000000),
            }),
        }).catch(err => console.warn('OPS Theme: Could not save preference:', err));
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

// Export for module usage
export { applyColorMode };
