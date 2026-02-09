/** @odoo-module **/
/**
 * OPS Theme - Chatter Position Patch (v8.0.0 - COMPLETE FIX)
 * ============================================================
 * Integrates WITH Odoo 19's native chatter layout system.
 * 
 * Odoo 19 Architecture:
 * - FormRenderer.mailLayout() determines chatter position string
 * - FormCompiler uses mailLayout() to set isChatterAside / CSS classes
 * - FormController.className adds o_xxl_form_view on XXL screens
 *   which sets flex-flow: row nowrap (designed for side chatter)
 * 
 * The Bug (pre-v8.0):
 * - mailLayout() was patched to return BOTTOM_CHATTER correctly
 * - But o_xxl_form_view still forced row layout on the parent
 * - Chatter expanded horizontally instead of moving below
 * 
 * The Fix (v8.0.0):
 * - Patch BOTH mailLayout() AND FormController.className
 * - When user wants bottom: skip o_xxl_form_view -> column layout
 * - When user wants side: keep o_xxl_form_view -> row layout (native)
 */

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { FormController } from "@web/views/form/form_controller";
import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";

// =========================================================================
// PATCH 1: FormRenderer.mailLayout() - Control chatter position string
// =========================================================================
patch(FormRenderer.prototype, {
    mailLayout(hasAttachmentContainer) {
        const userPreference = session.ops_chatter_position;
        
        if (userPreference) {
            const xxl = this.uiService.size >= SIZES.XXL;
            const hasFile = this.hasFile();
            const hasChatter = !!this.mailStore;
            const hasExternalWindow = !!this.mailPopoutService.externalWindow;
            
            // External window cases - always automatic
            if (hasExternalWindow && hasFile && hasAttachmentContainer) {
                return xxl ? "EXTERNAL_COMBO_XXL" : "EXTERNAL_COMBO";
            }
            
            if (hasChatter) {
                if (userPreference === 'right' || userPreference === 'side') {
                    if (xxl) {
                        if (hasAttachmentContainer && hasFile) {
                            return "COMBO";
                        }
                        return "SIDE_CHATTER";
                    }
                    return "BOTTOM_CHATTER";
                }
                
                if (userPreference === 'bottom') {
                    return "BOTTOM_CHATTER";
                }
            }
            
            return "NONE";
        }
        
        // No preference - Odoo's automatic logic
        return super.mailLayout(hasAttachmentContainer);
    },
});

// =========================================================================
// PATCH 2: FormController.className - Control form layout direction
// =========================================================================
// o_xxl_form_view sets flex-flow: row nowrap on XXL screens.
// When user wants bottom chatter, we must skip this class so the form
// uses default column layout, placing chatter below naturally.
patch(FormController.prototype, {
    get className() {
        const result = super.className;
        
        const userPreference = session.ops_chatter_position;
        if (userPreference === 'bottom' && result["o_xxl_form_view h-100"]) {
            delete result["o_xxl_form_view h-100"];
            result["h-100"] = true;
        }
        
        return result;
    },
});

console.log('[OPS Theme] Chatter position patch loaded (v8.0.0 - dual patch)');
