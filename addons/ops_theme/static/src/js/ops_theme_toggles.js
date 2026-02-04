/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v8.0.0 - Controller-Based)
 * ================================================================
 * Uses server-side controller endpoints with sudo() for reliable persistence.
 * Previous approach using ORM.write was silently blocked by SELF_WRITEABLE_FIELDS.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { cookie } from "@web/core/browser/cookie";
import { session } from "@web/session";

// =============================================================================
// COLOR MODE TOGGLE
// =============================================================================

function colorModeToggleItem(env) {
    // Read current mode from cookie (most reliable source on initial load)
    const currentScheme = cookie.get("color_scheme") || "light";
    const isDark = currentScheme === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark ? _t("☀️ Switch to Light Mode") : _t("🌙 Switch to Dark Mode"),
        callback: async function() {
            const newMode = isDark ? 'light' : 'dark';
            
            try {
                // Call controller endpoint (uses sudo() on server side)
                const result = await rpc("/ops_theme/toggle_color_mode", { mode: newMode });
                
                if (result && result.success) {
                    // Set cookie so Odoo loads correct CSS bundle on reload
                    cookie.set("color_scheme", result.mode);
                }
            } catch (error) {
                // Even if RPC fails, set cookie and reload
                cookie.set("color_scheme", newMode);
                console.warn("[OPS Theme] Color mode RPC failed, cookie set anyway:", error);
            }
            
            // ALWAYS reload to apply the change
            window.location.reload();
        },
        sequence: 5,
    };
}

// =============================================================================
// CHATTER POSITION TOGGLE
// =============================================================================

function chatterPositionToggleItem(env) {
    // Read from session (set by ir_http.session_info)
    const currentPosition = session.ops_chatter_position || 'bottom';
    const isBottom = currentPosition === 'bottom';

    return {
        type: "item",
        id: "ops_chatter_position",
        description: isBottom ? _t("📌 Chatter: Move to Side") : _t("📌 Chatter: Move to Bottom"),
        callback: async function() {
            try {
                // Call controller endpoint (uses sudo() on server side)
                await rpc("/ops_theme/toggle_chatter", {});
            } catch (error) {
                console.warn("[OPS Theme] Chatter toggle RPC failed:", error);
            }
            
            // ALWAYS reload to apply the change
            window.location.reload();
        },
        sequence: 10,
    };
}

// =============================================================================
// REGISTER MENU ITEMS
// =============================================================================

registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS Theme v8.0.0] Controller-based toggles loaded ✓');
