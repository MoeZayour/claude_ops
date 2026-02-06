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
 * Get ApexCharts reference if loaded
 */
function getApexCharts() {
    return window.ApexCharts;
}

// =============================================================================
// PERIOD SELECTOR COMPONENT
// =============================================================================
export class PeriodSelector extends Component {
    static template = "ops_kpi.PeriodSelector";
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
    static template = "ops_kpi.FilterPanel";
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
// KPI CARD WITH SPARKLINE (ApexCharts)
// =============================================================================
export class KPICardSparkline extends Component {
    static template = "ops_kpi.KPICardSparkline";
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
        this.chartRef = useRef("sparklineCanvas");
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
        const ApexCharts = getApexCharts();
        if (!ApexCharts || !this.chartRef.el || !this.props.sparklineData?.length) return;

        const color = this.props.color || COLORS.primary;
        const data = this.props.sparklineData.map(d => d.value !== undefined ? d.value : d);

        const options = {
            chart: {
                type: 'area',
                sparkline: { enabled: true },
                height: 50,
                animations: { enabled: false },
            },
            series: [{ data: data }],
            stroke: { curve: 'smooth', width: 2 },
            colors: [color],
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.4,
                    opacityTo: 0,
                },
            },
            tooltip: { enabled: false },
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

    onCardClick() {
        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}

// =============================================================================
// AREA CHART - Revenue Trends (ApexCharts)
// =============================================================================
export class AreaChart extends Component {
    static template = "ops_kpi.AreaChart";
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
        this.chartRef = useRef("chartCanvas");
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
        const ApexCharts = getApexCharts();
        if (!ApexCharts || !this.chartRef.el || !this.props.data?.length) return;

        const color = this.props.color || COLORS.primary;
        const dataKey = this.props.dataKey || 'value';
        const labelKey = this.props.labelKey || 'date';
        const formatType = this.props.formatType;
        const currencyInfo = this.props.currencyInfo;

        const series = [{
            name: this.props.title,
            data: this.props.data.map(d => d[dataKey]),
        }];

        const colors = [color];

        // Add target line if specified
        if (this.props.showTarget && this.props.targetValue) {
            series.push({
                name: 'Target',
                data: this.props.data.map(() => this.props.targetValue),
            });
            colors.push(COLORS.danger);
        }

