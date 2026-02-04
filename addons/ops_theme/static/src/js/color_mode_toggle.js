/** @odoo-module **/
/**
 * OPS Theme - Color Mode Toggle (v7.5.0 - ALIGNED WITH ODOO 19)
 * ==============================================================
 * Integrates WITH Odoo 19's native color scheme system (cookie-based).
 * 
 * Odoo 19 Architecture:
 * - Uses a COOKIE named "color_scheme" (values: "light" or "dark")
 * - All Odoo JS reads: cookie.get("color_scheme")
 * - Backend provides default via ir_http.color_scheme()
 * 
 * OPS Integration:
 * - Adds user menu toggle (Odoo 19 doesn't provide one)
 * - Stores preference in res.users.ops_color_mode
 * - Sets the color_scheme COOKIE (Odoo reads this)
 * - Override ir_http.color_scheme() to read from user field
 */

import { cookie } from "@web/core/browser/cookie";

/**
 * Get current color scheme from Odoo's cookie
 * @returns {string} 'light' or 'dark'
 */
function getColorScheme() {
    return cookie.get("color_scheme") || "light";
}

/**
 * Set color scheme via Odoo's cookie system
 * @param {string} scheme - 'light' or 'dark'
 */
function setColorScheme(scheme) {
    if (scheme !== 'light' && scheme !== 'dark') {
        console.warn('[OPS Theme] Invalid color scheme:', scheme, '- using light');
        scheme = 'light';
    }
    
    // Set Odoo's cookie (this is what Odoo reads)
    cookie.set("color_scheme", scheme);
    
    console.log('[OPS Theme] Color scheme set to:', scheme);
}

/**
 * Save color scheme preference to database
 * @param {string} scheme - 'light' or 'dark'
 * @returns {Promise<boolean>} Success status
 */
async function saveColorSchemeToDatabase(scheme) {
    if (!window.odoo?.session_info?.uid) {
        return false;
    }

    try {
        const response = await fetch('/web/dataset/call_kw/res.users/write', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: 'res.users',
                    method: 'write',
                    args: [[window.odoo.session_info.uid], { ops_color_mode: scheme }],
                    kwargs: {},
                },
                id: Math.floor(Math.random() * 1000000),
            }),
        });

        const result = await response.json();
        
        if (result.error) {
            console.error('[OPS Theme] Failed to save color scheme:', result.error);
            return false;
        }
        
        console.log('[OPS Theme] Color scheme saved to database:', scheme);
        return true;
    } catch (err) {
        console.error('[OPS Theme] Error saving color scheme:', err);
        return false;
    }
}

// =============================================================================
// PUBLIC API
// =============================================================================

/**
 * Set the color scheme and persist preference.
 * @param {string} scheme - 'light' or 'dark'
 * @returns {Promise<boolean>} Success status
 */
window.setOpsColorMode = async function(scheme) {
    // Set the cookie (Odoo's system)
    setColorScheme(scheme);
    
    // Save to database for persistence
    await saveColorSchemeToDatabase(scheme);
    
    // Reload page to apply theme changes
    // (Odoo's SCSS variables are compiled server-side based on color_scheme)
    setTimeout(() => {
        window.location.reload();
    }, 200);
    
    return true;
};

/**
 * Get current color scheme.
 * @returns {string} 'light' or 'dark'
 */
window.getOpsColorMode = function() {
    return getColorScheme();
};

/**
 * Toggle between light and dark mode.
 */
window.toggleOpsColorMode = async function() {
    const current = getColorScheme();
    const newScheme = current === 'light' ? 'dark' : 'light';
    await window.setOpsColorMode(newScheme);
};

// =============================================================================
// INITIALIZATION
// =============================================================================

// On page load, sync cookie with user's saved preference
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (window.odoo?.session_info) {
            const userPreference = window.odoo.session_info.ops_color_mode;
            const currentCookie = getColorScheme();
            
            // If user has a preference and it differs from cookie, apply it
            if (userPreference && userPreference !== currentCookie) {
                console.log('[OPS Theme] Syncing color scheme from user preference:', userPreference);
                setColorScheme(userPreference);
                // No reload needed - just set the cookie for consistency
            }
        }
    }, 100);
});

console.log('[OPS Theme] Color mode toggle loaded (v7.5.0 - Odoo 19 compatible)');
