/** @odoo-module **/

/**
 * OPS Color Mode - Early Initialization
 *
 * This script applies the stored color mode preference immediately
 * to prevent flash of wrong colors. No OWL component registration.
 */

(function() {
    'use strict';

    const storedMode = localStorage.getItem('ops_color_mode') || 'light';
    let effectiveMode = storedMode;

    if (storedMode === 'system') {
        effectiveMode = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    document.documentElement.setAttribute('data-color-mode', effectiveMode);

    // Listen for system preference changes
    if (storedMode === 'system') {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (localStorage.getItem('ops_color_mode') === 'system') {
                document.documentElement.setAttribute('data-color-mode', e.matches ? 'dark' : 'light');
            }
        });
    }
})();

/**
 * Global function to set color mode
 * Can be called from anywhere: setOpsColorMode('dark')
 */
window.setOpsColorMode = function(mode) {
    let effectiveMode = mode;

    if (mode === 'system') {
        effectiveMode = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    document.documentElement.setAttribute('data-color-mode', effectiveMode);
    localStorage.setItem('ops_color_mode', mode);
};
