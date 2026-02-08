/** @odoo-module **/

/**
 * OPS Theme Loader
 *
 * Handles initial theme setup on page load:
 * - Syncs the color_scheme cookie when server served dark from DB preference
 *   (so subsequent requests get the correct CSS bundle)
 * - Favicon and title debranding
 *
 * IMPORTANT: Does NOT override data-bs-theme from server rendering.
 * The server's color_scheme() already selected the correct CSS bundle.
 * Overriding the attribute client-side would cause a mismatch between
 * the loaded CSS bundle and the active theme attribute.
 */

document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;

    // Read the server-rendered theme (this is the source of truth)
    const serverScheme = html.getAttribute('data-bs-theme') || 'light';

    // If server rendered dark (from DB preference) but no cookie exists yet,
    // set the cookie so subsequent requests also get the dark CSS bundle.
    const cookieMatch = document.cookie.match(/(?:^|;\s*)color_scheme=(\w+)/);
    const cookieValue = cookieMatch ? cookieMatch[1] : null;

    if (!cookieValue && serverScheme === 'dark') {
        document.cookie = 'color_scheme=dark;path=/;SameSite=Lax;max-age=31536000';
    }

    // Replace favicon with OPS favicon (dynamic route serves company favicon)
    const favicon = document.querySelector('link[rel="icon"]') ||
                    document.querySelector('link[rel="shortcut icon"]');
    if (favicon) {
        favicon.href = '/ops_theme/favicon';
    }

    // Update page title (remove "Odoo" branding)
    if (document.title.includes('Odoo')) {
        document.title = document.title.replace(/Odoo\s*[-–]\s*/gi, '');
    }
});
