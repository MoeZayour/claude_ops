/** @odoo-module **/
/**
 * OPS Theme - Chatter Position Toggle (v7.5.0 - ALIGNED WITH ODOO 19)
 * ====================================================================
 * Adds chatter position toggle to the user menu dropdown.
 * Works WITH Odoo 19's mailLayout system via FormRenderer patch.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";

function getCurrentChatterPosition() {
    return session.ops_chatter_position || 'bottom';
}

async function toggleChatterPosition() {
    const current = getCurrentChatterPosition();
    const newPosition = current === 'bottom' ? 'right' : 'bottom';
    
    console.log('[OPS Theme] Toggling chatter position from', current, 'to', newPosition);
    
    // Save to database
    if (window.odoo?.session_info?.uid) {
        try {
            const response = await fetch('/web/dataset/call_kw/res.users/write', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        model: 'res.users',
                        method: 'write',
                        args: [[window.odoo.session_info.uid], { ops_chatter_position: newPosition }],
                        kwargs: {},
                    },
                    id: Math.floor(Math.random() * 1000000),
                }),
            });

            const result = await response.json();
            
            if (result.error) {
                console.error('[OPS Theme] Failed to save chatter position:', result.error);
                return;
            }
            
            console.log('[OPS Theme] Chatter position saved:', newPosition);
            
            // Reload page to recompile forms with new preference
            // (FormCompiler runs at compile time, reads mailLayout())
            console.log('[OPS Theme] Reloading to apply chatter position...');
            setTimeout(() => {
                browser.location.reload();
            }, 200);
            
        } catch (err) {
            console.error('[OPS Theme] Error saving chatter position:', err);
        }
    }
}

function chatterPositionToggleItem(env) {
    const currentPosition = getCurrentChatterPosition();
    const isRight = currentPosition === 'right';

    return {
        type: "item",
        id: "ops_chatter_position",
        description: isRight ? _t("Chatter: Move to Bottom") : _t("Chatter: Move to Side"),
        callback: async () => {
            await toggleChatterPosition();
        },
        sequence: 10,
    };
}

registry.category("user_menuitems").add("ops_chatter_position", chatterPositionToggleItem, { sequence: 10 });

console.log('[OPS Theme] Chatter toggle loaded (v7.5.0 - Odoo 19 compatible)');
