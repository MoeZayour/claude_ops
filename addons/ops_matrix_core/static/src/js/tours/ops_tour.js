/** @odoo-module **/
/**
 * EMERGENCY FIX: OPS Matrix Core Tour - COMPLETELY DISABLED
 *
 * This tour has been removed to prevent race conditions and localStorage issues
 * during system installation and crash loops.
 *
 * The tour was causing:
 * - Attempts to click .o_list_button_add while page is crashing
 * - Race conditions during asset loading
 * - Infinite loops when localStorage quota is exceeded
 *
 * DO NOT RE-ENABLE without fixing the core issues first.
 */

// Tour registration completely removed - no registry imports, no tour definition
console.log('[OPS Matrix] Tour system disabled for stability');
