/** @odoo-module **/
/**
 * OPS Theme - Chatter Position Patch (v7.5.0 - ALIGNED WITH ODOO 19)
 * ===================================================================
 * Integrates WITH Odoo 19's native chatter layout system.
 * 
 * Odoo 19 Architecture:
 * - FormRenderer has mailLayout() method that determines chatter position
 * - Automatic based on screen size (uiService.size >= SIZES.XXL)
 * - FormCompiler reads mailLayout() at compile time
 * - Returns: SIDE_CHATTER, BOTTOM_CHATTER, COMBO, etc.
 * 
 * OPS Integration:
 * - Patches FormRenderer.mailLayout() to check user preference FIRST
 * - Falls back to Odoo's automatic screen size logic
 * - Respects all of Odoo's layout modes (COMBO, EXTERNAL, etc.)
 */

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";

patch(FormRenderer.prototype, {
    mailLayout(hasAttachmentContainer) {
        // First check if user has an explicit preference
        const userPreference = session.ops_chatter_position;
        
        if (userPreference) {
            const xxl = this.uiService.size >= SIZES.XXL;
            const hasFile = this.hasFile();
            const hasChatter = !!this.mailStore;
            const hasExternalWindow = !!this.mailPopoutService.externalWindow;
            
            // Handle external window cases (these are automatic)
            if (hasExternalWindow && hasFile && hasAttachmentContainer) {
                if (xxl) {
                    return "EXTERNAL_COMBO_XXL";
                }
                return "EXTERNAL_COMBO";
            }
            
            if (hasChatter) {
                // User wants chatter on the RIGHT (side)
                if (userPreference === 'right' || userPreference === 'side') {
                    if (xxl) {
                        if (hasAttachmentContainer && hasFile) {
                            return "COMBO"; // chatter bottom, attachment side
                        }
                        return "SIDE_CHATTER"; // chatter on side
                    }
                    // On smaller screens, force bottom (can't fit on side)
                    return "BOTTOM_CHATTER";
                }
                
                // User wants chatter at BOTTOM (or default)
                if (userPreference === 'bottom') {
                    return "BOTTOM_CHATTER"; // always bottom
                }
            }
            
            return "NONE";
        }
        
        // No user preference - fall back to Odoo's automatic logic
        return super.mailLayout(hasAttachmentContainer);
    },
});

console.log('[OPS Theme] Chatter position patch loaded (v7.5.0 - Odoo 19 compatible)');
