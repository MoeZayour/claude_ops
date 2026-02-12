/** @odoo-module **/
/**
 * OPS Theme - Chatter Position Patch (v9.0.0 - CSS-driven approach)
 * ==================================================================
 * Uses a data attribute on <html> + CSS to control chatter layout.
 *
 * Previous approach (v8.0) tried to patch FormController.className getter
 * to remove o_xxl_form_view. This was fragile because Odoo's patch()
 * system for getters uses [[HomeObject]] prototype chaining which can
 * silently fail depending on load order.
 *
 * v9.0.0 approach:
 * 1. Patch FormRenderer.mailLayout() to return BOTTOM_CHATTER (same as before)
 * 2. Set data-ops-chatter attribute on <html> at module load time
 * 3. CSS handles the layout override (see _chatter_position.scss)
 *
 * This is bulletproof: no getter patching, no className manipulation,
 * just a data attribute that CSS reads declaratively.
 */

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";

// =========================================================================
// STEP 1: Set data-ops-chatter attribute on <html> at load time
// =========================================================================
// session_info is already populated by ir_http.py before JS modules execute.
// This attribute is read by _chatter_position.scss to override XXL layout.

const chatterPosition = session.ops_chatter_position
    || session.ops_default_chatter_position
    || 'bottom';
document.documentElement.setAttribute('data-ops-chatter', chatterPosition);

console.log('[OPS Theme] Chatter position:', chatterPosition, '(data-ops-chatter set on <html>)');

// =========================================================================
// STEP 2: Patch FormRenderer.mailLayout() — Control chatter position string
// =========================================================================
// This controls whether the Chatter component gets isChatterAside=true/false
// and CSS classes o-aside vs mt-4 on the chatter container.

patch(FormRenderer.prototype, {
    mailLayout(hasAttachmentContainer) {
        const userPreference = session.ops_chatter_position;

        if (userPreference) {
            const xxl = this.uiService.size >= SIZES.XXL;
            const hasFile = this.hasFile();
            const hasChatter = !!this.mailStore;
            const hasExternalWindow = !!this.mailPopoutService.externalWindow;

            // External window cases — always automatic
            if (hasExternalWindow && hasFile && hasAttachmentContainer) {
                return xxl ? "EXTERNAL_COMBO_XXL" : "EXTERNAL_COMBO";
            }

            if (hasChatter) {
                if (userPreference === 'right' || userPreference === 'side') {
                    // User wants side: return native XXL behavior
                    if (xxl) {
                        if (hasAttachmentContainer && hasFile) {
                            return "COMBO";
                        }
                        return "SIDE_CHATTER";
                    }
                    return "BOTTOM_CHATTER";
                }

                if (userPreference === 'bottom') {
                    // User wants bottom: always bottom, even on XXL
                    return "BOTTOM_CHATTER";
                }
            }

            return "NONE";
        }

        // No preference — Odoo's automatic logic
        return super.mailLayout(hasAttachmentContainer);
    },
});

console.log('[OPS Theme] Chatter position patch loaded (v9.0.0 - CSS-driven)');
