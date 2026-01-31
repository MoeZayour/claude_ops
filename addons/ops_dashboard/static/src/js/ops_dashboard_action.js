/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * OPS Dashboard Action Component
 * Displays KPI cards with real-time data, auto-refresh, and proper currency formatting
 */
class OpsDashboardAction extends Component {
    static template = "ops_dashboard.DashboardAction";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            dashboards: [],
            selectedDashboardId: null,
            dashboardData: null,
            period: "this_month",
            loading: true,
            refreshing: false,
            error: null,
            // Currency info - will be loaded from backend
            currencySymbol: "",
            currencyPosition: "before",
            currencyCode: "",
        });

        this.refreshInterval = null;
        this.periods = [
            { value: "today", label: _t("Today") },
            { value: "this_week", label: _t("This Week") },
            { value: "this_month", label: _t("This Month") },
            { value: "this_quarter", label: _t("This Quarter") },
            { value: "this_year", label: _t("This Year") },
            { value: "last_30_days", label: _t("Last 30 Days") },
            { value: "last_90_days", label: _t("Last 90 Days") },
            { value: "all_time", label: _t("All Time") },
        ];

        onWillStart(async () => {
            await this.loadCurrencyInfo();
            await this.loadDashboards();
        });

        onMounted(() => {
            this.setupAutoRefresh();
        });

        onWillUnmount(() => {
            this.clearAutoRefresh();
        });
    }

    /**
     * Load the company's currency information for proper formatting
     * Uses a backend method to get currency info for current user's company
     */
    async loadCurrencyInfo() {
        try {
            // Call backend method to get currency info
            const currencyInfo = await this.orm.call(
                "ops.dashboard",
                "get_company_currency_info",
                []
            );

            if (currencyInfo) {
                this.state.currencySymbol = currencyInfo.symbol || "$";
                this.state.currencyPosition = currencyInfo.position || "before";
                this.state.currencyCode = currencyInfo.code || "USD";
            }
        } catch (error) {
            console.warn("Could not load currency info:", error);
            // Set defaults if unable to load
            this.state.currencySymbol = "$";
            this.state.currencyPosition = "before";
            this.state.currencyCode = "USD";
        }
    }

    async loadDashboards() {
        try {
            this.state.loading = true;
            const dashboards = await this.orm.call(
                "ops.dashboard",
                "get_user_dashboards",
                []
            );
            this.state.dashboards = dashboards;

            if (dashboards.length > 0) {
                this.state.selectedDashboardId = dashboards[0].id;
                await this.loadDashboardData();
            }
        } catch (error) {
            console.error("Error loading dashboards:", error);
            this.state.error = _t("Failed to load dashboards");
        } finally {
            this.state.loading = false;
        }
    }

    async loadDashboardData() {
        if (!this.state.selectedDashboardId) {
            return;
        }

        try {
            this.state.refreshing = true;
            const data = await this.orm.call(
                "ops.dashboard",
                "get_dashboard_data",
                [this.state.selectedDashboardId, this.state.period]
            );

            if (data.error) {
                this.state.error = data.error;
                this.state.dashboardData = null;
            } else {
                this.state.dashboardData = data;
                this.state.error = null;
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = _t("Failed to load dashboard data");
        } finally {
            this.state.refreshing = false;
        }
    }

    setupAutoRefresh() {
        this.clearAutoRefresh();

        if (this.state.dashboardData && this.state.dashboardData.refresh_interval > 0) {
            this.refreshInterval = setInterval(() => {
                this.loadDashboardData();
            }, this.state.dashboardData.refresh_interval);
        }
    }

    clearAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    async onDashboardChange(ev) {
        this.state.selectedDashboardId = parseInt(ev.target.value);
        await this.loadDashboardData();
        this.setupAutoRefresh();
    }

    async onPeriodChange(ev) {
        this.state.period = ev.target.value;
        await this.loadDashboardData();
    }

    async onRefresh() {
        await this.loadDashboardData();
        this.notification.add(_t("Dashboard refreshed"), {
            type: "success",
        });
    }

    /**
     * Format a widget value according to its format type
     * Uses the company's currency for currency formatting
     */
    formatValue(widget) {
        const value = widget.value || 0;
        const formatType = widget.format_type || "number";

        switch (formatType) {
            case "currency":
                return this.formatCurrency(value);
            case "percentage":
                return `${value.toFixed(1)}%`;
            case "integer":
                return new Intl.NumberFormat().format(Math.round(value));
            default:
                return new Intl.NumberFormat(undefined, {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2,
                }).format(value);
        }
    }

    /**
     * Format a value as currency using the company's currency symbol and position
     */
    formatCurrency(value) {
        const absValue = Math.abs(value);
        const isNegative = value < 0;

        // Format the number with thousand separators, no decimals for large values
        const formatted = new Intl.NumberFormat(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: absValue >= 1000 ? 0 : 2,
        }).format(absValue);

        const symbol = this.state.currencySymbol || "$";
        let result;

        // Position the symbol based on currency settings
        if (this.state.currencyPosition === "after") {
            result = `${formatted} ${symbol}`;
        } else {
            result = `${symbol}${formatted}`;
        }

        return isNegative ? `-${result}` : result;
    }

    /**
     * Get the CSS color class for a card based on its color
     */
    getCardColorClass(widget) {
        const color = widget.color || "#3b82f6";
        if (color.includes("10b981") || color.includes("059669") || color.toLowerCase().includes("green")) {
            return "color-green";
        }
        if (color.includes("f59e0b") || color.includes("eab308") || color.toLowerCase().includes("yellow")) {
            return "color-yellow";
        }
        if (color.includes("ef4444") || color.includes("dc2626") || color.toLowerCase().includes("red")) {
            return "color-red";
        }
        if (color.includes("8b5cf6") || color.includes("7c3aed") || color.toLowerCase().includes("purple")) {
            return "color-purple";
        }
        if (color.includes("14b8a6") || color.includes("0d9488") || color.toLowerCase().includes("teal")) {
            return "color-teal";
        }
        if (color.includes("f97316") || color.toLowerCase().includes("orange")) {
            return "color-orange";
        }
        return "color-blue";
    }

    getTrendClass(widget) {
        const direction = widget.trend_direction;
        const isGood = widget.trend_is_good;

        if (direction === "flat") {
            return "trend-flat";
        }

        if (direction === "up") {
            return isGood ? "trend-up-good" : "trend-up-bad";
        }

        if (direction === "down") {
            return isGood ? "trend-down-good" : "trend-down-bad";
        }

        return "trend-flat";
    }

    getTrendIcon(widget) {
        const direction = widget.trend_direction;

        if (direction === "up") {
            return "fa-arrow-up";
        }
        if (direction === "down") {
            return "fa-arrow-down";
        }
        return "fa-minus";
    }

    get hasAutoRefresh() {
        return this.state.dashboardData && this.state.dashboardData.refresh_interval > 0;
    }

    get refreshIntervalText() {
        if (!this.state.dashboardData) return "";
        const ms = this.state.dashboardData.refresh_interval;
        const seconds = Math.floor(ms / 1000);
        if (seconds >= 60) {
            return `${Math.floor(seconds / 60)} min`;
        }
        return `${seconds}s`;
    }
}

OpsDashboardAction.template = "ops_dashboard.DashboardAction";

registry.category("actions").add("ops_dashboard_action", OpsDashboardAction);

export default OpsDashboardAction;
