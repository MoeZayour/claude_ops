/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount, onWillUpdateProps } from "@odoo/owl";

// =============================================================================
// COLOR PALETTE & UTILITIES
// =============================================================================
const COLORS = {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    purple: '#8b5cf6',
    pink: '#ec4899',
    teal: '#14b8a6',
    orange: '#f97316',
    palette: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'],
    paleGradients: {
        primary: ['rgba(59, 130, 246, 0.4)', 'rgba(59, 130, 246, 0.05)'],
        success: ['rgba(16, 185, 129, 0.4)', 'rgba(16, 185, 129, 0.05)'],
        warning: ['rgba(245, 158, 11, 0.4)', 'rgba(245, 158, 11, 0.05)'],
        danger: ['rgba(239, 68, 68, 0.4)', 'rgba(239, 68, 68, 0.05)'],
    },
};

/**
 * Format a numeric value according to type
 * @param {number} value - The value to format
 * @param {string} formatType - 'currency', 'percentage', 'integer', 'number'
 * @param {object} currencyInfo - {symbol, position, code}
 * @returns {string} Formatted value
 */
function formatValue(value, formatType = 'number', currencyInfo = { symbol: '$', position: 'before' }) {
    const absValue = Math.abs(value);
    const isNegative = value < 0;

    switch (formatType) {
        case 'currency': {
            // Format with appropriate decimal places
            const decimals = absValue >= 1000 ? 0 : 2;
            const formatted = new Intl.NumberFormat(undefined, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals,
            }).format(absValue);

            const symbol = currencyInfo.symbol || '$';
            let result;
            if (currencyInfo.position === 'after') {
                result = `${formatted} ${symbol}`;
            } else {
                result = `${symbol}${formatted}`;
            }
            return isNegative ? `-${result}` : result;
        }
        case 'percentage':
            return `${value.toFixed(1)}%`;
        case 'integer':
            return new Intl.NumberFormat().format(Math.round(value));
        default:
            return new Intl.NumberFormat(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2,
            }).format(value);
    }
}

/**
 * Abbreviate large numbers (e.g., 1.2M, 45K)
 */
function abbreviateNumber(num) {
    if (Math.abs(num) >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (Math.abs(num) >= 1000) {
        return (num / 1000).toFixed(0) + 'K';
    }
    return num.toFixed(0);
}

/**
 * Get Chart.js reference if loaded
 */
function getChart() {
    return window.Chart;
}

/**
 * Get ApexCharts reference if loaded
 */
function getApexCharts() {
    return window.ApexCharts;
}

// =============================================================================
// PERIOD SELECTOR COMPONENT
// =============================================================================
export class PeriodSelector extends Component {
    static template = "ops_dashboard.PeriodSelector";
    static props = {
        value: { type: String, optional: true },
        onChange: { type: Function },
        periods: { type: Array, optional: true },
    };

    setup() {
        this.defaultPeriods = [
            { value: 'today', label: 'Today' },
            { value: 'this_week', label: 'Week' },
            { value: 'this_month', label: 'Month' },
            { value: 'this_quarter', label: 'Quarter' },
            { value: 'this_year', label: 'Year' },
        ];
    }

    get periods() {
        return this.props.periods || this.defaultPeriods;
    }

    get currentValue() {
        return this.props.value || 'this_month';
    }

    onPeriodClick(periodValue) {
        this.props.onChange(periodValue);
    }
}

// =============================================================================
// FILTER PANEL COMPONENT
// =============================================================================
export class FilterPanel extends Component {
    static template = "ops_dashboard.FilterPanel";
    static props = {
        branches: { type: Array, optional: true },
        businessUnits: { type: Array, optional: true },
        filters: { type: Object, optional: true },
        onChange: { type: Function },
        collapsed: { type: Boolean, optional: true },
    };

    setup() {
        this.state = useState({
            collapsed: this.props.collapsed !== false,
        });
    }

    toggleCollapse() {
        this.state.collapsed = !this.state.collapsed;
    }

    onFilterChange(filterName, value) {
        const newFilters = { ...this.props.filters };
        newFilters[filterName] = value;
        this.props.onChange(newFilters);
    }
}

// =============================================================================
// KPI CARD WITH SPARKLINE
// =============================================================================
export class KPICardSparkline extends Component {
    static template = "ops_dashboard.KPICardSparkline";
    static props = {
        title: String,
        value: Number,
        formatType: { type: String, optional: true },
        color: { type: String, optional: true },
        icon: { type: String, optional: true },
        trend: { type: Object, optional: true },
        sparklineData: { type: Array, optional: true },
        currencyInfo: { type: Object, optional: true },
        onClick: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("sparklineCanvas");
        this.chart = null;

        onMounted(() => this.renderSparkline());
        onWillUnmount(() => this.destroyChart());
        onWillUpdateProps((nextProps) => {
            if (nextProps.sparklineData !== this.props.sparklineData) {
                this.destroyChart();
                setTimeout(() => this.renderSparkline(), 0);
            }
        });
    }

    get formattedValue() {
        return formatValue(this.props.value || 0, this.props.formatType, this.props.currencyInfo);
    }

    get trendClass() {
        const trend = this.props.trend;
        if (!trend) return 'trend-flat';
        if (trend.direction === 'up') {
            return trend.isGood ? 'trend-up-good' : 'trend-up-bad';
        }
        if (trend.direction === 'down') {
            return trend.isGood ? 'trend-down-good' : 'trend-down-bad';
        }
        return 'trend-flat';
    }

    get trendIcon() {
        const trend = this.props.trend;
        if (!trend || trend.direction === 'flat') return 'fa-minus';
        return trend.direction === 'up' ? 'fa-arrow-up' : 'fa-arrow-down';
    }

    get cardStyle() {
        return `--kpi-color: ${this.props.color || COLORS.primary}`;
    }

    renderSparkline() {
        const Chart = getChart();
        if (!Chart || !this.canvasRef.el || !this.props.sparklineData?.length) return;

        const ctx = this.canvasRef.el.getContext('2d');
        const color = this.props.color || COLORS.primary;

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 40);
        gradient.addColorStop(0, color.replace(')', ', 0.4)').replace('rgb', 'rgba'));
        gradient.addColorStop(1, color.replace(')', ', 0.05)').replace('rgb', 'rgba'));

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.props.sparklineData.map((_, i) => i),
                datasets: [{
                    data: this.props.sparklineData.map(d => d.value || d),
                    borderColor: color,
                    borderWidth: 2,
                    fill: true,
                    backgroundColor: gradient,
                    tension: 0.4,
                    pointRadius: 0,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                },
                scales: {
                    x: { display: false },
                    y: { display: false },
                },
                elements: {
                    line: { borderJoinStyle: 'round' },
                },
            },
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    onCardClick() {
        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}

// =============================================================================
// AREA CHART - Revenue Trends
// =============================================================================
export class AreaChart extends Component {
    static template = "ops_dashboard.AreaChart";
    static props = {
        title: String,
        subtitle: { type: String, optional: true },
        data: Array,
        dataKey: { type: String, optional: true },
        labelKey: { type: String, optional: true },
        color: { type: String, optional: true },
        showTarget: { type: Boolean, optional: true },
        targetValue: { type: Number, optional: true },
        formatType: { type: String, optional: true },
        currencyInfo: { type: Object, optional: true },
    };

    setup() {
        this.canvasRef = useRef("chartCanvas");
        this.chart = null;

        onMounted(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
        onWillUpdateProps((nextProps) => {
            if (nextProps.data !== this.props.data) {
                this.destroyChart();
                setTimeout(() => this.renderChart(), 0);
            }
        });
    }

    renderChart() {
        const Chart = getChart();
        if (!Chart || !this.canvasRef.el || !this.props.data?.length) return;

        const ctx = this.canvasRef.el.getContext('2d');
        const color = this.props.color || COLORS.primary;
        const dataKey = this.props.dataKey || 'value';
        const labelKey = this.props.labelKey || 'date';

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 280);
        gradient.addColorStop(0, color.replace(')', ', 0.3)').replace('rgb', 'rgba').replace('#', 'rgba(').replace(/([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i, (_, r, g, b) => `${parseInt(r, 16)}, ${parseInt(g, 16)}, ${parseInt(b, 16)}`));
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

        const datasets = [{
            label: this.props.title,
            data: this.props.data.map(d => d[dataKey]),
            borderColor: color,
            borderWidth: 2,
            fill: true,
            backgroundColor: gradient,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: color,
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2,
        }];

        // Add target line if specified
        if (this.props.showTarget && this.props.targetValue) {
            datasets.push({
                label: 'Target',
                data: this.props.data.map(() => this.props.targetValue),
                borderColor: COLORS.danger,
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
            });
        }

        const formatType = this.props.formatType;
        const currencyInfo = this.props.currencyInfo;

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.props.data.map(d => d[labelKey]),
                datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index',
                },
                plugins: {
                    legend: {
                        display: this.props.showTarget,
                        position: 'top',
                        align: 'end',
                        labels: {
                            boxWidth: 8,
                            boxHeight: 8,
                            usePointStyle: true,
                        },
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 8,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return formatValue(context.parsed.y, formatType, currencyInfo);
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { size: 11 } },
                    },
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            callback: function(value) {
                                return abbreviateNumber(value);
                            },
                        },
                    },
                },
            },
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// =============================================================================
// HORIZONTAL BAR CHART - Branch Comparison / Leaderboard
// =============================================================================
export class HorizontalBarChart extends Component {
    static template = "ops_dashboard.HorizontalBarChart";
    static props = {
        title: String,
        subtitle: { type: String, optional: true },
        data: Array,
        labelKey: { type: String, optional: true },
        valueKey: { type: String, optional: true },
        showRanking: { type: Boolean, optional: true },
        colors: { type: Array, optional: true },
        formatType: { type: String, optional: true },
        currencyInfo: { type: Object, optional: true },
        onClick: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("chartCanvas");
        this.chart = null;

        onMounted(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
        onWillUpdateProps((nextProps) => {
            if (nextProps.data !== this.props.data) {
                this.destroyChart();
                setTimeout(() => this.renderChart(), 0);
            }
        });
    }

    get sortedData() {
        if (!this.props.data) return [];
        const valueKey = this.props.valueKey || 'value';
        return [...this.props.data].sort((a, b) => b[valueKey] - a[valueKey]);
    }

    get maxValue() {
        if (!this.sortedData.length) return 0;
        const valueKey = this.props.valueKey || 'value';
        return Math.max(...this.sortedData.map(d => d[valueKey]));
    }

    renderChart() {
        const Chart = getChart();
        if (!Chart || !this.canvasRef.el || !this.props.data?.length) return;

        const ctx = this.canvasRef.el.getContext('2d');
        const labelKey = this.props.labelKey || 'name';
        const valueKey = this.props.valueKey || 'value';
        const colors = this.props.colors || COLORS.palette;

        const formatType = this.props.formatType;
        const currencyInfo = this.props.currencyInfo;

        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.sortedData.map(d => d[labelKey]),
                datasets: [{
                    data: this.sortedData.map(d => d[valueKey]),
                    backgroundColor: this.sortedData.map((_, i) => colors[i % colors.length]),
                    borderRadius: 4,
                    barThickness: 24,
                }],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        cornerRadius: 8,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return formatValue(context.parsed.x, formatType, currencyInfo);
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            callback: function(value) {
                                return abbreviateNumber(value);
                            },
                        },
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            color: '#334155',
                            font: { size: 12, weight: '500' },
                        },
                    },
                },
                onClick: (event, elements) => {
                    if (elements.length && this.props.onClick) {
                        const index = elements[0].index;
                        this.props.onClick(this.sortedData[index]);
                    }
                },
            },
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// =============================================================================
// DONUT CHART - AR Aging, Revenue by BU
// =============================================================================
export class DonutChart extends Component {
    static template = "ops_dashboard.DonutChart";
    static props = {
        title: String,
        subtitle: { type: String, optional: true },
        data: Array,
        labelKey: { type: String, optional: true },
        valueKey: { type: String, optional: true },
        centerValue: { type: [Number, String], optional: true },
        centerLabel: { type: String, optional: true },
        colors: { type: Array, optional: true },
        formatType: { type: String, optional: true },
        currencyInfo: { type: Object, optional: true },
        onClick: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("chartCanvas");
        this.chart = null;

        onMounted(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
        onWillUpdateProps((nextProps) => {
            if (nextProps.data !== this.props.data) {
                this.destroyChart();
                setTimeout(() => this.renderChart(), 0);
            }
        });
    }

    get totalValue() {
        if (!this.props.data) return 0;
        const valueKey = this.props.valueKey || 'value';
        return this.props.data.reduce((sum, d) => sum + (d[valueKey] || 0), 0);
    }

    get formattedCenterValue() {
        if (this.props.centerValue !== undefined) {
            if (typeof this.props.centerValue === 'number') {
                return formatValue(this.props.centerValue, this.props.formatType, this.props.currencyInfo);
            }
            return this.props.centerValue;
        }
        return formatValue(this.totalValue, this.props.formatType, this.props.currencyInfo);
    }

    get legendData() {
        if (!this.props.data) return [];
        const labelKey = this.props.labelKey || 'name';
        const valueKey = this.props.valueKey || 'value';
        const colors = this.props.colors || COLORS.palette;

        return this.props.data.map((d, i) => ({
            label: d[labelKey],
            value: d[valueKey],
            formattedValue: formatValue(d[valueKey], this.props.formatType, this.props.currencyInfo),
            color: colors[i % colors.length],
            percentage: this.totalValue ? ((d[valueKey] / this.totalValue) * 100).toFixed(1) : 0,
        }));
    }

    renderChart() {
        const Chart = getChart();
        if (!Chart || !this.canvasRef.el || !this.props.data?.length) return;

        const ctx = this.canvasRef.el.getContext('2d');
        const labelKey = this.props.labelKey || 'name';
        const valueKey = this.props.valueKey || 'value';
        const colors = this.props.colors || COLORS.palette;

        const formatType = this.props.formatType;
        const currencyInfo = this.props.currencyInfo;

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.props.data.map(d => d[labelKey]),
                datasets: [{
                    data: this.props.data.map(d => d[valueKey]),
                    backgroundColor: this.props.data.map((_, i) => colors[i % colors.length]),
                    borderWidth: 2,
                    borderColor: '#fff',
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        cornerRadius: 8,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                const value = formatValue(context.parsed, formatType, currencyInfo);
                                const percentage = ((context.parsed / context.chart.getDatasetMeta(0).total) * 100).toFixed(1);
                                return `${value} (${percentage}%)`;
                            },
                        },
                    },
                },
                onClick: (event, elements) => {
                    if (elements.length && this.props.onClick) {
                        const index = elements[0].index;
                        this.props.onClick(this.props.data[index]);
                    }
                },
            },
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// =============================================================================
// GAUGE CHART - Margin %, DSO, Budget Utilization
// =============================================================================
export class GaugeChart extends Component {
    static template = "ops_dashboard.GaugeChart";
    static props = {
        title: String,
        value: Number,
        min: { type: Number, optional: true },
        max: { type: Number, optional: true },
        zones: { type: Array, optional: true },
        formatType: { type: String, optional: true },
        currencyInfo: { type: Object, optional: true },
    };

    setup() {
        this.chartRef = useRef("gaugeChart");
        this.chart = null;

        onMounted(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
        onWillUpdateProps((nextProps) => {
            if (nextProps.value !== this.props.value) {
                this.destroyChart();
                setTimeout(() => this.renderChart(), 0);
            }
        });
    }

    get formattedValue() {
        return formatValue(this.props.value || 0, this.props.formatType, this.props.currencyInfo);
    }

    get percentage() {
        const min = this.props.min || 0;
        const max = this.props.max || 100;
        return Math.min(100, Math.max(0, ((this.props.value - min) / (max - min)) * 100));
    }

    get zones() {
        return this.props.zones || [
            { min: 0, max: 33, color: COLORS.danger },
            { min: 33, max: 66, color: COLORS.warning },
            { min: 66, max: 100, color: COLORS.success },
        ];
    }

    get currentColor() {
        const pct = this.percentage;
        for (const zone of this.zones) {
            if (pct >= zone.min && pct <= zone.max) {
                return zone.color;
            }
        }
        return COLORS.primary;
    }

    renderChart() {
        const ApexCharts = getApexCharts();
        if (!ApexCharts || !this.chartRef.el) return;

        const options = {
            series: [this.percentage],
            chart: {
                type: 'radialBar',
                height: 160,
                sparkline: { enabled: true },
            },
            plotOptions: {
                radialBar: {
                    startAngle: -135,
                    endAngle: 135,
                    hollow: {
                        size: '60%',
                    },
                    track: {
                        background: '#f1f5f9',
                        strokeWidth: '100%',
                    },
                    dataLabels: {
                        show: false,
                    },
                },
            },
            fill: {
                colors: [this.currentColor],
            },
            stroke: {
                lineCap: 'round',
            },
        };

        this.chart = new ApexCharts(this.chartRef.el, options);
        this.chart.render();
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// =============================================================================
// FUNNEL CHART - Quotation Pipeline
// =============================================================================
export class FunnelChart extends Component {
    static template = "ops_dashboard.FunnelChart";
    static props = {
        title: String,
        subtitle: { type: String, optional: true },
        data: Array,
        labelKey: { type: String, optional: true },
        valueKey: { type: String, optional: true },
        countKey: { type: String, optional: true },
        colors: { type: Array, optional: true },
        formatType: { type: String, optional: true },
        currencyInfo: { type: Object, optional: true },
        onClick: { type: Function, optional: true },
    };

    get maxValue() {
        if (!this.props.data?.length) return 0;
        const valueKey = this.props.valueKey || 'value';
        return Math.max(...this.props.data.map(d => d[valueKey] || 0));
    }

    get processedData() {
        if (!this.props.data) return [];
        const labelKey = this.props.labelKey || 'name';
        const valueKey = this.props.valueKey || 'value';
        const countKey = this.props.countKey || 'count';
        const colors = this.props.colors || COLORS.palette;
        const maxValue = this.maxValue;

        return this.props.data.map((d, i) => ({
            label: d[labelKey],
            value: d[valueKey],
            count: d[countKey],
            formattedValue: formatValue(d[valueKey], this.props.formatType, this.props.currencyInfo),
            color: colors[i % colors.length],
            width: maxValue ? (d[valueKey] / maxValue) * 100 : 0,
        }));
    }

    onStageClick(item) {
        if (this.props.onClick) {
            this.props.onClick(item);
        }
    }
}

// =============================================================================
// BULLET CHART - Target vs Actual
// =============================================================================
export class BulletChart extends Component {
    static template = "ops_dashboard.BulletChart";
    static props = {
        title: String,
        data: Array,
        labelKey: { type: String, optional: true },
        actualKey: { type: String, optional: true },
        targetKey: { type: String, optional: true },
        formatType: { type: String, optional: true },
        currencyInfo: { type: Object, optional: true },
    };

    get processedData() {
        if (!this.props.data) return [];
        const labelKey = this.props.labelKey || 'name';
        const actualKey = this.props.actualKey || 'actual';
        const targetKey = this.props.targetKey || 'target';

        return this.props.data.map(d => {
            const actual = d[actualKey] || 0;
            const target = d[targetKey] || 0;
            const max = Math.max(actual, target) * 1.1;

            return {
                label: d[labelKey],
                actual,
                target,
                formattedActual: formatValue(actual, this.props.formatType, this.props.currencyInfo),
                formattedTarget: formatValue(target, this.props.formatType, this.props.currencyInfo),
                actualWidth: max ? (actual / max) * 100 : 0,
                targetPosition: max ? (target / max) * 100 : 0,
                color: actual >= target ? COLORS.success : COLORS.warning,
            };
        });
    }
}

// =============================================================================
// ALERT LIST - KPIs Requiring Attention
// =============================================================================
export class AlertList extends Component {
    static template = "ops_dashboard.AlertList";
    static props = {
        title: String,
        alerts: Array,
        onClick: { type: Function, optional: true },
    };

    getSeverityClass(severity) {
        return `severity-${severity || 'info'}`;
    }

    getSeverityIcon(severity) {
        switch (severity) {
            case 'critical': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            case 'success': return 'fa-check-circle';
            default: return 'fa-info-circle';
        }
    }

    onAlertClick(alert) {
        if (this.props.onClick) {
            this.props.onClick(alert);
        }
    }
}

// =============================================================================
// DRILLDOWN BREADCRUMB
// =============================================================================
export class DrilldownBreadcrumb extends Component {
    static template = "ops_dashboard.DrilldownBreadcrumb";
    static props = {
        path: Array,
        onNavigate: { type: Function },
    };

    onItemClick(index) {
        this.props.onNavigate(index);
    }

    onBackClick() {
        if (this.props.path.length > 1) {
            this.props.onNavigate(this.props.path.length - 2);
        }
    }
}

// Export all components
export const ChartComponents = {
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
};

export { formatValue, abbreviateNumber, COLORS };
