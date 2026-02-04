/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v7.6.3 - MINIMAL TEST)
 * ============================================================
 * TESTING: Do callbacks execute AT ALL?
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { session } from "@web/session";

// =============================================================================
// COLOR MODE TOGGLE - MINIMAL TEST
// =============================================================================

function colorModeToggleItem(env) {
    const currentScheme = cookie.get("color_scheme") || "light";
    const isDark = currentScheme === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark ? _t("☀️ Light Mode") : _t("🌙 Dark Mode"),
        callback: () => {
            alert(`CALLBACK WORKS! Current: ${currentScheme}`);
            console.log(`[OPS v7.6.3] CALLBACK EXECUTED! Current: ${currentScheme}`);
            const newScheme = isDark ? 'light' : 'dark';
            
            // Set cookie
            cookie.set("color_scheme", newScheme);
            
            // Save using ORM
            env.services.orm.write("res.users", [session.uid], {
                ops_color_mode: newScheme
            }).then(() => {
                console.log(`[OPS v7.6.3] SAVED! Now reloading...`);
                setTimeout(() => {
                    window.location.href = window.location.pathname + window.location.search;
                }, 100);
            }).catch(err => {
                console.error(`[OPS v7.6.3] Save failed:`, err);
                alert(`Save failed: ${err.message}`);
            });
        },
        sequence: 5,
    };
}

// =============================================================================
// CHATTER POSITION TOGGLE - MINIMAL TEST
// =============================================================================

function chatterPositionToggleItem(env) {
    const currentPosition = session.ops_chatter_position || 'bottom';
    const isBottom = currentPosition === 'bottom';

    return {
        type: "item",
        id: "ops_chatter_position",
        description: isBottom ? _t("📌 Chatter: Side") : _t("📌 Chatter: Bottom"),
        callback: () => {
            alert(`CALLBACK WORKS! Current: ${currentPosition}`);
            console.log(`[OPS v7.6.3] CALLBACK EXECUTED! Current: ${currentPosition}`);
            const newPosition = isBottom ? 'right' : 'bottom';
            
            // Save using ORM
            env.services.orm.write("res.users", [session.uid], {
                ops_chatter_position: newPosition
            }).then(() => {
                console.log(`[OPS v7.6.3] SAVED! Now reloading...`);
                setTimeout(() => {
                    window.location.href = window.location.pathname + window.location.search;
                }, 100);
            }).catch(err => {
                console.error(`[OPS v7.6.3] Save failed:`, err);
                alert(`Save failed: ${err.message}`);
            });
        },
        sequence: 10,
    };
}

// Register both items
registry.category("user_menuitems")
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS v7.6.3] Toggles loaded with ALERT test ✓');
