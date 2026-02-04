/** @odoo-module **/
/**
 * OPS Theme - User Menu Items (v7.5.2 - WORKING)
 * ===============================================
 * Adds color mode toggle to the user menu dropdown.
 * Uses Odoo 19's cookie-based system.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { browser } from "@web/core/browser/browser";

function getCurrentColorMode() {
    // Read from Odoo's cookie (this is what Odoo uses)
    const scheme = cookie.get("color_scheme");
    return scheme === 'dark' ? 'dark' : 'light';
}

function colorModeToggleItem(env) {
    const currentMode = getCurrentColorMode();
    const isDark = currentMode === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark ? _t("Switch to Light Mode") : _t("Switch to Dark Mode"),
        callback: () => {
            const newMode = isDark ? 'light' : 'dark';
            
            console.log('[OPS Theme] Toggling color mode from', currentMode, 'to', newMode);
            
            // 1. Set Odoo's cookie
            cookie.set("color_scheme", newMode);
            
            // 2. Save to database for persistence
            if (window.odoo?.session_info?.uid) {
                fetch('/web/dataset/call_kw/res.users/write', {
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
                }).then(() => {
                    console.log('[OPS Theme] Color mode saved, reloading...');
                    // 3. Reload page to load correct CSS files
                    setTimeout(() => {
                        browser.location.reload();
                    }, 200);
                }).catch(err => {
                    console.error('[OPS Theme] Error saving color mode:', err);
                    // Still reload to apply cookie change
                    setTimeout(() => {
                        browser.location.reload();
                    }, 200);
                });
            } else {
                // No session, just reload
                setTimeout(() => {
                    browser.location.reload();
                }, 200);
            }
        },
        sequence: 5,
    };
}

registry.category("user_menuitems").add("ops_color_mode", colorModeToggleItem, { sequence: 5 });

console.log('[OPS Theme] User menu items loaded (v7.5.2 - working callbacks)');
