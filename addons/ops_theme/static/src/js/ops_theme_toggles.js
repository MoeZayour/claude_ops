/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v10.0.0)
 * ==============================================
 * Chatter position toggle in the user menu.
 * Color mode toggle removed — light-only skin system.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { session } from "@web/session";

// =============================================================================
// HELPERS
// =============================================================================

/**
 * Resolve chatter position: user pref > company default > 'bottom'
 */
function resolveChatterPosition() {
    // 1. Session preference
    if (session.ops_chatter_position === 'side' || session.ops_chatter_position === 'bottom') {
        return session.ops_chatter_position;
    }
    // 2. Company default
    if (session.ops_default_chatter_position === 'side') {
        return 'side';
    }
    return 'bottom';
}

// =============================================================================
// CHATTER POSITION TOGGLE
// =============================================================================

function chatterPositionToggleItem(env) {
    const currentPosition = resolveChatterPosition();
    const isBottom = currentPosition === 'bottom';

    return {
        type: "item",
        id: "ops_chatter_position",
        description: isBottom
            ? _t("Chatter: Bottom  \u2192 Move to Side")
            : _t("Chatter: Side  \u2192 Move to Bottom"),
        callback: async () => {
            const newPosition = isBottom ? 'side' : 'bottom';

            // Persist to database via controller
            try {
                await rpc("/ops_theme/toggle_chatter", { position: newPosition });
            } catch (err) {
                console.warn("[OPS Theme] Chatter toggle save failed:", err);
            }

            // Reload to apply layout change
            window.location.reload();
        },
        sequence: 10,
    };
}

// =============================================================================
// REGISTER MENU ITEMS
// =============================================================================

registry.category("user_menuitems")
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });
