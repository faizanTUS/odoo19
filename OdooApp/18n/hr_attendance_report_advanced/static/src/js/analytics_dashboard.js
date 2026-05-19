odoo.define('hr_attendance_report_advanced.dashboard', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var $ = core.$;

    // Function to load and render dashboard
    function initDashboard() {
        var $dashboard = $('.o_attendance_dashboard');
        if (!$dashboard.length) {
            return;
        }

        // Prefer server-injected data (set when user clicks Refresh Dashboard)
        var jsonEl = document.querySelector('textarea[name="dashboard_data_json"], input[name="dashboard_data_json"]');
        if (jsonEl && jsonEl.value) {
            try {
                var data = JSON.parse(jsonEl.value);
                loadAndRenderCharts(data);
                renderStatus(data);
                return;
            } catch (e) {
                console.warn("Could not parse dashboard_data_json", e);
            }
        }

        // Otherwise load via RPC
        var $form = $dashboard.closest('form');
        var dateFrom = $form.find('input[name="date_from"]').val();
        var dateTo = $form.find('input[name="date_to"]').val();
        var employeeIds = [];
        var departmentIds = [];
        $form.find('input[name="employee_ids"]').each(function() {
            if (this.value) employeeIds.push(parseInt(this.value, 10));
        });
        $form.find('input[name="department_ids"]').each(function() {
            if (this.value) departmentIds.push(parseInt(this.value, 10));
        });

        ajax.jsonRpc('/attendance/dashboard/data', 'call', {
            date_from: dateFrom,
            date_to: dateTo,
            employee_ids: employeeIds.length ? employeeIds : null,
            department_ids: departmentIds.length ? departmentIds : null,
        }).then(function(result) {
            if (result.status === 'success') {
                loadAndRenderCharts(result.data);
                renderStatus(result.data);
            }
        }).catch(function(error) {
            console.error("Error loading dashboard:", error);
        });
    }

    function renderKPIs(data) {
        if (!data.kpis) return;
        var kpis = data.kpis;
        var html = '';

        var cards = [
            { label: 'Total Employees', value: kpis.total_employees || 0, icon: 'fa-users', color: 'primary' },
            { label: 'Present Today', value: kpis.present_today || 0, icon: 'fa-check-circle', color: 'success' },
            { label: 'Attendance Rate', value: (kpis.attendance_rate || 0) + '%', icon: 'fa-percent', color: 'info' },
            { label: 'Total Hours', value: kpis.total_hours || 0, icon: 'fa-clock-o', color: 'warning' },
            { label: 'Avg Hours/Employee', value: kpis.avg_hours_per_employee || 0, icon: 'fa-bar-chart', color: 'secondary' },
        ];

        cards.forEach(function(kpi) {
            html += '<div class="kpi-card kpi-' + kpi.color + '">' +
                '<div class="kpi-icon"><i class="fa ' + kpi.icon + '"></i></div>' +
                '<div class="kpi-content">' +
                '<div class="kpi-label">' + kpi.label + '</div>' +
                '<div class="kpi-value">' + kpi.value + '</div>' +
                '</div></div>';
        });

        var $kpiContainer = $('#kpi_cards');
        if ($kpiContainer.length) {
            $kpiContainer.html(html);
        }
    }

    function loadAndRenderCharts(data) {
        // Load Chart.js if needed
        if (typeof Chart === 'undefined') {
            var script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
            script.onload = function() {
                renderCharts(data);
            };
            document.head.appendChild(script);
        } else {
            renderCharts(data);
        }
    }

    function renderCharts(data) {
        // Trends Chart
        var trendsCanvas = document.getElementById('trends_chart');
        if (trendsCanvas && data.trends) {
            new Chart(trendsCanvas, {
                type: 'line',
                data: {
                    labels: data.trends.map(function(t) { return t.date; }),
                    datasets: [{
                        label: 'Attendance Count',
                        data: data.trends.map(function(t) { return t.count; }),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Department Chart
        var deptCanvas = document.getElementById('department_chart');
        if (deptCanvas && data.department_stats) {
            var deptData = data.department_stats;
            new Chart(deptCanvas, {
                type: 'bar',
                data: {
                    labels: Object.keys(deptData),
                    datasets: [{
                        label: 'Attendance Rate %',
                        data: Object.values(deptData).map(function(d) { return d.attendance_rate; }),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Punctuality Chart
        var punctCanvas = document.getElementById('punctuality_chart');
        if (punctCanvas && data.punctuality) {
            new Chart(punctCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['On Time', 'Late', 'Early'],
                    datasets: [{
                        data: [data.punctuality.on_time, data.punctuality.late, data.punctuality.early],
                        backgroundColor: ['rgba(75, 192, 192, 0.5)', 'rgba(255, 99, 132, 0.5)', 'rgba(255, 206, 86, 0.5)'],
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Overtime Chart
        var overtimeCanvas = document.getElementById('overtime_chart');
        if (overtimeCanvas && data.overtime) {
            new Chart(overtimeCanvas, {
                type: 'bar',
                data: {
                    labels: ['Overtime Statistics'],
                    datasets: [{
                        label: 'Total Overtime Hours',
                        data: [data.overtime.total_overtime],
                        backgroundColor: 'rgba(255, 159, 64, 0.5)',
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    }

    function renderStatus(data) {
        if (!data.current_status) return;
        var status = data.current_status;
        var checkedIn = status.checked_in || [];
        var checkedOut = status.checked_out || [];
        var html = '<div class="status-grid">';

        if (checkedIn.length > 0) {
            html += '<div class="status-group checked-in"><h4>Checked In</h4><ul>';
            checkedIn.forEach(function(emp) {
                html += '<li>' + emp.name + ' (since ' + emp.check_in + ')</li>';
            });
            html += '</ul></div>';
        }

        if (checkedOut.length > 0) {
            html += '<div class="status-group checked-out"><h4>Checked Out</h4><ul>';
            checkedOut.forEach(function(emp) {
                html += '<li>' + emp.name + (emp.check_out ? ' (at ' + emp.check_out + ')' : '') + '</li>';
            });
            html += '</ul></div>';
        }

        html += '</div>';
        var $statusContainer = $('#current_status_container');
        if ($statusContainer.length) {
            $statusContainer.html(html);
        }
    }

    // Initialize when page is ready
    $(document).ready(function() {
        initDashboard();
    });

    // Re-initialize when form is updated (for Odoo's dynamic form loading)
    var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
    if (MutationObserver) {
        var observer = new MutationObserver(function(mutations) {
            var $dashboard = $('.o_attendance_dashboard');
            if ($dashboard.length && !$dashboard.data('initialized')) {
                $dashboard.data('initialized', true);
                setTimeout(initDashboard, 100);
            }
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    return {};
});
