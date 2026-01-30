/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * OPS Dashboard Action Component
 * Displays KPI cards with real-time data and auto-refresh
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
            await this.loadDashboards();
        });

        onMounted(() => {
            this.setupAutoRefresh();
        });

        onWillUnmount(() => {
            this.clearAutoRefresh();
        });
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

    formatValue(widget) {
        const value = widget.value || 0;
        const formatType = widget.format_type || "number";

        switch (formatType) {
            case "currency":
                return new Intl.NumberFormat(undefined, {
                    style: "currency",
                    currency: "USD",
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }).format(value);
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
