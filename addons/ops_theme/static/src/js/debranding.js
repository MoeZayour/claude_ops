/** @odoo-module **/
/**
 * OPS Framework — Debranding
 * ==========================
 * Two-layer approach:
 * 1. REGISTRY CLEANUP — Remove Odoo items from OWL registries before render
 * 2. TITLE ENFORCER   — Keeps browser tab title clean
 *
 * CSS handles all visual debranding (_debranding.scss).
 * No MutationObserver needed — CSS is faster and more reliable.
 */

import { registry } from "@web/core/registry";

const OPS_TITLE = "OPS Framework";

// Registry items to remove (user menu dropdown)
const USER_MENU_REMOVE = [
    "odoo_account",
    "install_app",
    "upgrade",
    "odoo_help",
    "documentation",
    "support",
];

// Systray items to remove (top-right icons)
const SYSTRAY_REMOVE = [
    "upgrade",
    "enterprise_upgrade",
    "odoo_enterprise",
    "web_enterprise.ExpiredBanner",
    "BurgerMenu.CompanyItem",
];

// =============================================================================
// 1. REGISTRY CLEANUP — Remove items before they render
// =============================================================================

function cleanRegistry(categoryName, itemsToRemove) {
    try {
        const cat = registry.category(categoryName);
        for (const key of itemsToRemove) {
            try {
                if (cat.contains(key)) {
                    cat.remove(key);
                }
            } catch (e) { /* Item doesn't exist */ }
        }
    } catch (e) { /* Category doesn't exist */ }
}

cleanRegistry("user_menuitems", USER_MENU_REMOVE);
cleanRegistry("systray", SYSTRAY_REMOVE);

// =============================================================================
// 2. TITLE ENFORCER — Replace "Odoo" in document title
// =============================================================================

function enforceTitle() {
    const desc = Object.getOwnPropertyDescriptor(Document.prototype, "title") ||
                 Object.getOwnPropertyDescriptor(HTMLDocument.prototype, "title");

    if (desc && desc.set) {
        Object.defineProperty(document, "title", {
            get() { return desc.get.call(this); },
            set(val) { desc.set.call(this, val.replace(/Odoo/gi, OPS_TITLE)); },
            configurable: true,
        });
    }

    if (document.title && document.title.includes("Odoo")) {
        document.title = document.title.replace(/Odoo/gi, OPS_TITLE);
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        enforceTitle();
    });
} else {
    enforceTitle();
}
