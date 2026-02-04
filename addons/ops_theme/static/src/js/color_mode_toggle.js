/** @odoo-module **/
/**
 * OPS Theme - Color Mode Toggle (FIXED v7.4.0)
 * ==============================================
 * Handles light/dark mode switching with proper persistence.
 *
 * PRIORITY ORDER (FIXED):
 * 1. HTML attribute (set by server via template from user.ops_color_mode)
 * 2. localStorage (for client-side persistence)
 * 3. Default: 'light'
 *
 * BUG FIX: Previously localStorage was checked before HTML attribute,
 * causing server preference to be ignored on page load.
 */

// =============================================================================
// EARLY INITIALIZATION (before DOM ready to prevent flash)
// =============================================================================

(function() {
    'use strict';

    // PRIORITY 1: Check if server set the attribute via template
    // This is the authoritative source - the user's saved preference
    let serverMode = document.documentElement.getAttribute('data-color-mode');

    // PRIORITY 2: If no server attribute yet (template not fully rendered),
    // check localStorage as fallback
    if (!serverMode || (serverMode !== 'light' && serverMode !== 'dark')) {
        serverMode = localStorage.getItem('ops_color_mode');
    }

    // PRIORITY 3: Default to light if nothing is set
    let effectiveMode = serverMode;
    if (!effectiveMode || (effectiveMode !== 'light' && effectiveMode !== 'dark')) {
        effectiveMode = 'light';
    }

    // Apply immediately to prevent flash
    applyColorMode(effectiveMode);
    
    // Sync localStorage with the applied mode
    localStorage.setItem('ops_color_mode', effectiveMode);
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
    // Wait for Odoo session to be available
    setTimeout(() => {
        if (window.odoo && window.odoo.session_info) {
            const serverMode = window.odoo.session_info.ops_color_mode;
            
            // If server has a preference and it differs from current, apply it
            if (serverMode && (serverMode === 'light' || serverMode === 'dark')) {
                const currentMode = document.documentElement.getAttribute('data-color-mode');
                
                if (currentMode !== serverMode) {
                    // Server preference is authoritative
                    localStorage.setItem('ops_color_mode', serverMode);
                    applyColorMode(serverMode);
                    console.log('[OPS Theme] Synced color mode from server:', serverMode);
                }
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
 * @returns {Promise<boolean>} Success status
 */
window.setOpsColorMode = async function(mode) {
    if (mode !== 'light' && mode !== 'dark') {
        console.warn('[OPS Theme] Invalid color mode:', mode, '- using light');
        mode = 'light';
    }

    // Apply to DOM immediately
    applyColorMode(mode);

    // Persist to localStorage
    localStorage.setItem('ops_color_mode', mode);

    // Save to server if session available
    if (window.odoo && window.odoo.session_info && window.odoo.session_info.uid) {
        try {
            const response = await fetch('/web/dataset/call_kw/res.users/write', {
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
            });

            const result = await response.json();
            
            if (result.error) {
                console.error('[OPS Theme] Failed to save color mode:', result.error);
                return false;
            }
            
            console.log('[OPS Theme] Color mode saved to server:', mode);
            return true;
        } catch (err) {
            console.error('[OPS Theme] Error saving color mode:', err);
            return false;
        }
    }

    console.log('[OPS Theme] Color mode set to', mode);
    return true;
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
window.toggleOpsColorMode = async function() {
    const current = window.getOpsColorMode();
    const newMode = current === 'light' ? 'dark' : 'light';
    await window.setOpsColorMode(newMode);
};

// Export for module usage
export { applyColorMode };

console.log('[OPS Theme] Color mode toggle loaded (v7.4.0 - fixed persistence)');