        const options = {
            chart: {
                type: 'area',
                height: 300,
                toolbar: { show: false },
                animations: { enabled: true },
            },
            series: series,
            xaxis: {
                categories: this.props.data.map(d => d[labelKey]),
                labels: { style: { colors: '#94a3b8', fontSize: '11px' } },
                axisBorder: { show: false },
                axisTicks: { show: false },
            },
            yaxis: {
                labels: {
                    style: { colors: '#94a3b8', fontSize: '11px' },
                    formatter: function(value) {
                        return abbreviateNumber(value);
                    },
                },
            },
            stroke: {
                curve: 'smooth',
                width: this.props.showTarget && this.props.targetValue ? [2, 2] : [2],
                dashArray: this.props.showTarget && this.props.targetValue ? [0, 5] : [0],
            },
            colors: colors,
            fill: {
                type: this.props.showTarget && this.props.targetValue ? ['gradient', 'solid'] : ['gradient'],
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.45,
                    opacityTo: 0.05,
                },
                opacity: this.props.showTarget && this.props.targetValue ? [1, 0] : [1],
            },
            dataLabels: { enabled: false },
            legend: {
                show: !!this.props.showTarget,
                position: 'top',
                horizontalAlign: 'right',
            },
            grid: {
                borderColor: '#f1f5f9',
                xaxis: { lines: { show: false } },
            },
            tooltip: {
                theme: 'dark',
                y: {
                    formatter: function(val) {
                        return formatValue(val, formatType, currencyInfo);
                    },
                },
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
// HORIZONTAL BAR CHART - Branch Comparison / Leaderboard (ApexCharts)
// =============================================================================
export class HorizontalBarChart extends Component {
    static template = "ops_kpi.HorizontalBarChart";
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
        this.chartRef = useRef("chartCanvas");
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
        const ApexCharts = getApexCharts();
        if (!ApexCharts || !this.chartRef.el || !this.props.data?.length) return;

        const labelKey = this.props.labelKey || 'name';
        const valueKey = this.props.valueKey || 'value';
        const colors = this.props.colors || COLORS.palette;
        const formatType = this.props.formatType;
        const currencyInfo = this.props.currencyInfo;
        const sorted = this.sortedData;

        const options = {
            chart: {
                type: 'bar',
                height: 300,
                toolbar: { show: false },
                events: {
                    dataPointSelection: (event, chartContext, config) => {
                        if (this.props.onClick) {
                            const index = config.dataPointIndex;
                            this.props.onClick(sorted[index]);
                        }
                    },
                },
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    borderRadius: 4,
                    barHeight: '70%',
                    distributed: true,
                },
            },
            series: [{
                data: sorted.map(d => d[valueKey]),
            }],
            xaxis: {
                categories: sorted.map(d => d[labelKey]),
                labels: {
                    style: { colors: '#94a3b8', fontSize: '11px' },
                    formatter: function(value) {
                        return abbreviateNumber(value);
                    },
                },
            },
            yaxis: {
                labels: {
                    style: { colors: '#334155', fontSize: '12px', fontWeight: 500 },
                },
            },
            colors: sorted.map((_, i) => colors[i % colors.length]),
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return formatValue(val, formatType, currencyInfo);
                },
                style: { fontSize: '11px' },
            },
            grid: {
                borderColor: '#f1f5f9',
                yaxis: { lines: { show: false } },
            },
            legend: { show: false },
            tooltip: {
                theme: 'dark',
                y: {
                    formatter: function(val) {
                        return formatValue(val, formatType, currencyInfo);
                    },
                },
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
// DONUT CHART - AR Aging, Revenue by BU (ApexCharts)
// =============================================================================
export class DonutChart extends Component {
    static template = "ops_kpi.DonutChart";
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
        this.chartRef = useRef("chartCanvas");
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
        const ApexCharts = getApexCharts();
        if (!ApexCharts || !this.chartRef.el || !this.props.data?.length) return;

        const labelKey = this.props.labelKey || 'name';
        const valueKey = this.props.valueKey || 'value';
        const colors = this.props.colors || COLORS.palette;
        const formatType = this.props.formatType;
        const currencyInfo = this.props.currencyInfo;

        const options = {
            chart: {
                type: 'donut',
                height: 300,
                events: {
                    dataPointSelection: (event, chartContext, config) => {
                        if (this.props.onClick) {
                            const index = config.dataPointIndex;
                            this.props.onClick(this.props.data[index]);
                        }
                    },
                },
            },
            series: this.props.data.map(d => d[valueKey]),
            labels: this.props.data.map(d => d[labelKey]),
            colors: this.props.data.map((_, i) => colors[i % colors.length]),
            legend: { show: false },
            plotOptions: {
                pie: {
                    donut: {
                        size: '70%',
                        labels: {
                            show: false,
                        },
                    },
                },
            },
            stroke: {
                width: 2,
                colors: ['#fff'],
            },
            dataLabels: { enabled: false },
            tooltip: {
                y: {
                    formatter: function(val, opts) {
                        const total = opts.globals.seriesTotals.reduce((a, b) => a + b, 0);
                        const percentage = total ? ((val / total) * 100).toFixed(1) : 0;
                        return formatValue(val, formatType, currencyInfo) + ' (' + percentage + '%)';
                    },
                },
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
// GAUGE CHART - Margin %, DSO, Budget Utilization
// =============================================================================
export class GaugeChart extends Component {
    static template = "ops_kpi.GaugeChart";
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
    static template = "ops_kpi.FunnelChart";
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
    static template = "ops_kpi.BulletChart";
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
    static template = "ops_kpi.AlertList";
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
    static template = "ops_kpi.DrilldownBreadcrumb";
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
