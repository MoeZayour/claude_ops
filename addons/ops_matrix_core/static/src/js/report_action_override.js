/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Task 3: Global PDF "New Tab" Behavior
 * Override the IR Actions Report Handler to force PDFs to open in new tab
 *
 * Odoo 19 Compatibility: Safely check for existing handler before overriding
 */

const reportHandlerRegistry = registry.category("ir.actions.report handlers");

// Safely get the original handler if it exists
let originalHandler = null;
try {
    originalHandler = reportHandlerRegistry.get("handler");
} catch (e) {
    // Handler may not be registered yet - that's okay
    console.debug("Original report handler not found in registry yet");
}

reportHandlerRegistry.add("handler", async function (action, options, env) {
    // Check if this is a PDF report
    if (action.report_type === 'qweb-pdf') {
        // Build the report URL
        const type = action.report_type === 'qweb-pdf' ? 'pdf' : 'text';
        let url = `/report/${type}/${action.report_name}`;
        const actionContext = action.context || {};
        
        if (action.data && JSON.stringify(action.data) !== '{}') {
            const options_param = encodeURIComponent(JSON.stringify(action.data));
            const context_param = encodeURIComponent(JSON.stringify(actionContext));
            url += `?options=${options_param}&context=${context_param}`;
        } else {
            if (actionContext.active_ids) {
                url += `/${actionContext.active_ids.join(',')}`;
            }
            if (action.report_file) {
                url += `?report_file=${encodeURIComponent(action.report_file)}`;
            }
        }
        
        // Force open in new tab
        window.open(url, '_blank');
        return true;
    }
    
    // For non-PDF reports, use original handler if it exists
    if (originalHandler) {
        return originalHandler(action, options, env);
    }
    
    // Fallback: return true to prevent default behavior
    return true;
}, { force: true });
