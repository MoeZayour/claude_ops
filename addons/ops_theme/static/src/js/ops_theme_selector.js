/** @odoo-module **/
/**
 * OPS Theme Selector — Visual palette card widget for theme preset selection.
 * Light-only skins. Fetches from `ops.theme.skin` model.
 */

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";

class OpsThemeSelector extends Component {
    static template = "ops_theme.ThemeSelector";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.palettes = [];

        onWillStart(async () => {
            await this.loadSkins();
        });
    }

    async loadSkins() {
        // Fetch all active skins from the database
        const skins = await this.orm.searchRead("ops.theme.skin", [], [
            "id", "name", "tag",
            "bg_color", "surface_color", "border_color", "text_color",
            "secondary_color"
        ], { order: "sequence, id" });

        this.palettes = skins.map(s => ({
            key: s.id,
            name: s.name,
            tag: s.tag,
            bg: s.bg_color,
            surface: s.surface_color,
            border: s.border_color,
            text: s.text_color,
            accent: s.secondary_color,
        }));
    }

    get currentValue() {
        const val = this.props.record.data[this.props.name];
        if (!val) return false;
        if (Array.isArray(val)) return val[0];
        if (typeof val === 'object' && val.id) return val.id;
        return val;
    }

    isSelected(key) {
        if (key === 'custom') {
            return !this.currentValue;
        }
        return this.currentValue == key;
    }

    async onSelect(key) {
        if (this.props.readonly) return;

        if (key === 'custom') {
            await this.props.record.update({ [this.props.name]: false });
        } else {
            await this.props.record.update({ [this.props.name]: key });
        }
    }
}

registry.category("fields").add("ops_theme_selector", {
    component: OpsThemeSelector,
    supportedTypes: ["many2one"],
});
