odoo.define('hr_attendance_report_advanced.matrix', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var $ = core.$;

    function getMatrixRecordId() {
        var hash = window.location.hash || '';
        var match = hash.match(/[?&]id=(\d+)/) || hash.match(/id=(\d+)/);
        if (match) return parseInt(match[1], 10);
        var form = document.querySelector('form.o_form_view');
        if (form) {
            var idInput = form.querySelector('input[name="id"]');
            if (idInput && idInput.value) return parseInt(idInput.value, 10);
        }
        return null;
    }

    function loadAndRenderMatrix() {
        var matrixEl = document.querySelector('.o_attendance_matrix');
        if (!matrixEl) return;

        var container = document.getElementById('matrix_table_container');
        if (!container) return;

        var matrixId = getMatrixRecordId();
        var params = matrixId ? { matrix_id: matrixId } : {};

        if (!matrixId) {
            var form = matrixEl.closest('form');
            if (form) {
                var fromInput = form.querySelector('input[name="date_from"]');
                var toInput = form.querySelector('input[name="date_to"]');
                if (fromInput && fromInput.value) params.date_from = fromInput.value;
                if (toInput && toInput.value) params.date_to = toInput.value;
            }
        }

        container.innerHTML = '<p class="text-muted">Loading matrix...</p>';

        ajax.jsonRpc('/attendance/matrix/data', 'call', params).then(function(result) {
            if (result && result.status === 'success' && result.data) {
                renderMatrix(result.data);
            } else {
                var msg = (result && result.message) ? result.message : 'Failed to load matrix data.';
                container.innerHTML = '<p class="text-danger">' + msg + '</p>';
            }
        }).catch(function(error) {
            console.error('Matrix load error:', error);
            container.innerHTML = '<p class="text-danger">An error occurred while loading the matrix. Check the console.</p>';
        });
    }

    function formatTooltipValue(val) {
        if (val === null || val === undefined) return 'N/A';
        if (typeof val === 'string') return val.replace(/"/g, '&quot;');
        return String(val);
    }

    function renderMatrix(data) {
        var container = document.getElementById('matrix_table_container');
        if (!container || !data) return;

        var dates = data.dates || [];
        var employees = data.employees || [];

        if (dates.length === 0 || employees.length === 0) {
            container.innerHTML = '<p class="text-muted">No data available for the selected period.</p>';
            return;
        }

        var html = '<table class="matrix-table table table-sm table-bordered"><thead><tr><th>Employee</th><th>Department</th>';
        dates.forEach(function(date) {
            var dateObj = new Date(date + 'T12:00:00');
            var dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
            var dayNum = dateObj.getDate();
            html += '<th title="' + date + '">' + dayName + '<br/>' + dayNum + '</th>';
        });
        html += '</tr></thead><tbody>';

        employees.forEach(function(emp) {
            var name = (emp.employee_name || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            var dept = (emp.department || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            html += '<tr><td>' + name + '</td><td>' + dept + '</td>';
            dates.forEach(function(date) {
                var dayData = emp.dates && emp.dates[date] ? emp.dates[date] : {};
                var status = dayData.status || 'absent';
                var color = dayData.color || '#6c757d';
                var hours = typeof dayData.hours === 'number' ? dayData.hours : 0;
                var checkIn = formatTooltipValue(dayData.check_in);
                var checkOut = formatTooltipValue(dayData.check_out);
                var tooltip = 'Status: ' + status + ' | Hours: ' + hours + ' | Check In: ' + checkIn + ' | Check Out: ' + checkOut;
                html += '<td class="matrix-cell" style="background-color:' + color + ';" title="' + tooltip + '">';
                if (hours > 0) {
                    html += '<span class="hours-badge">' + hours.toFixed(1) + 'h</span>';
                }
                html += '</td>';
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        container.innerHTML = html;

        var cells = container.querySelectorAll('.matrix-cell');
        cells.forEach(function(cell) {
            cell.addEventListener('mouseenter', function() {
                this.style.opacity = '0.85';
                this.style.transform = 'scale(1.05)';
            });
            cell.addEventListener('mouseleave', function() {
                this.style.opacity = '1';
                this.style.transform = 'scale(1)';
            });
        });
    }

    function initMatrix() {
        var matrixEl = document.querySelector('.o_attendance_matrix');
        if (!matrixEl) return;
        loadAndRenderMatrix();
    }

    $(document).ready(function() {
        initMatrix();
        $(document).on('click', '.o_matrix_refresh_btn', function() {
            var container = document.getElementById('matrix_table_container');
            if (container) loadAndRenderMatrix();
        });
    });

    var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
    if (MutationObserver) {
        var observer = new MutationObserver(function() {
            var matrixEl = document.querySelector('.o_attendance_matrix');
            if (matrixEl && document.getElementById('matrix_table_container')) {
                var key = matrixEl.getAttribute('data-matrix-init');
                if (!key) {
                    matrixEl.setAttribute('data-matrix-init', '1');
                    setTimeout(loadAndRenderMatrix, 150);
                }
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    return {
        loadMatrix: loadAndRenderMatrix,
    };
});
