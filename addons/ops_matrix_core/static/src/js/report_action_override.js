/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * OPS PDF "New Tab" Behavior
 *
 * Opens qweb-pdf reports in a new browser tab instead of triggering
 * a file download.  The URL follows the standard Odoo 19 pattern:
 *
 *   /report/pdf/<report_name>/<docids>
 *
 * Document IDs come from action.context.active_ids (set by
 * report.report_action() on the server side).
 *
 * For non-PDF reports we return `false` so Odoo's built-in
 * handlers continue to process the action normally.
 */

const reportHandlerRegistry = registry.category("ir.actions.report handlers");

reportHandlerRegistry.add("ops_pdf_new_tab", async function (action, options, env) {
    if (action.report_type !== "qweb-pdf") {
        // Not a PDF – let Odoo's default handler take over
        return false;
    }

    const context = action.context || {};
    const activeIds = context.active_ids || [];

    // Build the standard Odoo report URL
    let url = `/report/pdf/${action.report_name}`;
    if (activeIds.length) {
        url += `/${activeIds.join(",")}`;
    }

    // Open in a new tab for convenient viewing / browser print
    window.open(url, "_blank");
    return true;
});
