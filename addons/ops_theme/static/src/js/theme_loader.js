/** @odoo-module **/

/**
 * OPS Theme Loader
 *
 * Applies color mode immediately on page load to prevent flash of wrong theme.
 * Runs before any other scripts.
 */

(function() {
    'use strict';

    // Get saved color mode from localStorage
    const savedMode = localStorage.getItem('ops_color_mode') || 'system';

    // Apply to document
    document.documentElement.setAttribute('data-color-mode', savedMode);

    // Also apply chatter position class if saved
    const chatterPosition = localStorage.getItem('ops_chatter_position') || 'below';
    if (chatterPosition === 'right') {
        document.documentElement.classList.add('ops-chatter-right-enabled');
    }
})();
