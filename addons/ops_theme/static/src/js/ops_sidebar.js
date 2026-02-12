/** @odoo-module **/
/**
 * OPS Theme - Sidebar Navigation Component
 * ==========================================
 * Collapsible sidebar showing app icons with labels.
 *
 * Three modes:
 *   - large:     200px with icons + labels
 *   - small:     60px icons only
 *   - invisible: hidden (0px)
 *
 * User pref saved to res.users via controller + localStorage for instant restore.
 * Company toggle (ops_sidebar_enabled) can disable the entire feature.
 *
 * Architecture:
 *   - Reads current state from session (ops_sidebar_type, ops_sidebar_enabled)
 *   - menuService.getApps() provides the app list
 *   - menuService.getCurrentApp() highlights the active app
 *   - CSS custom property --ops-sidebar-width shifts the main content
 */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { useBus, useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

const SIDEBAR_LS_KEY = "ops_sidebar_type";
const MOBILE_BREAKPOINT = 768;

export class OpsSidebar extends Component {
    static template = "ops_theme.OpsSidebar";
    static props = {};

    setup() {
        this.menuService = useService("menu");
        this.actionService = useService("action");

        // Resolve sidebar type: session pref > localStorage > default 'large'
        const sessionType = session.ops_sidebar_type;
        const storedType = localStorage.getItem(SIDEBAR_LS_KEY);
        const initialType = sessionType || storedType || "large";

        // Company-level toggle
        const sidebarEnabled = session.ops_sidebar_enabled !== false;

        this.state = useState({
            sidebarType: sidebarEnabled ? initialType : "invisible",
            enabled: sidebarEnabled,
            mobileOpen: false,
            isMobile: window.innerWidth < MOBILE_BREAKPOINT,
            // Counter to force re-render on app change (OWL needs tracked state change)
            appChangeCounter: 0,
        });

        // Listen for app changes to re-render active state
        useBus(this.env.bus, "MENUS:APP-CHANGED", () => {
            this.state.appChangeCounter++;
            if (this.state.mobileOpen) {
                this.state.mobileOpen = false;
            }
        });

        this._onResize = this._onResize.bind(this);
        this._onKeyDown = this._onKeyDown.bind(this);

        onMounted(() => {
            window.addEventListener("resize", this._onResize);
            window.addEventListener("keydown", this._onKeyDown);
            this._applySidebarWidth();
        });

        onWillUnmount(() => {
            window.removeEventListener("resize", this._onResize);
            window.removeEventListener("keydown", this._onKeyDown);
            // Clean up CSS custom property and class
            document.documentElement.style.removeProperty("--ops-sidebar-width");
            document.documentElement.classList.remove("ops-sidebar-active");
        });
    }

    // =========================================================================
    // GETTERS
    // =========================================================================

    get apps() {
        // Access appChangeCounter to ensure reactivity on app changes
        void this.state.appChangeCounter;
        return this.menuService.getApps() || [];
    }

    get currentApp() {
        void this.state.appChangeCounter;
        return this.menuService.getCurrentApp();
    }

    get sidebarClass() {
        const classes = ["ops-sidebar"];
        classes.push(`ops-sidebar-${this.state.sidebarType}`);
        if (this.state.mobileOpen) {
            classes.push("ops-sidebar-mobile-open");
        }
        return classes.join(" ");
    }

    get isVisible() {
        return this.state.enabled && this.state.sidebarType !== "invisible";
    }

    get showLabels() {
        return this.state.sidebarType === "large";
    }

    get companyName() {
        const company = user.activeCompany;
        return company ? company.name : "";
    }

    /**
     * Return the effective width in pixels for CSS variable.
     */
    get sidebarWidthPx() {
        if (!this.state.enabled || this.state.isMobile) {
            return 0;
        }
        switch (this.state.sidebarType) {
            case "large":
                return 200;
            case "small":
                return 60;
            default:
                return 0;
        }
    }

    // =========================================================================
    // ACTIONS
    // =========================================================================

    /**
     * Cycle through sidebar modes: large -> small -> invisible -> large
     */
    toggleSidebar() {
        const cycle = { large: "small", small: "invisible", invisible: "large" };
        const newType = cycle[this.state.sidebarType] || "large";
        this._setSidebarType(newType);
    }

    /**
     * Navigate to the OPS Home Menu grid.
     */
    onHomeClick() {
        this.actionService.doAction("ops_home_menu");
        if (this.state.mobileOpen) {
            this.state.mobileOpen = false;
        }
    }

    /**
     * Handle clicking an app in the sidebar.
     */
    onAppClick(app) {
        this.menuService.selectMenu(app);
        // Close mobile overlay
        if (this.state.mobileOpen) {
            this.state.mobileOpen = false;
        }
    }

    /**
     * Open mobile overlay sidebar.
     */
    openMobile() {
        this.state.mobileOpen = true;
    }

    /**
     * Close mobile overlay sidebar.
     */
    closeMobile() {
        this.state.mobileOpen = false;
    }

    /**
     * Check if an app is the currently active one.
     */
    isActiveApp(app) {
        const current = this.currentApp;
        return current && current.id === app.id;
    }

    /**
     * Get the icon source for an app. Uses webIconData if available,
     * otherwise returns null and template uses fallback fa icon.
     */
    getAppIcon(app) {
        return app.webIconData || null;
    }

    // =========================================================================
    // INTERNAL
    // =========================================================================

    _setSidebarType(newType) {
        this.state.sidebarType = newType;
        localStorage.setItem(SIDEBAR_LS_KEY, newType);
        this._applySidebarWidth();
        this._persistPreference(newType);
    }

    _applySidebarWidth() {
        document.documentElement.style.setProperty(
            "--ops-sidebar-width",
            `${this.sidebarWidthPx}px`
        );
        // Toggle class so CSS can hide the native home menu grid button
        document.documentElement.classList.toggle(
            "ops-sidebar-active",
            this.state.enabled && this.state.sidebarType !== "invisible"
        );
    }

    /**
     * Persist preference to server (fire and forget).
     */
    async _persistPreference(type) {
        try {
            await rpc("/ops_theme/set_sidebar_type", { type });
        } catch (err) {
            console.warn("[OPS Sidebar] Failed to persist sidebar type:", err);
        }
    }

    _onResize() {
        const wasMobile = this.state.isMobile;
        this.state.isMobile = window.innerWidth < MOBILE_BREAKPOINT;

        // Close mobile overlay when resizing to desktop
        if (wasMobile && !this.state.isMobile) {
            this.state.mobileOpen = false;
        }

        this._applySidebarWidth();
    }

    _onKeyDown(ev) {
        // Escape closes mobile overlay
        if (ev.key === "Escape" && this.state.mobileOpen) {
            this.state.mobileOpen = false;
        }
    }
}
