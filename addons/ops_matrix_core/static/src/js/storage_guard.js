/** @odoo-module **/

import { browser } from "@web/core/browser/browser";

/**
 * OPS Matrix Core - LocalStorage Safety Guard
 * 
 * Purpose: Prevent QuotaExceededError crashes during menu loading
 * Issue: Odoo 19 stores webclient_menus in localStorage which can exceed quota with large menu structures
 * Solution: Catch QuotaExceededError, clear problematic keys, and reload gracefully
 */

const STORAGE_KEYS_TO_CLEAR = [
    'webclient_menus',
    'web.webclient.menus',
    'odoo.menus',
];

/**
 * Wrap localStorage.setItem with error handling
 */
const originalSetItem = Storage.prototype.setItem;
Storage.prototype.setItem = function(key, value) {
    try {
        originalSetItem.call(this, key, value);
    } catch (error) {
        if (error.name === 'QuotaExceededError' || error.code === 22) {
            console.warn('⚠️ OPS Matrix: LocalStorage quota exceeded. Clearing menu cache...');
            
            // Clear known problematic keys
            STORAGE_KEYS_TO_CLEAR.forEach(storageKey => {
                try {
                    localStorage.removeItem(storageKey);
                    console.log(`✓ Cleared: ${storageKey}`);
                } catch (e) {
                    console.error(`Failed to clear ${storageKey}:`, e);
                }
            });
            
            // Try again after clearing
            try {
                originalSetItem.call(this, key, value);
                console.log('✓ Successfully stored data after clearing cache');
            } catch (retryError) {
                console.error('❌ Still failed after clearing cache. Consider reducing menu items.');
                
                // Show user-friendly notification
                if (typeof browser !== 'undefined' && browser.localStorage) {
                    // Notify user about the issue
                    const event = new CustomEvent('ops_storage_quota_exceeded', {
                        detail: {
                            message: 'Menu cache cleared due to storage limit. Please refresh the page.',
                            action: 'reload'
                        }
                    });
                    window.dispatchEvent(event);
                }
            }
        } else {
            throw error;
        }
    }
};

/**
 * Listen for quota exceeded events and handle gracefully
 */
window.addEventListener('ops_storage_quota_exceeded', (event) => {
    console.warn('🔄 OPS Matrix: Handling storage quota issue...', event.detail);
    
    // Optional: Show notification to user (requires Odoo notification service)
    if (event.detail.action === 'reload') {
        setTimeout(() => {
            console.log('🔄 Reloading page to apply changes...');
            window.location.reload();
        }, 2000);
    }
});

/**
 * Monitor localStorage usage
 */
function checkStorageUsage() {
    if (typeof localStorage === 'undefined') return;
    
    let totalSize = 0;
    for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
            totalSize += localStorage[key].length + key.length;
        }
    }
    
    // Convert to KB
    const sizeKB = (totalSize / 1024).toFixed(2);
    
    // Warn if approaching 5MB (browser limit is usually 5-10MB)
    if (totalSize > 4 * 1024 * 1024) {
        console.warn(`⚠️ OPS Matrix: LocalStorage usage high: ${sizeKB} KB`);
    } else {
        console.debug(`✓ OPS Matrix: LocalStorage usage: ${sizeKB} KB`);
    }
}

// Check storage on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkStorageUsage);
} else {
    checkStorageUsage();
}

console.log('✓ OPS Matrix Storage Guard initialized');
