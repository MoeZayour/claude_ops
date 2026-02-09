/** @odoo-module **/
/**
 * OPS Theme - User Preference Toggles (v9.0.0)
 * ==============================================
 * Professional state-aware user menu items for color mode and chatter position.
 *
 * Architecture:
 * - Reads current state from cookie/session (fastest)
 * - Falls back to company defaults from session_info (for new users)
 * - Saves to res.users via sudo controller endpoint
 * - Applies immediately via DOM + cookie, then reloads
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { cookie } from "@web/core/browser/cookie";
import { session } from "@web/session";

// =============================================================================
// HELPERS
// =============================================================================

/**
 * Resolve color mode: user pref > company default > 'light'
 */
function resolveColorMode() {
    // 1. Cookie is set by Odoo's native dark mode system
    const fromCookie = cookie.get("color_scheme");
    if (fromCookie === 'dark' || fromCookie === 'light') {
        return fromCookie;
    }
    // 2. Session preference (set by ir_http.session_info)
    if (session.ops_color_mode === 'dark' || session.ops_color_mode === 'light') {
        return session.ops_color_mode;
    }
    // 3. Company default (injected by ir_http.session_info)
    if (session.ops_default_color_mode === 'dark') {
        return 'dark';
    }
    return 'light';
}

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
// COLOR MODE TOGGLE
// =============================================================================

function colorModeToggleItem(env) {
    const currentMode = resolveColorMode();
    const isDark = currentMode === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark
            ? _t("Color Mode: Dark  \u2192 Switch to Light")
            : _t("Color Mode: Light  \u2192 Switch to Dark"),
        callback: async () => {
            const newMode = isDark ? 'light' : 'dark';

            // 1. Set cookie immediately (Odoo reads this for CSS bundle)
            // TTL = 1 year in seconds — matches Odoo's native cookie lifetime
            cookie.set("color_scheme", newMode, 365 * 24 * 60 * 60);

            // 2. Persist to database via controller
            try {
                await rpc("/ops_theme/toggle_color_mode", { mode: newMode });
            } catch (err) {
                console.warn("[OPS Theme] Color mode save failed:", err);
            }

            // 3. Reload to apply CSS bundle switch
            window.location.reload();
        },
        sequence: 5,
    };
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
    .add("ops_color_mode", colorModeToggleItem, { sequence: 5 })
    .add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });
