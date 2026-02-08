/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";

// Import chart components
import {
    PeriodSelector,
    FilterPanel,
    KPICardSparkline,
    AreaChart,
    HorizontalBarChart,
    DonutChart,
    GaugeChart,
    FunnelChart,
    BulletChart,
    AlertList,
    DrilldownBreadcrumb,
    formatValue,
    COLORS,
} from "./chart_components";

/**
 * OPS Dashboard Action Component V2
 * Enhanced dashboard with interactive charts, drill-down, and filters
 */
class OpsDashboardAction extends Component {
    static template = "ops_kpi.KPICenterAction";
    static props = ["*"];

    // Register child components
    static components = {
        PeriodSelector,
        FilterPanel,
        KPICardSparkline,
        AreaChart,
        HorizontalBarChart,
        DonutChart,
        GaugeChart,
        AlertList,
        DrilldownBreadcrumb,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        this.displaySettings = {};

        this.state = useState({
            // Dashboard selection
            dashboards: [],
            selectedDashboardId: null,

            // Data
            dashboardData: null,
            chartData: null,

            // UI State
            period: "this_month",
            loading: true,
            refreshing: false,
            error: null,
            viewMode: "grid", // 'grid' or 'list'
            filtersExpanded: false,

            // Filters
            filters: {
                branch_id: null,
                business_unit_id: null,
                date_from: null,
                date_to: null,
            },

            // Drilldown
            drilldownPath: [],
            drilldownData: null,

            // Currency info
            currencySymbol: "",
            currencyPosition: "before",
            currencyCode: "",
        });

        this.refreshInterval = null;

        this.periods = [
            { value: "today", label: _t("Today") },
            { value: "this_week", label: _t("Week") },
            { value: "this_month", label: _t("Month") },
            { value: "this_quarter", label: _t("Quarter") },
            { value: "this_year", label: _t("Year") },
        ];

        onWillStart(async () => {
            await this.loadDisplaySettings();
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
     * Load KPI display settings from company configuration.
     * Applied as data-* attributes on the dashboard container.
     */
    async loadDisplaySettings() {
        try {
            const result = await this.orm.call(
                "res.company",
                "read",
                [user.activeCompany.id],
                {
                    fields: [
                        "ops_kpi_gradient_headers",
                        "ops_kpi_sparkline_style",
                        "ops_kpi_chart_fill",
                        "ops_kpi_animation",
                        "ops_kpi_card_style",
                        "ops_kpi_color_scheme",
                        "ops_kpi_refresh_interval",
                    ],
                }
            );
            if (result && result.length) {
                this.displaySettings = result[0];
            }
        } catch (e) {
            // Gracefully fallback to defaults if fields don't exist yet
            console.warn("[OPS KPI] Could not load display settings:", e.message);
            this.displaySettings = {};
        }
    }

    /**
     * Get data attributes for the dashboard container based on settings.
     */
    get dashboardDataAttrs() {
        const s = this.displaySettings || {};
        return {
            "data-card-style": s.ops_kpi_card_style || "accent",
            "data-gradient-headers": s.ops_kpi_gradient_headers !== false ? "true" : "false",
            "data-sparkline-style": s.ops_kpi_sparkline_style || "gradient",
            "data-chart-fill": s.ops_kpi_chart_fill || "gradient",
            "data-color-scheme": s.ops_kpi_color_scheme || "default",
            "data-animation": s.ops_kpi_animation || "full",
        };
    }

    /**
     * Load the company's currency information
     */
    async loadCurrencyInfo() {
        try {
            const currencyInfo = await this.orm.call(
                "ops.kpi.board",
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
            this.state.currencySymbol = "$";
            this.state.currencyPosition = "before";
            this.state.currencyCode = "USD";
        }
    }

    get currencyInfo() {
        return {
            symbol: this.state.currencySymbol,
            position: this.state.currencyPosition,
            code: this.state.currencyCode,
        };
    }

    async loadDashboards() {
        try {
            this.state.loading = true;
            const dashboards = await this.orm.call(
                "ops.kpi.board",
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

            // Load both standard widget data and chart data
            const [widgetData, chartData] = await Promise.all([
                this.orm.call(
                    "ops.kpi.board",
                    "get_dashboard_data",
                    [this.state.selectedDashboardId, this.state.period]
                ),
                this.orm.call(
                    "ops.kpi.board",
                    "get_chart_data",
                    [this.state.selectedDashboardId, this.state.period]
                ),
            ]);

            if (widgetData.error) {
                this.state.error = widgetData.error;
                this.state.dashboardData = null;
                this.state.chartData = null;
            } else {
                this.state.dashboardData = widgetData;
                this.state.chartData = chartData;
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

    // =========================================================================
    // EVENT HANDLERS
    // =========================================================================

    async onDashboardChange(ev) {
        this.state.selectedDashboardId = parseInt(ev.target.value);
        this.state.drilldownPath = [];
        this.state.drilldownData = null;
        await this.loadDashboardData();
        this.setupAutoRefresh();
    }

    async onPeriodChange(newPeriod) {
        this.state.period = newPeriod;
        this.state.drilldownPath = [];
        this.state.drilldownData = null;
        await this.loadDashboardData();
    }

    async onFilterChange(newFilters) {
        this.state.filters = newFilters;
        await this.loadDashboardData();
    }

    async onRefresh() {
        await this.loadDashboardData();
        this.notification.add(_t("Dashboard refreshed"), {
            type: "success",
        });
    }

    toggleViewMode() {
        this.state.viewMode = this.state.viewMode === "grid" ? "list" : "grid";
    }

    // =========================================================================
    // DRILLDOWN HANDLERS
    // =========================================================================

    async onKPIDrilldown(widget) {
        if (!widget.kpi_id) return;

        // Set drilldown path: root (dashboard) + KPI
        this.state.drilldownPath = [
            {
                label: this.state.chartData?.dashboard_name || "Dashboard",
                type: "root",
            },
            {
                label: widget.name,
                kpi_id: widget.kpi_id,
                type: "kpi",
            },
        ];

        try {
            // Load detailed data for this KPI
            const [timeSeries, breakdown] = await Promise.all([
                this.orm.call("ops.kpi.board", "get_kpi_chart_data", [
                    widget.kpi_id,
                    "time_series",
                    this.state.period,
                ]),
                this.orm.call("ops.kpi.board", "get_kpi_chart_data", [
                    widget.kpi_id,
                    "breakdown",
                    this.state.period,
                    "ops_branch_id",
                ]),
            ]);

            this.state.drilldownData = {
                kpi: widget,
                timeSeries: timeSeries.data || [],
                breakdown: breakdown.data || [],
            };
        } catch (error) {
            console.error("Error loading drilldown data:", error);
            this.notification.add(_t("Failed to load details"), { type: "warning" });
        }
    }

    onDrilldownNavigate(index) {
        if (index <= 0) {
            // Back to main dashboard (index -1 = back button, 0 = root)
            this.state.drilldownPath = [];
            this.state.drilldownData = null;
        } else {
            // Navigate to specific level
            this.state.drilldownPath = this.state.drilldownPath.slice(0, index + 1);
        }
    }

    onChartItemClick(item) {
        // Handle click on chart item (e.g., branch in bar chart)
        if (item && item.id) {
            this.notification.add(_t("Clicked: ") + item.name, { type: "info" });
            // Could implement further drill-down here
        }
    }

    onAlertClick(alert) {
        // Navigate to the KPI or related records
        if (alert.kpi_id) {
            const widget = this.state.chartData?.kpi_cards?.find(
                (w) => w.kpi_id === alert.kpi_id
            );
            if (widget) {
                this.onKPIDrilldown(widget);
            }
        }
    }

    // =========================================================================
    // COMPUTED PROPERTIES
    // =========================================================================

    get hasChartData() {
        return (
            this.state.chartData &&
            (this.state.chartData.kpi_cards?.length > 0 ||
                this.state.chartData.trend_charts?.length > 0 ||
                this.state.chartData.breakdown_charts?.length > 0)
        );
    }

    get isInDrilldown() {
        return this.state.drilldownPath.length > 0;
    }

    get filterBranches() {
        return this.state.chartData?.filters?.branches || [];
    }

    get filterBusinessUnits() {
        return this.state.chartData?.filters?.business_units || [];
    }

    get alerts() {
        return this.state.chartData?.alerts || [];
    }

    get trendCharts() {
        return this.state.chartData?.trend_charts || [];
    }

    get breakdownCharts() {
        return this.state.chartData?.breakdown_charts || [];
    }

    get kpiCards() {
        // Use chart data KPI cards which include sparkline data
        return this.state.chartData?.kpi_cards || this.state.dashboardData?.widgets || [];
    }

    // =========================================================================
    // FORMATTING HELPERS
    // =========================================================================

    formatValue(widget) {
        const value = widget.value || 0;
        const formatType = widget.format_type || "number";
        return formatValue(value, formatType, this.currencyInfo);
    }

    formatCurrency(value) {
        return formatValue(value, "currency", this.currencyInfo);
    }

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

    // Helper for KPI card trend object
    getWidgetTrend(widget) {
        if (!widget.trend_direction || widget.trend_direction === "flat") {
            return null;
        }
        return {
            direction: widget.trend_direction,
            percentage: widget.trend_percentage || 0,
            isGood: widget.trend_is_good !== false,
        };
    }

    // Helper for sparkline data
    getWidgetSparkline(widget) {
        return widget.sparkline_data || [];
    }
}

OpsDashboardAction.template = "ops_kpi.KPICenterAction";

registry.category("actions").add("ops_kpi_center_action", OpsDashboardAction);

export default OpsDashboardAction;
