/** @odoo-module **/
/**
 * OPS Theme - User Menu Items (v7.5.1 - FIXED)
 * ===============================================
 * Adds color mode toggle to the user menu dropdown.
 * Uses Odoo 19's cookie-based system.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";

function getCurrentColorMode() {
    // Read from Odoo's cookie (this is what Odoo uses)
    return cookie.get("color_scheme") || "light";
}

async function toggleColorMode() {
    const current = getCurrentColorMode();
    const newMode = current === 'light' ? 'dark' : 'light';
    
    console.log('[OPS Theme] Toggling color mode from', current, 'to', newMode);
    
    // 1. Set Odoo's cookie
    cookie.set("color_scheme", newMode);
    
    // 2. Save to database for persistence
    if (window.odoo?.session_info?.uid) {
        try {
            await fetch('/web/dataset/call_kw/res.users/write', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        model: 'res.users',
                        method: 'write',
                        args: [[window.odoo.session_info.uid], { ops_color_mode: newMode }],
                        kwargs: {},
                    },
                    id: Math.floor(Math.random() * 1000000),
                }),
            });
            console.log('[OPS Theme] Color mode saved to database');
        } catch (err) {
            console.error('[OPS Theme] Error saving color mode:', err);
        }
    }
    
    // 3. Reload page to apply new CSS
    // (Odoo loads different CSS files based on color_scheme)
    setTimeout(() => {
        window.location.reload();
    }, 200);
}

function colorModeToggleItem(env) {
    const currentMode = getCurrentColorMode();
    const isDark = currentMode === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark ? _t("Switch to Light Mode") : _t("Switch to Dark Mode"),
        callback: async () => {
            await toggleColorMode();
        },
        sequence: 5,
    };
}

registry.category("user_menuitems").add("ops_color_mode", colorModeToggleItem, { sequence: 5 });

console.log('[OPS Theme] User menu items loaded (v7.5.1 - cookie-based)');
