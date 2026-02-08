/** @odoo-module **/
/**
 * OPS Theme Selector — Visual palette card widget for theme preset selection.
 *
 * Replaces the plain radio widget with clickable swatch cards showing
 * name, tag, and 7 color circles per palette.
 *
 * Registered as field widget "ops_theme_selector" for Selection fields.
 */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// ─── Palette definitions (mirrors Python THEME_PRESETS) ───
const PALETTES = [
    {
        key: "corporate_blue", name: "Corporate Blue", tag: "Professional",
        bg: "#f1f5f9", surface: "#ffffff", border: "#e2e8f0", text: "#1e293b",
        accent: "#3b82f6", accent2: "#60a5fa", btn: "#3b82f6", dark: false,
    },
    {
        key: "modern_dark", name: "Modern Dark", tag: "Sleek",
        bg: "#0f172a", surface: "#1e293b", border: "#334155", text: "#f1f5f9",
        accent: "#6366f1", accent2: "#818cf8", btn: "#6366f1", dark: true,
    },
    {
        key: "clean_light", name: "Clean Light", tag: "Minimal",
        bg: "#ffffff", surface: "#f8fafc", border: "#e2e8f0", text: "#0f172a",
        accent: "#0ea5e9", accent2: "#38bdf8", btn: "#0ea5e9", dark: false,
    },
    {
        key: "enterprise_navy", name: "Enterprise Navy", tag: "Corporate",
        bg: "#f8fafc", surface: "#ffffff", border: "#e2e8f0", text: "#0f172a",
        accent: "#2563eb", accent2: "#3b82f6", btn: "#2563eb", dark: false,
    },
    {
        key: "warm_professional", name: "Warm Professional", tag: "Classic",
        bg: "#fafaf9", surface: "#ffffff", border: "#e7e5e4", text: "#292524",
        accent: "#d97706", accent2: "#ea580c", btn: "#d97706", dark: false,
    },
    {
        key: "mono_minimal", name: "Monochromatic Minimalism", tag: "Professional",
        bg: "#121212", surface: "#1E1E1E", border: "#444444", text: "#E0E0E0",
        accent: "#888888", accent2: "#AAAAAA", btn: "#888888", dark: true,
    },
    {
        key: "neon_highlights", name: "Neon Highlights", tag: "Energetic",
        bg: "#0D0D0D", surface: "#1A1A1A", border: "#333333", text: "#FFFFFF",
        accent: "#00FF85", accent2: "#1E90FF", btn: "#00FF85", dark: true,
    },
    {
        key: "warm_tones", name: "Warm Tones", tag: "Inviting",
        bg: "#1C1C1C", surface: "#2A2420", border: "#4A4038", text: "#F5E8D8",
        accent: "#FF6F61", accent2: "#DAA520", btn: "#FF6F61", dark: true,
    },
    {
        key: "muted_pastels", name: "Muted Pastels", tag: "Creative",
        bg: "#2C2C2C", surface: "#363636", border: "#505050", text: "#E4E4E4",
        accent: "#A8DADC", accent2: "#FFC1CC", btn: "#B39CD0", dark: true,
    },
    {
        key: "deep_jewel", name: "Deep Jewel Tones", tag: "Luxurious",
        bg: "#1A1A1A", surface: "#242424", border: "#404040", text: "#F0F0F0",
        accent: "#006B7F", accent2: "#822659", btn: "#3E5641", dark: true,
    },
    {
        key: "contrast_vibrant", name: "Contrasting Vibrancy", tag: "Dynamic",
        bg: "#181818", surface: "#222222", border: "#404040", text: "#F7F7F7",
        accent: "#FF5722", accent2: "#673AB7", btn: "#FF5722", dark: true,
    },
];

class OpsThemeSelector extends Component {
    static template = "ops_theme.ThemeSelector";
    static props = { ...standardFieldProps };

    setup() {
        this.palettes = PALETTES;
    }

    get currentValue() {
        return this.props.record.data[this.props.name] || "corporate_blue";
    }

    get lightPalettes() {
        return this.palettes.filter((p) => !p.dark);
    }

    get darkPalettes() {
        return this.palettes.filter((p) => p.dark);
    }

    isSelected(key) {
        return this.currentValue === key;
    }

    async onSelect(key) {
        if (this.props.readonly) return;
        await this.props.record.update({ [this.props.name]: key });
    }
}

registry.category("fields").add("ops_theme_selector", {
    component: OpsThemeSelector,
    supportedTypes: ["selection"],
});
