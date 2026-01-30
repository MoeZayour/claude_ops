/** @odoo-module **/

/**
 * OPS Theme v2.0 - Page Loader Module
 *
 * Manages the page loading spinner and provides smooth
 * transitions between views.
 */

import { registry } from "@web/core/registry";

// =============================================================================
// PAGE LOADER CONTROLLER
// =============================================================================

class OPSPageLoader {
    constructor() {
        this.loaderElement = null;
        this.isShowing = false;
        this.minShowTime = 200; // Minimum time to show loader (prevents flash)
        this.showStartTime = 0;
    }

    /**
     * Create and inject the loader element into the DOM
     */
    createLoader() {
        if (this.loaderElement) return;

        this.loaderElement = document.createElement('div');
        this.loaderElement.id = 'ops-loader';
        this.loaderElement.className = 'ops-loader-hidden';
        this.loaderElement.innerHTML = `
            <div class="ops-spinner"></div>
            <div class="ops-loader-text">Loading...</div>
        `;

        document.body.appendChild(this.loaderElement);
    }

    /**
     * Show the loader
     * @param {string} text - Optional loading text
     */
    show(text = 'Loading...') {
        if (!this.loaderElement) {
            this.createLoader();
        }

        const textElement = this.loaderElement.querySelector('.ops-loader-text');
        if (textElement) {
            textElement.textContent = text;
        }

        this.loaderElement.classList.remove('ops-loader-hidden');
        this.isShowing = true;
        this.showStartTime = Date.now();
    }

    /**
     * Hide the loader (respects minimum show time)
     */
    hide() {
        if (!this.loaderElement || !this.isShowing) return;

        const elapsed = Date.now() - this.showStartTime;
        const remaining = Math.max(0, this.minShowTime - elapsed);

        setTimeout(() => {
            if (this.loaderElement) {
                this.loaderElement.classList.add('ops-loader-hidden');
            }
            this.isShowing = false;
        }, remaining);
    }

    /**
     * Force immediate hide (no minimum time)
     */
    forceHide() {
        if (this.loaderElement) {
            this.loaderElement.classList.add('ops-loader-hidden');
        }
        this.isShowing = false;
    }
}

// Create global loader instance
const pageLoader = new OPSPageLoader();

// Expose to window for manual control
window.OPSTheme = window.OPSTheme || {};
window.OPSTheme.loader = pageLoader;

// =============================================================================
// ODOO RPC LOADING INTEGRATION
// =============================================================================

// Track active RPC calls
let activeRPCs = 0;
let rpcTimeout = null;

/**
 * Hook into Odoo's RPC system to show loader on long operations
 */
function setupRPCHooks() {
    // Create a subtle top loading bar
    const loadingBar = document.createElement('div');
    loadingBar.id = 'ops-loading-bar';
    loadingBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, var(--ops-secondary, #3b82f6), var(--ops-info, #06b6d4));
        z-index: 10000;
        transition: width 0.3s ease;
        opacity: 0;
    `;
    document.body.appendChild(loadingBar);

    // Show/hide functions
    window.OPSTheme.showLoadingBar = function() {
        loadingBar.style.opacity = '1';
        loadingBar.style.width = '30%';

        // Animate to 70%
        setTimeout(() => {
            if (loadingBar.style.opacity === '1') {
                loadingBar.style.width = '70%';
            }
        }, 500);
    };

    window.OPSTheme.hideLoadingBar = function() {
        loadingBar.style.width = '100%';
        setTimeout(() => {
            loadingBar.style.opacity = '0';
            loadingBar.style.width = '0%';
        }, 200);
    };
}

// Initialize RPC hooks when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupRPCHooks);
} else {
    setupRPCHooks();
}

// =============================================================================
// VIEW TRANSITION ANIMATIONS
// =============================================================================

// Add smooth transitions when switching between views
const viewTransitionStyles = document.createElement('style');
viewTransitionStyles.textContent = `
    /* View container transitions */
    .o_action_manager > .o_action {
        animation: ops-view-enter 0.2s ease;
    }

    @keyframes ops-view-enter {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    /* Form view specific */
    .o_form_view.o_form_editable {
        animation: ops-form-edit 0.15s ease;
    }

    @keyframes ops-form-edit {
        from {
            opacity: 0.9;
        }
        to {
            opacity: 1;
        }
    }

    /* Smooth breadcrumb transitions */
    .o_breadcrumb {
        animation: ops-breadcrumb-in 0.2s ease;
    }

    @keyframes ops-breadcrumb-in {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(viewTransitionStyles);

// =============================================================================
// INITIAL PAGE LOAD HANDLING
// =============================================================================

// Show loader on initial page load (for slow connections)
let initialLoadTimeout = null;

function handleInitialLoad() {
    // If page takes more than 500ms to become interactive, show loader
    initialLoadTimeout = setTimeout(() => {
        if (document.readyState !== 'complete') {
            pageLoader.show('Loading application...');
        }
    }, 500);
}

// Hide loader when page is fully loaded
function handleLoadComplete() {
    if (initialLoadTimeout) {
        clearTimeout(initialLoadTimeout);
    }
    pageLoader.hide();
}

// Set up initial load handlers
if (document.readyState === 'loading') {
    handleInitialLoad();
    window.addEventListener('load', handleLoadComplete);
} else {
    // Already loaded
    handleLoadComplete();
}

// =============================================================================
// EXPORT
// =============================================================================

export const OPSPageLoader = pageLoader;

console.log('[OPS Theme] Page loader module initialized');
