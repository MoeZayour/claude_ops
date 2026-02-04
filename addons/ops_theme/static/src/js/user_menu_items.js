/** @odoo-module **/
/**
 * OPS Theme - User Menu Items
 * ===========================
 * Adds color mode toggle to the user menu dropdown.
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function getCurrentColorMode() {
    // Try global function first
    if (typeof window.getOpsColorMode === 'function') {
        return window.getOpsColorMode();
    }
    // Fallback to DOM attribute
    const attr = document.documentElement.getAttribute('data-color-mode');
    if (attr === 'light' || attr === 'dark') {
        return attr;
    }
    // Fallback to localStorage
    const stored = localStorage.getItem('ops_color_mode');
    if (stored === 'light' || stored === 'dark') {
        return stored;
    }
    // Default
    return 'light';
}

function toggleColorMode() {
    const current = getCurrentColorMode();
    const newMode = current === 'light' ? 'dark' : 'light';

    // Use global function if available
    if (typeof window.setOpsColorMode === 'function') {
        window.setOpsColorMode(newMode);
    } else {
        // Fallback: apply directly
        document.documentElement.setAttribute('data-color-mode', newMode);
        localStorage.setItem('ops_color_mode', newMode);

        if (newMode === 'dark') {
            document.documentElement.classList.add('ops-dark-mode');
            document.body?.classList.add('ops-dark-mode');
        } else {
            document.documentElement.classList.remove('ops-dark-mode');
            document.body?.classList.remove('ops-dark-mode');
        }
    }

    console.log('[OPS Theme] Color mode toggled to:', newMode);
}

// =============================================================================
// COLOR MODE TOGGLE MENU ITEM
// =============================================================================

function colorModeToggleItem(env) {
    const currentMode = getCurrentColorMode();
    const isDark = currentMode === 'dark';

    return {
        type: "item",
        id: "ops_color_mode",
        description: isDark ? _t("Switch to Light Mode") : _t("Switch to Dark Mode"),
        callback: async () => {
            toggleColorMode();
            // Reload the menu to update the description
            // The menu will close after click, so user sees new mode on next open
        },
        sequence: 5,
    };
}

registry.category("user_menuitems").add("ops_color_mode", colorModeToggleItem, { sequence: 5 });

console.log('[OPS Theme] User menu items loaded');
