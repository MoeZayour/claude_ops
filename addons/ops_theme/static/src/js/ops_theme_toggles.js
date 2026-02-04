/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v7.6.1 - SERVICE-BASED)
 * =============================================================
 * Provides color mode and chatter position toggles in the user menu.
 * Uses Odoo 19 services (orm, cookie) for reliability.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { session } from "@web/session";

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
        callback: async () => {
            const newScheme = isDark ? 'light' : 'dark';
            console.log(`[OPS v7.6.1] Color mode: ${currentScheme} → ${newScheme}`);
            
            try {
                // Set cookie (Odoo reads this)
                cookie.set("color_scheme", newScheme);
                console.log(`[OPS v7.6.1] Cookie set`);
                
                // Save to database using ORM service
                await env.services.orm.write("res.users", [session.uid], {
                    ops_color_mode: newScheme
                });
                console.log(`[OPS v7.6.1] Saved to DB`);
                
                // Reload
                console.log(`[OPS v7.6.1] RELOADING NOW...`);
                window.location.reload();
                
            } catch (error) {
                console.error(`[OPS v7.6.1] ERROR:`, error);
                // Try to reload anyway
                window.location.reload();
            }
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
        callback: async () => {
            const newPosition = isBottom ? 'right' : 'bottom';
            console.log(`[OPS v7.6.1] Chatter: ${currentPosition} → ${newPosition}`);
            
            try {
                // Save to database using ORM service
                await env.services.orm.write("res.users", [session.uid], {
                    ops_chatter_position: newPosition
                });
                console.log(`[OPS v7.6.1] Saved to DB`);
                
                // Reload
                console.log(`[OPS v7.6.1] RELOADING NOW...`);
                window.location.reload();
                
            } catch (error) {
                console.error(`[OPS v7.6.1] ERROR:`, error);
                // Try to reload anyway
                window.location.reload();
            }
        },
        sequence: 10,
    };
}

// Register both items
registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS v7.6.1] Theme toggles loaded (using services.orm) ✓');
