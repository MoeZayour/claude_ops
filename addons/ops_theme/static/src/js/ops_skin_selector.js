/** @odoo-module **/
/**
 * OPS Skin Selector -- Visual palette card widget for skin preset selection.
 * Registered as "ops_skin_selector" for many2one fields pointing to ops.theme.skin.
 */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";

class OpsSkinSelector extends Component {
    static template = "ops_theme.SkinSelector";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            skins: [],
            previewSkinId: null,
        });
        this.originalColors = null;

        onWillStart(async () => {
            await this.loadSkins();
            // Store original CSS variable values for preview restoration
            this.storeOriginalColors();
        });
    }

    /**
     * Store current CSS custom property values from :root
     * for restoration after preview hover ends
     */
    storeOriginalColors() {
        const root = document.documentElement;
        const style = getComputedStyle(root);
        this.originalColors = {
            brand: style.getPropertyValue('--ops-brand').trim(),
            action: style.getPropertyValue('--ops-action').trim(),
            success: style.getPropertyValue('--ops-success').trim(),
            warning: style.getPropertyValue('--ops-warning').trim(),
            danger: style.getPropertyValue('--ops-danger').trim(),
            info: style.getPropertyValue('--ops-info').trim(),
            bg: style.getPropertyValue('--ops-bg').trim(),
            surface: style.getPropertyValue('--ops-surface').trim(),
            text: style.getPropertyValue('--ops-text').trim(),
            border: style.getPropertyValue('--ops-border').trim(),
        };
    }

    async loadSkins() {
        const skins = await this.orm.searchRead(
            "ops.theme.skin",
            [["active", "=", true]],
            [
                "id", "name", "tag",
                "brand_color", "action_color", "success_color",
                "warning_color", "danger_color", "info_color",
                "bg_color", "surface_color", "text_color",
                "border_color", "navbar_style",
            ],
            { order: "sequence, id" },
        );
        this.state.skins = skins;
    }

    /**
     * PHASE 9: Live Hover Preview
     * Apply skin colors to :root CSS variables on hover
     */
    onSkinHoverStart(skin) {
        if (this.props.readonly) return;

        this.state.previewSkinId = skin.id;
        const root = document.documentElement;

        // Temporarily inject this skin's colors into :root
        root.style.setProperty('--ops-brand', skin.brand_color);
        root.style.setProperty('--ops-action', skin.action_color);
        root.style.setProperty('--ops-success', skin.success_color);
        root.style.setProperty('--ops-warning', skin.warning_color);
        root.style.setProperty('--ops-danger', skin.danger_color);
        root.style.setProperty('--ops-info', skin.info_color);
        root.style.setProperty('--ops-bg', skin.bg_color);
        root.style.setProperty('--ops-surface', skin.surface_color);
        root.style.setProperty('--ops-text', skin.text_color);
        root.style.setProperty('--ops-border', skin.border_color);
    }

    /**
     * Restore original colors when hover ends
     */
    onSkinHoverEnd() {
        if (this.props.readonly || !this.originalColors) return;

        this.state.previewSkinId = null;
        const root = document.documentElement;

        // Restore original color values
        root.style.setProperty('--ops-brand', this.originalColors.brand);
        root.style.setProperty('--ops-action', this.originalColors.action);
        root.style.setProperty('--ops-success', this.originalColors.success);
        root.style.setProperty('--ops-warning', this.originalColors.warning);
        root.style.setProperty('--ops-danger', this.originalColors.danger);
        root.style.setProperty('--ops-info', this.originalColors.info);
        root.style.setProperty('--ops-bg', this.originalColors.bg);
        root.style.setProperty('--ops-surface', this.originalColors.surface);
        root.style.setProperty('--ops-text', this.originalColors.text);
        root.style.setProperty('--ops-border', this.originalColors.border);
    }

    get currentValue() {
        const val = this.props.record.data[this.props.name];
        if (!val) return false;
        if (Array.isArray(val)) return val[0];
        if (typeof val === "object" && val.id) return val.id;
        return val;
    }

    isSelected(id) {
        return this.currentValue == id;
    }

    async selectSkin(id) {
        if (this.props.readonly) return;

        // Odoo 19 OWL: Many2one record.update() requires {id, display_name} object
        const skin = this.state.skins.find(s => s.id === id);
        await this.props.record.update({
            [this.props.name]: skin ? { id: skin.id, display_name: skin.name } : false,
        });
    }

    getTagColor(tag) {
        const map = {
            "Anti-Blue": "#8B6914",
            "Focus": "#4338CA",
            "Stress Relief": "#166534",
            "Minimal": "#0284C7",
            "Sleek": "#4F46E5",
            "Energetic": "#059669",
            "Inviting": "#DC2626",
            "Creative": "#7C3AED",
            "Pro": "#525252",
            "Clinical": "#0D9488",
            "Wealth": "#92400E",
            "Efficiency": "#EA580C",
            "Growth": "#7C3AED",
            "Corporate": "#1E40AF",
            "Seamless": "#020617",
        };
        return map[tag] || "#64748B";
    }

    getTagTextColor(tag) {
        return "#FFFFFF";
    }
}

registry.category("fields").add("ops_skin_selector", {
    component: OpsSkinSelector,
    supportedTypes: ["many2one"],
});
