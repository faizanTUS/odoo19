/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class RingCentralKPIDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            kpis: [],
            chartData: {
                directionChart: { inbound: 0, outbound: 0 },
                statusChart: { answered: 0, missed: 0 }
            },
            loading: true,
        });
        
        onWillStart(async () => {
            await Promise.all([this.loadKPIs(), this.loadChartData()]);
            this.state.loading = false;
        });
    }

    async loadKPIs() {
        try {
            // Force create KPIs by calling search with context
            const kpis = await this.orm.searchRead(
                "ringcentral.kpi",
                [],
                ["name", "kpi_type", "value", "icon", "color"],
                { 
                    context: { kpi_dashboard: true },
                    limit: 100 
                }
            );
            this.state.kpis = kpis && kpis.length > 0 ? kpis : await this.createDefaultKPIs();
        } catch (error) {
            console.error("Error loading KPIs:", error);
            this.state.kpis = await this.createDefaultKPIs();
        }
    }

    async loadChartData() {
        try {
            // Get call history data for charts
            // Domain will be automatically filtered by record rules based on user permissions
            const domain = [];
            const callHistory = await this.orm.searchRead(
                "ringcentral.call.history",
                domain,
                ["direction", "status"],
                { limit: 10000 }
            );

            // Calculate direction chart data
            const directionChart = { inbound: 0, outbound: 0 };
            const statusChart = { answered: 0, missed: 0 };

            callHistory.forEach(call => {
                const direction = ((call.direction || '') + '').toLowerCase();
                const status = ((call.status || '') + '').toLowerCase();

                // Direction chart (handle variations like 'Inbound', 'in', etc.)
                if (direction.startsWith('in')) {
                    directionChart.inbound++;
                } else if (direction.startsWith('out')) {
                    directionChart.outbound++;
                }

                // Status chart
                if (['answered', 'completed', 'connected', 'picked'].some(keyword => status.startsWith(keyword))) {
                    statusChart.answered++;
                } else if (['missed', 'failed', 'busy', 'no-answer', 'declined', 'voicemail'].some(keyword => status.startsWith(keyword))) {
                    statusChart.missed++;
                }
            });

            Object.assign(this.state.chartData.directionChart, directionChart);
            Object.assign(this.state.chartData.statusChart, statusChart);
        } catch (error) {
            console.error("Error loading chart data:", error);
            Object.assign(this.state.chartData.directionChart, { inbound: 0, outbound: 0 });
            Object.assign(this.state.chartData.statusChart, { answered: 0, missed: 0 });
        }
    }

    async createDefaultKPIs() {
        const kpiTypes = [
            { type: 'total_calls', name: 'Total Calls', icon: 'fa-phone' },
            { type: 'inbound_calls', name: 'Inbound Calls', icon: 'fa-arrow-down' },
            { type: 'outbound_calls', name: 'Outbound Calls', icon: 'fa-arrow-up' },
            { type: 'answered_calls', name: 'Answered Calls', icon: 'fa-check-circle' },
            { type: 'missed_calls', name: 'Missed Calls', icon: 'fa-times-circle' },
            { type: 'avg_duration', name: 'Avg Duration', icon: 'fa-clock-o' },
            { type: 'total_duration', name: 'Total Duration', icon: 'fa-hourglass' },
            { type: 'success_rate', name: 'Success Rate', icon: 'fa-percent' },
            { type: 'calls_today', name: 'Calls Today', icon: 'fa-calendar-day' },
            { type: 'calls_this_week', name: 'Calls This Week', icon: 'fa-calendar-week' },
            { type: 'calls_this_month', name: 'Calls This Month', icon: 'fa-calendar' },
            { type: 'active_calls', name: 'Active Calls', icon: 'fa-phone-square' },
        ];
        
        return kpiTypes.map((kpi, index) => ({
            id: index + 1,
            name: kpi.name,
            kpi_type: kpi.type,
            value: '0',
            icon: kpi.icon,
            color: 'text-primary'
        }));
    }

    getIconClass(kpi) {
        return kpi.icon || 'fa-chart-line';
    }

    getNumericValue(kpi) {
        const value = kpi.value || '0';
        // Extract numeric value from strings like "85%", "5m 30s", "10h 5m"
        if (value.includes('%')) {
            return parseFloat(value.replace('%', '')) || 0;
        }
        if (value.includes('h') || value.includes('m') || value.includes('s')) {
            // For duration, return a normalized value for visualization
            return this.parseDuration(value);
        }
        return parseFloat(value) || 0;
    }

    parseDuration(duration) {
        // Parse duration strings like "5m 30s", "10h 5m", "30s"
        let totalSeconds = 0;
        const hours = duration.match(/(\d+)h/);
        const minutes = duration.match(/(\d+)m/);
        const seconds = duration.match(/(\d+)s/);
        if (hours) totalSeconds += parseInt(hours[1]) * 3600;
        if (minutes) totalSeconds += parseInt(minutes[1]) * 60;
        if (seconds) totalSeconds += parseInt(seconds[1]);
        return totalSeconds;
    }

    getValueColor(kpi) {
        const value = this.getNumericValue(kpi);
        if (kpi.kpi_type === 'success_rate') {
            if (value >= 80) return '#28a745'; // Green
            if (value >= 60) return '#ffc107'; // Yellow
            return '#dc3545'; // Red
        }
        if (kpi.kpi_type === 'missed_calls') {
            if (value === 0) return '#28a745'; // Green
            if (value < 10) return '#ffc107'; // Yellow
            return '#dc3545'; // Red
        }
        if (kpi.kpi_type === 'answered_calls' || kpi.kpi_type === 'total_calls') {
            if (value > 0) return '#28a745'; // Green
            return '#6c757d'; // Gray
        }
        return '#007bff'; // Blue (default)
    }

    getBarChartHeight(value, max) {
        const numericValue = Number(value) || 0;
        const numericMax = Number(max) || 0;
        if (numericMax === 0) {
            return numericValue > 0 ? 100 : 5;
        }
        const percentage = (numericValue / numericMax) * 100;
        return Math.max(5, percentage);
    }

    getBarChartHeightSafe(value, max) {
        const height = this.getBarChartHeight(value, max);
        return Math.max(5, height || 0);
    }

    getMaxValue(data) {
        if (!data) {
            return 1;
        }
        const values = Object.values(data).map((val) => Number(val) || 0);
        const max = Math.max(...values, 0);
        return max > 0 ? max : 1;
    }

    getPieChartData(chartData) {
        const total = chartData.answered + chartData.missed;
        if (total === 0) {
            return {
                answered: { percentage: 0, angle: 0 },
                missed: { percentage: 0, angle: 0 }
            };
        }
        const answeredPercentage = (chartData.answered / total) * 100;
        const missedPercentage = (chartData.missed / total) * 100;
        return {
            answered: { 
                percentage: answeredPercentage, 
                angle: (answeredPercentage / 100) * 360 
            },
            missed: { 
                percentage: missedPercentage, 
                angle: (missedPercentage / 100) * 360 
            }
        };
    }

    getPieSlicePath(centerX, centerY, radius, startAngle, endAngle) {
        const startRad = (startAngle - 90) * Math.PI / 180;
        const endRad = (endAngle - 90) * Math.PI / 180;
        const x1 = centerX + radius * Math.cos(startRad);
        const y1 = centerY + radius * Math.sin(startRad);
        const x2 = centerX + radius * Math.cos(endRad);
        const y2 = centerY + radius * Math.sin(endRad);
        const largeArc = (endAngle - startAngle) > 180 ? 1 : 0;
        return `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
    }
}

RingCentralKPIDashboard.template = "ringcentral_integration.KPIDashboard";

registry.category("actions").add("ringcentral_kpi_dashboard", RingCentralKPIDashboard);

