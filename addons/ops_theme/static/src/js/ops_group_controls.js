/** @odoo-module **/
/**
 * OPS Framework — Group Expand/Collapse Controls
 * ================================================
 * Adds "Expand All Groups" and "Collapse All Groups" items to the cog menu
 * when a list or kanban view is actively grouped.
 *
 * Architecture:
 *   - Registered in cogMenu registry (same pattern as web.ExportAll)
 *   - isDisplayed: only shown when view is list/kanban AND has active groupBy
 *   - Operates on env.model.root (DynamicGroupList) via group.toggle()
 *   - Handles nested groups recursively
 */

import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

import { Component, useState } from "@odoo/owl";

const cogMenuRegistry = registry.category("cogMenu");

export class OpsGroupControls extends Component {
    static template = "ops_theme.OpsGroupControls";
    static components = { DropdownItem };
    static props = {};

    setup() {
        this.state = useState({ busy: false });
    }

    // -------------------------------------------------------------------------
    // Actions
    // -------------------------------------------------------------------------

    /**
     * Expand all groups. Works top-down: expand top-level first, then nested.
     * Each toggle() on a folded group loads its data, so we must await sequentially
     * for nested groups to become available.
     */
    async onExpandAll() {
        if (this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            const root = this.env.model.root;
            if (!root || !root.isGrouped || !root.groups) {
                return;
            }
            await this._expandGroupsRecursive(root.groups);
        } finally {
            this.state.busy = false;
        }
    }

    /**
     * Recursively expand an array of groups. For each folded group, toggle it
     * (which loads data), then if its children are also grouped, expand those too.
     *
     * @param {Object[]} groups
     */
    async _expandGroupsRecursive(groups) {
        for (const group of groups) {
            if (group.isFolded) {
                await group.toggle();
            }
            // After expanding, check if the group has nested sub-groups
            if (group.list && group.list.isGrouped && group.list.groups) {
                await this._expandGroupsRecursive(group.list.groups);
            }
        }
    }

    /**
     * Collapse all groups. Works bottom-up: collapse nested groups first,
     * then top-level groups. This avoids visual jumps.
     */
    async onCollapseAll() {
        if (this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            const root = this.env.model.root;
            if (!root || !root.isGrouped || !root.groups) {
                return;
            }
            await this._collapseGroupsRecursive(root.groups);
        } finally {
            this.state.busy = false;
        }
    }

    /**
     * Recursively collapse groups bottom-up. First collapse children,
     * then collapse the group itself.
     *
     * @param {Object[]} groups
     */
    async _collapseGroupsRecursive(groups) {
        for (const group of groups) {
            // First collapse nested sub-groups if they exist
            if (!group.isFolded && group.list && group.list.isGrouped && group.list.groups) {
                await this._collapseGroupsRecursive(group.list.groups);
            }
            if (!group.isFolded) {
                await group.toggle();
            }
        }
    }
}

// -------------------------------------------------------------------------
// Registry
// -------------------------------------------------------------------------

export const opsGroupControlsItem = {
    Component: OpsGroupControls,
    groupNumber: 20,
    isDisplayed: (env) => {
        // Company-level toggle
        if (session.ops_group_controls_enabled === false) {
            return false;
        }
        // Only show in list and kanban views that have active grouping
        const viewType = env.config && env.config.viewType;
        if (!["list", "kanban"].includes(viewType)) {
            return false;
        }
        // Check if there's an active groupBy on the search model
        const groupBy = env.searchModel && env.searchModel.groupBy;
        if (!groupBy || !groupBy.length) {
            return false;
        }
        // Don't show when records are selected (same pattern as ExportAll)
        if (env.model && env.model.root && env.model.root.selection && env.model.root.selection.length) {
            return false;
        }
        return true;
    },
};

cogMenuRegistry.add("ops-group-controls", opsGroupControlsItem, { sequence: 50 });
