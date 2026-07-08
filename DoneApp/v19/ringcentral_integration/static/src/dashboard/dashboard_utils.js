/** @odoo-module **/

export const RC_CHART_PALETTE = [
    "#714B67",
    "#17a2b8",
    "#28a745",
    "#ffc107",
    "#dc3545",
    "#6f42c1",
    "#fd7e14",
    "#20c997",
];

export function formatNumber(value) {
    const n = Number(value) || 0;
    if (n >= 1000000) {
        return `${(n / 1000000).toFixed(1)}M`;
    }
    if (n >= 1000) {
        return `${(n / 1000).toFixed(1)}k`;
    }
    return String(n);
}

export function formatDelta(delta) {
    const n = Number(delta) || 0;
    if (n > 0) {
        return { text: `+${n}`, className: "o_rc_delta_up" };
    }
    if (n < 0) {
        return { text: String(n), className: "o_rc_delta_down" };
    }
    return { text: "0", className: "o_rc_delta_neutral" };
}

export function formatDurationSeconds(seconds) {
    const s = Number(seconds) || 0;
    if (s <= 0) {
        return "0s";
    }
    const hours = Math.floor(s / 3600);
    const minutes = Math.floor((s % 3600) / 60);
    const secs = Math.floor(s % 60);
    if (hours) {
        return `${hours}h ${minutes}m`;
    }
    if (minutes) {
        return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
}

export function kpiDeltaProps(delta, hint = "vs previous period") {
    const d = formatDelta(delta);
    return { delta, deltaText: d.text, deltaClass: d.className, deltaHint: hint };
}

export function defaultChartOptions(overrides = {}) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 500 },
        plugins: {
            legend: {
                position: "bottom",
                labels: { boxWidth: 12, padding: 12, usePointStyle: true },
            },
        },
        ...overrides,
    };
}

export function lineChartConfig(labels, datasets, options = {}) {
    return {
        type: "line",
        data: { labels, datasets },
        options: defaultChartOptions({
            plugins: { legend: { display: datasets.length > 1 } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: "rgba(0,0,0,0.05)" } },
            },
            ...options,
        }),
    };
}

export function barChartConfig(labels, data, colors, label = "Calls") {
    const bg = colors || RC_CHART_PALETTE[0];
    return {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label,
                data,
                backgroundColor: Array.isArray(bg) ? bg : labels.map(() => bg),
                borderRadius: 6,
                maxBarThickness: 48,
            }],
        },
        options: defaultChartOptions({
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: "rgba(0,0,0,0.05)" } },
            },
        }),
    };
}

export function doughnutChartConfig(labels, data, colors) {
    return {
        type: "doughnut",
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors || RC_CHART_PALETTE,
                borderWidth: 2,
                borderColor: "#fff",
            }],
        },
        options: defaultChartOptions({
            cutout: "62%",
            plugins: { legend: { position: "right" } },
        }),
    };
}

export function horizontalBarChartConfig(labels, data, colors, label = "Calls") {
    return {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label,
                data,
                backgroundColor: colors || RC_CHART_PALETTE,
                borderRadius: 6,
                maxBarThickness: 32,
            }],
        },
        options: defaultChartOptions({
            indexAxis: "y",
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: "rgba(0,0,0,0.05)" },
                },
                y: {
                    grid: { display: false },
                    ticks: { autoSkip: false },
                },
            },
        }),
    };
}

export function attachChartClick(config, onClick) {
    config.options = config.options || {};
    const existing = config.options.onClick;
    config.options.onClick = (evt, elements, chart) => {
        if (existing) {
            existing(evt, elements, chart);
        }
        if (elements.length && onClick) {
            const el = elements[0];
            onClick(el.index, el.datasetIndex, chart);
        }
    };
    return config;
}
