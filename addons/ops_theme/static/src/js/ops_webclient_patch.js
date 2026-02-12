/** @odoo-module **/
/**
 * OPS Theme - WebClient Patch for Sidebar Integration
 * =====================================================
 * Registers OpsSidebar as a sub-component of WebClient so that the
 * template extension (ops_webclient.xml) can render <OpsSidebar/>.
 *
 * Strategy:
 *   - Directly add OpsSidebar to WebClient.components (static property)
 *   - Template inheritance (via XML) adds <OpsSidebar/> before ActionContainer
 *   - No setup() override needed — sidebar manages its own lifecycle
 */

import { WebClient } from "@web/webclient/webclient";
import { OpsSidebar } from "./ops_sidebar";

// Register OpsSidebar as a sub-component of WebClient.
// Direct assignment is the safest way to extend the static components dict
// without overriding other patches that may have already added entries.
WebClient.components = {
    ...WebClient.components,
    OpsSidebar,
};
