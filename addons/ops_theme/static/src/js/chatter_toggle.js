/** @odoo-module **/
/**
 * OPS Theme - Chatter Position Toggle (FIXED v7.4.0)
 * ===================================================
 * Adds chatter position toggle to the user menu dropdown.
 * 
 * BUG FIX: FormCompiler reads session.chatter_position at compile time,
 * which is static. After toggling, we now reload the page to refresh
 * the session with the new preference.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function getCurrentChatterPosition() {
    // First check session (authoritative)
    if (window.odoo?.session_info?.ops_chatter_position) {
        return window.odoo.session_info.ops_chatter_position;
    }
    
    // Fallback to localStorage
    const stored = localStorage.getItem('ops_chatter_position');
    if (stored === 'side' || stored === 'right') {
        return 'right';
    }
    return 'bottom';
}

function applyChatterPosition(position) {
    localStorage.setItem('ops_chatter_position', position);

    // Apply class to all form views
    const formViews = document.querySelectorAll('.o_form_view');
    formViews.forEach(form => {
        if (position === 'right') {
            form.classList.add('ops-chatter-right');
        } else {
            form.classList.remove('ops-chatter-right');
        }
    });

    // Set on document for future form views
    if (position === 'right') {
        document.documentElement.classList.add('ops-chatter-right-enabled');
    } else {
        document.documentElement.classList.remove('ops-chatter-right-enabled');
    }
}

async function toggleChatterPosition() {
    const current = getCurrentChatterPosition();
    const newPosition = current === 'bottom' ? 'right' : 'bottom';
    
    console.log('[OPS Theme] Toggling chatter position from', current, 'to', newPosition);
    
    // Apply locally first
    applyChatterPosition(newPosition);

    // Save to server
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
            
            console.log('[OPS Theme] Chatter position saved to server:', newPosition);
            
            // CRITICAL FIX: Reload page to refresh session and re-compile forms
            // FormCompiler reads session.chatter_position at compile time,
            // so we need a fresh session for it to pick up the new value
            console.log('[OPS Theme] Reloading page to apply chatter position change...');
            setTimeout(() => {
                browser.location.reload();
            }, 300);
            
        } catch (err) {
            console.error('[OPS Theme] Error saving chatter position:', err);
        }
    }
}

// =============================================================================
// CHATTER POSITION TOGGLE MENU ITEM
// =============================================================================

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

// =============================================================================
// APPLY SAVED POSITION ON PAGE LOAD
// =============================================================================

function initChatterPosition() {
    const savedPosition = getCurrentChatterPosition();
    applyChatterPosition(savedPosition);
    console.log('[OPS Theme] Chatter position initialized to:', savedPosition);
}

// Apply on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatterPosition);
} else {
    initChatterPosition();
}

// Also apply when navigating (Odoo SPA)
const originalPushState = history.pushState;
history.pushState = function() {
    originalPushState.apply(this, arguments);
    setTimeout(() => {
        const savedPosition = getCurrentChatterPosition();
        applyChatterPosition(savedPosition);
    }, 100);
};

console.log('[OPS Theme] Chatter toggle loaded (v7.4.0 - fixed persistence with page reload)');
