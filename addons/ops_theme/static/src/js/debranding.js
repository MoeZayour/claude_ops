/** @odoo-module **/
/**
 * OPS Framework — Dynamic Debranding Runtime Interceptor
 * ======================================================
 *
 * Three-pronged approach:
 * 1. REGISTRY CLEANUP — Remove Odoo items from OWL registries before render
 * 2. DOM INTERCEPTOR  — MutationObserver catches dynamically injected elements
 * 3. TITLE ENFORCER   — Keeps browser tab title clean
 *
 * This runs once at module load and stays active for the session lifetime.
 */

import { registry } from "@web/core/registry";

// =============================================================================
// CONFIGURATION
// =============================================================================

const OPS_TITLE = "OPS Framework";

// Registry items to remove (user menu dropdown)
const USER_MENU_REMOVE = [
    "odoo_account",      // My Odoo.com Account
    "install_app",       // Install App
    "upgrade",           // Upgrade
    "odoo_help",         // Odoo Help
    "documentation",     // Odoo Documentation
    "support",           // Odoo Support
];

// Systray items to remove (top-right icons)
const SYSTRAY_REMOVE = [
    "upgrade",
    "enterprise_upgrade",
    "odoo_enterprise",
    "web_enterprise.ExpiredBanner",
    "BurgerMenu.CompanyItem",
];

// CSS selectors for DOM cleanup (backup for anything CSS misses)
const HIDE_SELECTORS = [
    'a[href*="odoo.com"]:not([href*="documentation"])',
    '[class*="o_enterprise_upgrade"]',
    '[class*="o_upgrade"]',
    'button[name="upgrade"]',
    '.o_not_community',
    '[class*="o_database_expiration"]',
    '.o_login_footer',
    'img[src*="odoo_logo"]',
    'a.o_odoo_icon',
    '.o_brand_promotion',
    '[class*="o_enterprise_label"]',
    '.o_settings_upgrade_btn',
    '[data-menu="odoo_account"]',
    '[data-menu="install_app"]',
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
                    console.debug(`[OPS Debranding] Removed '${key}' from ${categoryName}`);
                }
            } catch (e) {
                // Item doesn't exist, silent
            }
        }
    } catch (e) {
        // Category doesn't exist, silent
    }
}

// Clean user menu
cleanRegistry("user_menuitems", USER_MENU_REMOVE);

// Clean systray
cleanRegistry("systray", SYSTRAY_REMOVE);

// =============================================================================
// 2. DOM INTERCEPTOR — MutationObserver for dynamic content
// =============================================================================

function hideMatchingElements() {
    for (const selector of HIDE_SELECTORS) {
        try {
            document.querySelectorAll(selector).forEach(el => {
                if (el.style.display !== "none") {
                    el.style.display = "none";
                }
            });
        } catch (e) {
            // Invalid selector or element already removed
        }
    }
}

function initDomInterceptor() {
    // Run immediately
    hideMatchingElements();

    // Observe DOM for dynamically added elements
    const observer = new MutationObserver((mutations) => {
        let shouldRun = false;
        for (const m of mutations) {
            if (m.addedNodes.length > 0) {
                shouldRun = true;
                break;
            }
        }
        if (shouldRun) {
            hideMatchingElements();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });

    // Cleanup on page unload
    window.addEventListener("beforeunload", () => {
        observer.disconnect();
    });

    console.debug("[OPS Debranding] DOM interceptor active");
}

// =============================================================================
// 3. TITLE ENFORCER — Replace "Odoo" in document title
// =============================================================================

function enforceTitle() {
    const originalDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, "title") ||
                               Object.getOwnPropertyDescriptor(HTMLDocument.prototype, "title");

    if (originalDescriptor && originalDescriptor.set) {
        Object.defineProperty(document, "title", {
            get: function() {
                return originalDescriptor.get.call(this);
            },
            set: function(val) {
                const cleaned = val.replace(/Odoo/gi, OPS_TITLE);
                originalDescriptor.set.call(this, cleaned);
            },
            configurable: true,
        });
    }

    // Also clean current title
    if (document.title && document.title.includes("Odoo")) {
        document.title = document.title.replace(/Odoo/gi, OPS_TITLE);
    }

    console.debug("[OPS Debranding] Title enforcer active");
}

// =============================================================================
// 4. FAVICON OVERRIDE
// =============================================================================

function overrideFavicon() {
    const links = document.querySelectorAll('link[rel*="icon"]');
    links.forEach(link => {
        if (link.href && link.href.includes("odoo")) {
            link.href = "/ops_theme/favicon";
        }
    });
}

// =============================================================================
// INITIALIZATION
// =============================================================================

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        initDomInterceptor();
        enforceTitle();
        overrideFavicon();
    });
} else {
    initDomInterceptor();
    enforceTitle();
    overrideFavicon();
}

console.log("[OPS Debranding] Module loaded — 4-layer interceptor active");
