/** @odoo-module **/

import { Component } from '@odoo/owl';
import { registry } from '@web/core/registry';
import { DropdownItem } from '@web/core/dropdown/dropdown_item';

const cogMenuRegistry = registry.category('cogMenu');

/**
 * OPS Theme - Expand All Groups
 *
 * Adds an "Expand All" option to the cog menu in list and kanban views.
 * This expands all grouped rows recursively.
 */
export class ExpandAllGroups extends Component {
    static template = 'ops_theme.ExpandAllGroups';
    static components = { DropdownItem };
    static props = {};

    async onClick() {
        let groups = this.env.model?.root?.groups;

        if (!groups || !groups.length) {
            return;
        }

        // Expand groups recursively
        while (groups && groups.length) {
            const foldedGroups = groups.filter(g => g._config?.isFolded);

            for (const group of foldedGroups) {
                await group.toggle();
            }

            // Get subgroups
            const subGroups = foldedGroups
                .map(g => g.list?.groups || [])
                .flat();

            groups = subGroups;
        }

        // Reload and notify
        await this.env.model.root.load();
        this.env.model.notify();
    }
}

cogMenuRegistry.add('ops-expand-all', {
    Component: ExpandAllGroups,
    groupNumber: 15,
    isDisplayed: (env) => (
        ['kanban', 'list'].includes(env.config?.viewType) &&
        env.model?.root?.isGrouped
    ),
}, { sequence: 1 });


/**
 * OPS Theme - Collapse All Groups
 *
 * Adds a "Collapse All" option to the cog menu in list and kanban views.
 * This collapses all grouped rows.
 */
export class CollapseAllGroups extends Component {
    static template = 'ops_theme.CollapseAllGroups';
    static components = { DropdownItem };
    static props = {};

    async onClick() {
        const groups = this.env.model?.root?.groups || [];

        // Collapse all expanded groups
        for (const group of groups) {
            if (!group._config?.isFolded) {
                await group.toggle();
            }
        }

        // Notify of changes
        this.env.model.notify();
    }
}

cogMenuRegistry.add('ops-collapse-all', {
    Component: CollapseAllGroups,
    groupNumber: 15,
    isDisplayed: (env) => (
        ['kanban', 'list'].includes(env.config?.viewType) &&
        env.model?.root?.isGrouped
    ),
}, { sequence: 2 });
