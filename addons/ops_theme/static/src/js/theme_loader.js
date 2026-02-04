/** @odoo-module **/

/**
 * OPS Theme Loader
 *
 * Handles initial theme setup. Dark mode is handled natively by Odoo 19.
 * Chatter position is handled by FormCompiler patch via session.
 * This file handles other OPS-specific initializations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize color mode attribute on HTML element
    // This supports Odoo 19's native dark mode system
    const htmlElement = document.documentElement;
    if (!htmlElement.hasAttribute('data-color-mode')) {
        htmlElement.setAttribute('data-color-mode', 'light');
    }

    // Replace favicon with OPS favicon
    const favicon = document.querySelector('link[rel="icon"]') ||
                    document.querySelector('link[rel="shortcut icon"]');
    if (favicon) {
        favicon.href = '/ops_theme/static/src/img/favicon.ico';
    }

    // Update page title (remove "Odoo" branding)
    if (document.title.includes('Odoo')) {
        document.title = document.title.replace(/Odoo\s*[-–]\s*/gi, '');
    }
});
