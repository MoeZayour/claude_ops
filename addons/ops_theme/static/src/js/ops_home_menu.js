/** @odoo-module **/
/**
 * OPS Home Menu — Enhanced App Grid for Odoo 19 CE
 * =================================================
 * Odoo 19 CE has no HomeMenu component (that is Enterprise-only).
 * This module provides a full-featured app launcher registered as a client action.
 *
 * Features:
 *  - Three view modes: grid (default), list, tiles — persisted to localStorage
 *  - Real-time search/filter by app name
 *  - Smooth hover animations
 *  - Responsive layout for all screen sizes
 *
 * Integration:
 *  - Registered as client action "ops_home_menu" in the actions registry
 *  - WebClient._loadDefaultApp is patched to show this instead of auto-selecting first app
 *  - Navbar "Home" button (oi-apps) triggers navigation back here
 */

import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { session } from "@web/session";

const STORAGE_KEY = "ops_home_view_mode";
const VALID_MODES = ["grid", "list", "tiles"];

export class OpsHomeMenu extends Component {
    static template = "ops_theme.HomeMenu";
    static props = { "*": true };

    setup() {
        this.menuService = useService("menu");

        const savedMode = localStorage.getItem(STORAGE_KEY);
        const initialMode = VALID_MODES.includes(savedMode) ? savedMode : "grid";

        this.state = useState({
            viewMode: initialMode,
            searchTerm: "",
        });

        onMounted(() => {
            const input = document.querySelector(".ops-home-search__input");
            if (input) {
                input.focus();
            }
        });
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    get apps() {
        const apps = this.menuService.getApps() || [];
        if (!this.state.searchTerm) {
            return apps;
        }
        const term = this.state.searchTerm.toLowerCase().trim();
        return apps.filter((app) => (app.name || "").toLowerCase().includes(term));
    }

    get viewMode() {
        return this.state.viewMode;
    }

    get containerClass() {
        switch (this.state.viewMode) {
            case "list":
                return "ops-apps-list";
            case "tiles":
                return "ops-apps-tiles";
            default:
                return "ops-apps-grid";
        }
    }

    // -------------------------------------------------------------------------
    // Actions
    // -------------------------------------------------------------------------

    onSearchInput(ev) {
        this.state.searchTerm = ev.target.value;
    }

    onSearchClear() {
        this.state.searchTerm = "";
        const input = document.querySelector(".ops-home-search__input");
        if (input) {
            input.focus();
        }
    }

    setViewMode(mode) {
        if (VALID_MODES.includes(mode)) {
            this.state.viewMode = mode;
            localStorage.setItem(STORAGE_KEY, mode);
        }
    }

    selectApp(app) {
        this.menuService.selectMenu(app);
    }

    /**
     * Returns a suitable icon source for an app.
     * Odoo apps have webIconData (base64) or webIcon (path string).
     */
    getAppIcon(app) {
        if (app.webIconData) {
            return app.webIconData;
        }
        if (app.webIcon) {
            // webIcon can be "module,path" format or a direct path
            const parts = app.webIcon.split(",");
            if (parts.length === 2) {
                return `/${parts[0].trim()}/static/${parts[1].trim()}`;
            }
            return app.webIcon;
        }
        return null;
    }

    /**
     * Generates a deterministic hue for the fallback icon background
     * based on the app name, giving each app a unique color.
     */
    getFallbackColor(app) {
        const name = app.name || "";
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = Math.abs(hash) % 360;
        return `hsl(${hue}, 55%, 50%)`;
    }

    /**
     * Returns the first letter of the app name for the fallback icon.
     */
    getFallbackLetter(app) {
        return (app.name || "?").charAt(0).toUpperCase();
    }

    onKeydown(ev) {
        if (ev.key === "Escape" && this.state.searchTerm) {
            this.onSearchClear();
            ev.preventDefault();
        }
    }
}

// Register as a client action so it can be invoked via doAction
registry.category("actions").add("ops_home_menu", OpsHomeMenu);

// =============================================================================
// PATCH: WebClient._loadDefaultApp
// =============================================================================
// In vanilla Odoo 19 CE, _loadDefaultApp immediately navigates to the first
// app menu. We replace that behavior with showing the OPS Home Menu, giving
// users a visual dashboard of all available apps.

patch(WebClient.prototype, {
    _loadDefaultApp() {
        if (session.ops_home_menu_enhanced === false) {
            return super._loadDefaultApp();
        }
        return this.actionService.doAction("ops_home_menu");
    },
});

// NavBar patch removed — Home button now lives in OpsSidebar component.
