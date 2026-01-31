/** @odoo-module **/

import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { append, setAttributes } from '@web/core/utils/xml';
import { FormCompiler } from '@web/views/form/form_compiler';

/**
 * OPS Theme - FormCompiler Patch
 *
 * This patch handles chatter positioning based on user preference.
 * When chatter_position is 'bottom', the chatter is moved inside the form sheet.
 * When chatter_position is 'side' (default Odoo), chatter stays on the right side.
 */
patch(FormCompiler.prototype, {
    /**
     * Override compile to handle chatter positioning based on user preference.
     * When chatter_position is 'bottom', move chatter inside the form sheet.
     */
    compile(node, params) {
        const res = super.compile(node, params);

        // Find chatter container - try multiple selectors for compatibility
        const chatterContainerHookXml = res.querySelector(
            '.o_form_renderer > .o-mail-Form-chatter'
        ) || res.querySelector(
            '.o-mail-Form-chatter'
        ) || res.querySelector(
            '[class*="chatter"]'
        );

        if (!chatterContainerHookXml) {
            return res;
        }

        // Set ref for potential JS access
        setAttributes(chatterContainerHookXml, {
            't-ref': 'chatterContainer',
        });

        // Handle bottom position (user preference from session)
        if (session.chatter_position === 'bottom') {
            const formSheetBgXml = res.querySelector('.o_form_sheet_bg');

            if (!formSheetBgXml?.parentNode) {
                return res;
            }

            // Get the chatter component
            const chatterContainerXml = chatterContainerHookXml.querySelector(
                "t[t-component='__comp__.mailComponents.Chatter']"
            );

            // Clone and modify for bottom position
            const sheetBgChatterContainerHookXml = chatterContainerHookXml.cloneNode(true);
            const sheetBgChatterContainerXml = sheetBgChatterContainerHookXml.querySelector(
                "t[t-component='__comp__.mailComponents.Chatter']"
            );

            // Add classes for bottom positioning
            sheetBgChatterContainerHookXml.classList.add('o-isInFormSheetBg', 'w-auto', 'mt-4');

            // Append to form sheet background
            append(formSheetBgXml, sheetBgChatterContainerHookXml);

            // Set attributes for bottom mode on both original and cloned
            if (sheetBgChatterContainerXml) {
                setAttributes(sheetBgChatterContainerXml, {
                    isInFormSheetBg: 'true',
                    isChatterAside: 'false',
                });
            }

            if (chatterContainerXml) {
                setAttributes(chatterContainerXml, {
                    isInFormSheetBg: 'true',
                    isChatterAside: 'false',
                });
            }

            // Hide original chatter container (it's now in the sheet)
            setAttributes(chatterContainerHookXml, {
                't-if': 'false',
            });

            // Also hide attachment preview if present (for bottom mode)
            const webClientViewAttachmentViewHookXml = res.querySelector('.o_attachment_preview');
            if (webClientViewAttachmentViewHookXml) {
                setAttributes(webClientViewAttachmentViewHookXml, {
                    't-if': 'false',
                });
            }
        }

        return res;
    },
});
