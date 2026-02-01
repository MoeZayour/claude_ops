/** @odoo-module **/
/**
 * OPS Theme - Chatter Position Toggle
 * ====================================
 * Adds chatter position toggle to the user menu dropdown.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function getCurrentChatterPosition() {
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

function toggleChatterPosition() {
    const current = getCurrentChatterPosition();
    const newPosition = current === 'bottom' ? 'right' : 'bottom';
    applyChatterPosition(newPosition);
    console.log('[OPS Theme] Chatter position toggled to:', newPosition);

    // Save to server
    if (window.odoo?.session_info?.uid) {
        fetch('/web/dataset/call_kw/res.users/write', {
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
        }).catch(err => console.warn('[OPS Theme] Could not save chatter position:', err));
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
            toggleChatterPosition();
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

console.log('[OPS Theme] Chatter toggle loaded');
