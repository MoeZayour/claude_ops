/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v7.6.0 - FINAL SIMPLIFIED VERSION)
 * ========================================================================
 * Provides color mode and chatter position toggles in the user menu.
 * Integrates WITH Odoo 19's native systems (cookie + mailLayout).
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { session } from "@web/session";
import { rpc } from "@web/core/network/rpc";

// =============================================================================
// COLOR MODE TOGGLE
// =============================================================================

function colorModeToggleItem(env) {
    const currentScheme = cookie.get("color_scheme") || "light";
    const isDark = currentScheme === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark ? _t("☀️ Light Mode") : _t("🌙 Dark Mode"),
        callback: () => {
            const newScheme = isDark ? 'light' : 'dark';
            console.log(`[OPS v7.6.0] Color mode: ${currentScheme} → ${newScheme}`);
            
            // Set cookie (Odoo reads this)
            cookie.set("color_scheme", newScheme);
            
            // Save to database (for persistence across browsers)
            rpc("/web/dataset/call_kw/res.users/write", {
                model: "res.users",
                method: "write",
                args: [[session.uid], { ops_color_mode: newScheme }],
                kwargs: {},
            }).then(() => {
                console.log(`[OPS v7.6.0] Saved. Reloading...`);
                window.location.reload();
            }).catch(() => {
                console.log(`[OPS v7.6.0] Save failed. Reloading anyway...`);
                window.location.reload();
            });
        },
        sequence: 5,
    };
}

// =============================================================================
// CHATTER POSITION TOGGLE
// =============================================================================

function chatterPositionToggleItem(env) {
    const currentPosition = session.ops_chatter_position || 'bottom';
    const isBottom = currentPosition === 'bottom';

    return {
        type: "item",
        id: "ops_chatter_position",
        description: isBottom ? _t("📌 Chatter: Side") : _t("📌 Chatter: Bottom"),
        callback: () => {
            const newPosition = isBottom ? 'right' : 'bottom';
            console.log(`[OPS v7.6.0] Chatter: ${currentPosition} → ${newPosition}`);
            
            // Save to database
            rpc("/web/dataset/call_kw/res.users/write", {
                model: "res.users",
                method: "write",
                args: [[session.uid], { ops_chatter_position: newPosition }],
                kwargs: {},
            }).then(() => {
                console.log(`[OPS v7.6.0] Saved. Reloading...`);
                window.location.reload();
            }).catch(() => {
                console.log(`[OPS v7.6.0] Save failed but reloading...`);
                window.location.reload();
            });
        },
        sequence: 10,
    };
}

// Register both items
registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS v7.6.0] Theme toggles loaded ✓');
