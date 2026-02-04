/** @odoo-module **/
/**
 * OPS Theme - User Menu Items (v7.5.3 - DEBUGGED)
 * ================================================
 * Adds color mode toggle to the user menu dropdown.
 * Uses Odoo 19's cookie-based system.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";

function getCurrentColorMode() {
    // Read from Odoo's cookie (this is what Odoo uses)
    const scheme = cookie.get("color_scheme");
    console.log('[OPS Theme Debug] Current cookie value:', scheme);
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
            try {
                const newMode = isDark ? 'light' : 'dark';
                
                console.log('[OPS Theme] Color mode toggle clicked!');
                console.log('[OPS Theme] Current:', currentMode, 'New:', newMode);
                
                // 1. Set Odoo's cookie
                cookie.set("color_scheme", newMode);
                console.log('[OPS Theme] Cookie set to:', newMode);
                
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
                    }).then(response => response.json())
                      .then(result => {
                          console.log('[OPS Theme] Save result:', result);
                          console.log('[OPS Theme] Reloading page...');
                          window.location.reload();
                      })
                      .catch(err => {
                          console.error('[OPS Theme] Error saving:', err);
                          // Still reload
                          window.location.reload();
                      });
                } else {
                    console.log('[OPS Theme] No session, reloading anyway...');
                    window.location.reload();
                }
            } catch (error) {
                console.error('[OPS Theme] Callback error:', error);
            }
        },
        sequence: 5,
    };
}

registry.category("user_menuitems").add("ops_color_mode", colorModeToggleItem, { sequence: 5 });

console.log('[OPS Theme] User menu items loaded (v7.5.3 - with debug logs)');
