/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v7.6.2 - DIRECT RELOAD)
 * =============================================================
 * Provides color mode and chatter position toggles.
 * Uses direct window.location.href for guaranteed reload.
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
        callback: async function() {  // Note: function() not arrow function
            const newScheme = isDark ? 'light' : 'dark';
            console.log(`[OPS v7.6.2] CLICKED! Color: ${currentScheme} → ${newScheme}`);
            
            // Set cookie immediately
            cookie.set("color_scheme", newScheme);
            console.log(`[OPS v7.6.2] Cookie set to: ${newScheme}`);
            
            // Save to database
            try {
                await env.services.orm.write("res.users", [session.uid], {
                    ops_color_mode: newScheme
                });
                console.log(`[OPS v7.6.2] Saved to database`);
            } catch (error) {
                console.error(`[OPS v7.6.2] Save error (will reload anyway):`, error);
            }
            
            // Reload using direct href assignment (more reliable than reload())
            console.log(`[OPS v7.6.2] Navigating to trigger reload...`);
            window.location.href = window.location.href;
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
        callback: async function() {  // Note: function() not arrow function
            const newPosition = isBottom ? 'right' : 'bottom';
            console.log(`[OPS v7.6.2] CLICKED! Chatter: ${currentPosition} → ${newPosition}`);
            
            // Save to database
            try {
                await env.services.orm.write("res.users", [session.uid], {
                    ops_chatter_position: newPosition
                });
                console.log(`[OPS v7.6.2] Saved to database`);
            } catch (error) {
                console.error(`[OPS v7.6.2] Save error (will reload anyway):`, error);
            }
            
            // Reload using direct href assignment
            console.log(`[OPS v7.6.2] Navigating to trigger reload...`);
            window.location.href = window.location.href;
        },
        sequence: 10,
    };
}

// Register both items
registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS v7.6.2] Theme toggles loaded (async function + href navigation) ✓');
