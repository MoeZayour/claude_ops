/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * OPS Color Mode Toggle Component
 *
 * Allows users to switch between Light, Dark, and System color modes.
 */
export class OpsColorModeToggle extends Component {
    static template = "ops_theme.ColorModeToggle";

    setup() {
        this.user = useService("user");
        this.orm = useService("orm");

        this.state = useState({
            mode: localStorage.getItem('ops_color_mode') || 'system',
        });

        onMounted(() => {
            this.loadUserPreference();
        });
    }

    async loadUserPreference() {
        try {
            const result = await this.orm.read('res.users', [this.user.userId], ['ops_color_mode']);
            if (result.length && result[0].ops_color_mode) {
                this.state.mode = result[0].ops_color_mode;
                this.applyMode(this.state.mode);
            }
        } catch (error) {
            console.warn('Could not load color mode preference:', error);
        }
    }

    applyMode(mode) {
        document.documentElement.setAttribute('data-color-mode', mode);
        localStorage.setItem('ops_color_mode', mode);
    }

    async setMode(mode) {
        this.state.mode = mode;
        this.applyMode(mode);

        try {
            await this.orm.write('res.users', [this.user.userId], {
                ops_color_mode: mode,
            });
        } catch (error) {
            console.warn('Could not save color mode preference:', error);
        }
    }

    get isLight() {
        return this.state.mode === 'light';
    }

    get isDark() {
        return this.state.mode === 'dark';
    }

    get isSystem() {
        return this.state.mode === 'system';
    }
}

OpsColorModeToggle.template = "ops_theme.ColorModeToggle";
