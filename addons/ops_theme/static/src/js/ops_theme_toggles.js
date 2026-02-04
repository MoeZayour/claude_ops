/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v7.6.4 - FIXED ORM CALL)
 * ==============================================================
 * Fixed: ORM.write expects [id] not session.uid directly
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { user } from "@web/core/user";

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
        callback: async function() {
            const newScheme = isDark ? 'light' : 'dark';
            console.log(`[OPS v7.6.4] Color: ${currentScheme} → ${newScheme}`);
            
            try {
                // Set cookie
                cookie.set("color_scheme", newScheme);
                
                // Save using user.userId (not session.uid)
                await env.services.orm.write("res.users", [user.userId], {
                    ops_color_mode: newScheme
                });
                console.log(`[OPS v7.6.4] Saved! Reloading...`);
                
                // Reload page
                window.location.href = window.location.pathname + window.location.search;
                
            } catch (error) {
                console.error(`[OPS v7.6.4] Error:`, error);
                // Reload anyway to apply cookie
                window.location.href = window.location.pathname + window.location.search;
            }
        },
        sequence: 5,
    };
}

// =============================================================================
// CHATTER POSITION TOGGLE
// =============================================================================

function chatterPositionToggleItem(env) {
    const currentPosition = env.services?.['mail.store']?.__userSettings?.chatterPosition || 
                            user.settings?.chatterPosition || 
                            'bottom';
    const isBottom = currentPosition === 'bottom';

    return {
        type: "item",
        id: "ops_chatter_position",
        description: isBottom ? _t("📌 Chatter: Side") : _t("📌 Chatter: Bottom"),
        callback: async function() {
            const newPosition = isBottom ? 'right' : 'bottom';
            console.log(`[OPS v7.6.4] Chatter: ${currentPosition} → ${newPosition}`);
            
            try {
                // Save using user.userId
                await env.services.orm.write("res.users", [user.userId], {
                    ops_chatter_position: newPosition
                });
                console.log(`[OPS v7.6.4] Saved! Reloading...`);
                
                // Reload page
                window.location.href = window.location.pathname + window.location.search;
                
            } catch (error) {
                console.error(`[OPS v7.6.4] Error:`, error);
                // Reload anyway
                window.location.href = window.location.pathname + window.location.search;
            }
        },
        sequence: 10,
    };
}

// Register both items
registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS v7.6.4] Toggles loaded (fixed ORM.write call) ✓');
