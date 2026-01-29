/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * OPS Chatter Position Toggle Component
 *
 * Allows users to switch chatter between below and right positions.
 */
export class OpsChatterToggle extends Component {
    static template = "ops_theme.ChatterToggle";

    setup() {
        this.user = useService("user");
        this.orm = useService("orm");

        this.state = useState({
            position: localStorage.getItem('ops_chatter_position') || 'below',
        });

        onMounted(() => {
            this.loadUserPreference();
            this.applyPosition(this.state.position);
        });
    }

    async loadUserPreference() {
        try {
            const result = await this.orm.read('res.users', [this.user.userId], ['ops_chatter_position']);
            if (result.length && result[0].ops_chatter_position) {
                this.state.position = result[0].ops_chatter_position;
                this.applyPosition(this.state.position);
            }
        } catch (error) {
            console.warn('Could not load chatter position preference:', error);
        }
    }

    applyPosition(position) {
        localStorage.setItem('ops_chatter_position', position);

        // Apply class to all form views
        const formViews = document.querySelectorAll('.o_form_view');
        formViews.forEach(form => {
            if (position === 'right') {
                form.classList.add('ops-chatter-right');
            } else {
                form.classList.remove('ops-chatter-right');
            }
        });

        // Also set on document for future form views
        if (position === 'right') {
            document.documentElement.classList.add('ops-chatter-right-enabled');
        } else {
            document.documentElement.classList.remove('ops-chatter-right-enabled');
        }
    }

    async setPosition(position) {
        this.state.position = position;
        this.applyPosition(position);

        try {
            await this.orm.write('res.users', [this.user.userId], {
                ops_chatter_position: position,
            });
        } catch (error) {
            console.warn('Could not save chatter position preference:', error);
        }
    }

    get isBelow() {
        return this.state.position === 'below';
    }

    get isRight() {
        return this.state.position === 'right';
    }
}

OpsChatterToggle.template = "ops_theme.ChatterToggle";
