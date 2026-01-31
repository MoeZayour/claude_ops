/** @odoo-module **/

// =============================================================================
// OPS THEME - DEBRANDING JAVASCRIPT
// =============================================================================
// Removes Odoo.com links and enterprise features from JS registries
// =============================================================================

import { registry } from "@web/core/registry";

// -----------------------------------------------------------------------------
// Remove items from User Menu Registry
// -----------------------------------------------------------------------------
const userMenuRegistry = registry.category("user_menuitems");

// Items to remove from user menu
const userMenuItemsToRemove = [
    'odoo_account',      // My Odoo.com Account
    'install_app',       // Install App
    'upgrade',           // Upgrade prompt
    'odoo_help',         // Odoo Help (if exists)
    'documentation',     // Documentation link to odoo.com
];

// Remove each item if it exists
userMenuItemsToRemove.forEach(itemKey => {
    try {
        if (userMenuRegistry.contains(itemKey)) {
            userMenuRegistry.remove(itemKey);
            console.log(`OPS Theme: Removed '${itemKey}' from user menu`);
        }
    } catch (e) {
        // Item doesn't exist, ignore
    }
});

// -----------------------------------------------------------------------------
// Remove Enterprise-only systray items
// -----------------------------------------------------------------------------
const systrayRegistry = registry.category("systray");

const systrayItemsToRemove = [
    'upgrade',
    'enterprise_upgrade',
    'odoo_enterprise',
    'web_enterprise.ExpiredBanner',
];

systrayItemsToRemove.forEach(itemKey => {
    try {
        if (systrayRegistry.contains(itemKey)) {
            systrayRegistry.remove(itemKey);
            console.log(`OPS Theme: Removed '${itemKey}' from systray`);
        }
    } catch (e) {
        // Item doesn't exist, ignore
    }
});

// -----------------------------------------------------------------------------
// DOM Cleanup on Page Load (Fallback)
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
    // Hide enterprise elements function
    const hideEnterpriseElements = () => {
        // Hide by data attributes
        document.querySelectorAll('[data-menu="odoo_account"], [data-menu="install_app"]').forEach(el => {
            el.style.display = 'none';
        });

        // Hide by href
        document.querySelectorAll('a[href*="odoo.com"]').forEach(el => {
            // Keep documentation links if needed
            if (!el.href.includes('documentation') && !el.href.includes('github')) {
                el.style.display = 'none';
            }
        });

        // Hide enterprise classes
        document.querySelectorAll('.o_not_community, .o_enterprise_only, .o_upgrade_btn, .o_enterprise_label').forEach(el => {
            el.style.display = 'none';
        });

        // Hide upgrade buttons
        document.querySelectorAll('button[name="upgrade"], a.o_upgrade_btn, .o_settings_upgrade_btn').forEach(el => {
            el.style.display = 'none';
        });
    };

    // Run immediately
    hideEnterpriseElements();

    // Run again after short delay (for dynamically loaded content)
    setTimeout(hideEnterpriseElements, 1000);
    setTimeout(hideEnterpriseElements, 3000);
    setTimeout(hideEnterpriseElements, 5000);

    // Observe DOM changes and hide new enterprise elements
    const observer = new MutationObserver((mutations) => {
        let shouldCheck = false;
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                shouldCheck = true;
                break;
            }
        }
        if (shouldCheck) {
            hideEnterpriseElements();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

console.log('OPS Theme: Debranding module loaded');
