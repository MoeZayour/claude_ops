/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v7.6.5 - EXTREME DEBUG)
 * =============================================================
 * Added extreme logging to trace exact execution flow.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { user } from "@web/core/user";
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
        callback: async function() {
            console.log(`[OPS v7.6.5] === COLOR MODE TOGGLE CLICKED ===`);
            console.log(`[OPS v7.6.5] Current scheme from cookie: ${currentScheme}`);
            console.log(`[OPS v7.6.5] isDark: ${isDark}`);
            console.log(`[OPS v7.6.5] user.userId: ${user.userId}`);
            console.log(`[OPS v7.6.5] session.uid: ${session.uid}`);
            
            const newScheme = isDark ? 'light' : 'dark';
            console.log(`[OPS v7.6.5] New scheme will be: ${newScheme}`);
            
            try {
                // Set cookie
                console.log(`[OPS v7.6.5] Setting cookie...`);
                cookie.set("color_scheme", newScheme);
                const verifyC = cookie.get("color_scheme");
                console.log(`[OPS v7.6.5] Cookie now reads: ${verifyC}`);
                
                // Save to database
                console.log(`[OPS v7.6.5] Calling ORM.write...`);
                const result = await env.services.orm.write("res.users", [user.userId], {
                    ops_color_mode: newScheme
                });
                console.log(`[OPS v7.6.5] ORM.write result:`, result);
                console.log(`[OPS v7.6.5] Database saved successfully!`);
                
                // Reload
                console.log(`[OPS v7.6.5] About to reload...`);
                console.log(`[OPS v7.6.5] window.location.href =`, window.location.href);
                console.log(`[OPS v7.6.5] RELOADING NOW IN 3...2...1...`);
                
                window.location.href = window.location.href;
                
            } catch (error) {
                console.error(`[OPS v7.6.5] EXCEPTION CAUGHT:`, error);
                console.error(`[OPS v7.6.5] Error name:`, error.name);
                console.error(`[OPS v7.6.5] Error message:`, error.message);
                console.error(`[OPS v7.6.5] Error stack:`, error.stack);
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
        callback: async function() {
            console.log(`[OPS v7.6.5] === CHATTER TOGGLE CLICKED ===`);
            console.log(`[OPS v7.6.5] Current position: ${currentPosition}`);
            console.log(`[OPS v7.6.5] user.userId: ${user.userId}`);
            
            const newPosition = isBottom ? 'right' : 'bottom';
            console.log(`[OPS v7.6.5] New position will be: ${newPosition}`);
            
            try {
                console.log(`[OPS v7.6.5] Calling ORM.write...`);
                const result = await env.services.orm.write("res.users", [user.userId], {
                    ops_chatter_position: newPosition
                });
                console.log(`[OPS v7.6.5] ORM.write result:`, result);
                console.log(`[OPS v7.6.5] Database saved successfully!`);
                
                console.log(`[OPS v7.6.5] RELOADING NOW IN 3...2...1...`);
                window.location.href = window.location.href;
                
            } catch (error) {
                console.error(`[OPS v7.6.5] EXCEPTION CAUGHT:`, error);
                console.error(`[OPS v7.6.5] Error details:`, error.message, error.stack);
            }
        },
        sequence: 10,
    };
}

// Register both items
registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS v7.6.5] Toggles loaded (EXTREME DEBUG MODE) ✓');
