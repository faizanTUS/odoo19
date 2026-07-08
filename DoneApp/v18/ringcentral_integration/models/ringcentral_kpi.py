# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class RingCentralKPI(models.TransientModel):
    _name = 'ringcentral.kpi'
    _description = 'RingCentral KPI Dashboard'

    name = fields.Char(string='KPI Name', required=True)
    kpi_type = fields.Selection([
        ('total_calls', 'Total Calls'),
        ('inbound_calls', 'Inbound Calls'),
        ('outbound_calls', 'Outbound Calls'),
        ('answered_calls', 'Answered Calls'),
        ('missed_calls', 'Missed Calls'),
        ('avg_duration', 'Average Duration'),
        ('total_duration', 'Total Duration'),
        ('success_rate', 'Success Rate'),
        ('calls_today', 'Calls Today'),
        ('calls_this_week', 'Calls This Week'),
        ('calls_this_month', 'Calls This Month'),
        ('active_calls', 'Active Calls'),
    ], string='KPI Type', required=True)
    value = fields.Char(string='Value', compute='_compute_value')
    icon = fields.Char(string='Icon', compute='_compute_icon')
    color = fields.Char(string='Color', compute='_compute_color')
    trend = fields.Char(string='Trend', compute='_compute_trend')

    @api.depends('kpi_type')
    def _compute_value(self):
        """Compute KPI value based on call history data"""
        call_history = self.env['ringcentral.call.history']
        today = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        for kpi in self:
            domain = []
            if self.env.user.has_group('ringcentral_integration.group_ringcentral_user'):
                # Users can only see their own calls
                domain = [('user_id', '=', self.env.user.id)]
            
            if kpi.kpi_type == 'total_calls':
                count = call_history.search_count(domain)
                kpi.value = str(count)
            elif kpi.kpi_type == 'inbound_calls':
                count = call_history.search_count(domain + [('direction', '=', 'inbound')])
                kpi.value = str(count)
            elif kpi.kpi_type == 'outbound_calls':
                count = call_history.search_count(domain + [('direction', '=', 'outbound')])
                kpi.value = str(count)
            elif kpi.kpi_type == 'answered_calls':
                count = call_history.search_count(domain + [('status', 'in', ['answered', 'completed'])])
                kpi.value = str(count)
            elif kpi.kpi_type == 'missed_calls':
                count = call_history.search_count(domain + [('status', 'in', ['no-answer', 'busy', 'failed'])])
                kpi.value = str(count)
            elif kpi.kpi_type == 'avg_duration':
                calls = call_history.search(domain + [('duration', '>', 0)])
                if calls:
                    avg = sum(calls.mapped('duration')) / len(calls)
                    minutes = int(avg // 60)
                    seconds = int(avg % 60)
                    kpi.value = f"{minutes}m {seconds}s"
                else:
                    kpi.value = "0s"
            elif kpi.kpi_type == 'total_duration':
                calls = call_history.search(domain + [('duration', '>', 0)])
                if calls:
                    total_seconds = sum(calls.mapped('duration'))
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    kpi.value = f"{hours}h {minutes}m"
                else:
                    kpi.value = "0h 0m"
            elif kpi.kpi_type == 'success_rate':
                total = call_history.search_count(domain)
                answered = call_history.search_count(domain + [('status', 'in', ['answered', 'completed'])])
                if total > 0:
                    rate = (answered / total) * 100
                    kpi.value = f"{rate:.1f}%"
                else:
                    kpi.value = "0%"
            elif kpi.kpi_type == 'calls_today':
                count = call_history.search_count(domain + [('start_time', '>=', today)])
                kpi.value = str(count)
            elif kpi.kpi_type == 'calls_this_week':
                count = call_history.search_count(domain + [('start_time', '>=', week_start)])
                kpi.value = str(count)
            elif kpi.kpi_type == 'calls_this_month':
                count = call_history.search_count(domain + [('start_time', '>=', month_start)])
                kpi.value = str(count)
            elif kpi.kpi_type == 'active_calls':
                count = call_history.search_count(domain + [('status', 'in', ['initiated', 'ringing'])])
                kpi.value = str(count)
            else:
                kpi.value = "0"

    @api.depends('kpi_type')
    def _compute_icon(self):
        """Compute icon for KPI"""
        icon_map = {
            'total_calls': 'fa-phone',
            'inbound_calls': 'fa-arrow-down',
            'outbound_calls': 'fa-arrow-up',
            'answered_calls': 'fa-check-circle',
            'missed_calls': 'fa-times-circle',
            'avg_duration': 'fa-clock-o',
            'total_duration': 'fa-hourglass',
            'success_rate': 'fa-percent',
            'calls_today': 'fa-calendar-day',
            'calls_this_week': 'fa-calendar-week',
            'calls_this_month': 'fa-calendar',
            'active_calls': 'fa-phone-square',
        }
        for kpi in self:
            kpi.icon = icon_map.get(kpi.kpi_type, 'fa-chart-line')

    @api.depends('kpi_type')
    def _compute_color(self):
        """Compute color for KPI"""
        color_map = {
            'total_calls': 'text-primary',
            'inbound_calls': 'text-info',
            'outbound_calls': 'text-success',
            'answered_calls': 'text-success',
            'missed_calls': 'text-danger',
            'avg_duration': 'text-warning',
            'total_duration': 'text-info',
            'success_rate': 'text-primary',
            'calls_today': 'text-info',
            'calls_this_week': 'text-primary',
            'calls_this_month': 'text-success',
            'active_calls': 'text-warning',
        }
        for kpi in self:
            kpi.color = color_map.get(kpi.kpi_type, 'text-secondary')

    @api.depends('kpi_type')
    def _compute_trend(self):
        """Compute trend indicator (placeholder for future enhancement)"""
        for kpi in self:
            kpi.trend = ""

    @api.model
    def _get_default_kpis(self):
        """Get default KPI records for dashboard"""
        kpi_types = [
            'total_calls', 'inbound_calls', 'outbound_calls', 'answered_calls',
            'missed_calls', 'avg_duration', 'total_duration', 'success_rate',
            'calls_today', 'calls_this_week', 'calls_this_month', 'active_calls'
        ]
        
        kpi_names = {
            'total_calls': 'Total Calls',
            'inbound_calls': 'Inbound Calls',
            'outbound_calls': 'Outbound Calls',
            'answered_calls': 'Answered Calls',
            'missed_calls': 'Missed Calls',
            'avg_duration': 'Avg Duration',
            'total_duration': 'Total Duration',
            'success_rate': 'Success Rate',
            'calls_today': 'Calls Today',
            'calls_this_week': 'Calls This Week',
            'calls_this_month': 'Calls This Month',
            'active_calls': 'Active Calls',
        }
        
        # Use sudo() to bypass access rights for this transient model
        self = self.sudo()
        
        # Check if we already have KPIs in the database for this session (use super to avoid recursion)
        try:
            existing_kpis = super(RingCentralKPI, self).search([])
            if existing_kpis and len(existing_kpis) == len(kpi_types):
                # Return existing KPIs and ensure computed fields are up to date
                existing_kpis._compute_value()
                existing_kpis._compute_icon()
                existing_kpis._compute_color()
                return existing_kpis
        except Exception:
            # If search fails, continue to create new KPIs
            pass
        
        # Create new KPIs with sudo to bypass access rights
        kpis = self.browse()
        for kpi_type in kpi_types:
            kpi = self.create({
                'name': kpi_names[kpi_type],
                'kpi_type': kpi_type,
            })
            kpis |= kpi
        
        # Ensure computed fields are calculated for all KPIs
        if kpis:
            kpis._compute_value()
            kpis._compute_icon()
            kpis._compute_color()
        
        return kpis
    
    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        """Override search to return KPI records when in dashboard context"""
        # Always return KPIs for this transient model (it's only used for dashboard)
        kpis = self._get_default_kpis()
        # Apply domain filtering if needed
        if domain:
            # Filter by kpi_type if domain specifies it
            kpi_type_domain = [d for d in domain if isinstance(d, (list, tuple)) and len(d) == 3 and d[0] == 'kpi_type']
            if kpi_type_domain:
                filter_type = kpi_type_domain[0][2]
                kpis = kpis.filtered(lambda k: k.kpi_type == filter_type)
        # Apply offset and limit
        if offset:
            kpis = kpis[offset:]
        if limit:
            kpis = kpis[:limit]
        return kpis
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to return KPI records with computed values"""
        kpis = self.search(domain or [], offset=offset, limit=limit, order=order)
        # Ensure computed fields are up to date
        if kpis:
            kpis._compute_value()
            kpis._compute_icon()
            kpis._compute_color()
        # Return as list of dicts
        return kpis.read(fields or [])
    
    @api.model
    def search_count(self, domain):
        """Override search_count for dashboard context"""
        kpis = self._get_default_kpis()
        # Apply domain filtering if needed
        if domain:
            kpi_type_domain = [d for d in domain if isinstance(d, (list, tuple)) and len(d) == 3 and d[0] == 'kpi_type']
            if kpi_type_domain:
                filter_type = kpi_type_domain[0][2]
                kpis = kpis.filtered(lambda k: k.kpi_type == filter_type)
        return len(kpis)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override read_group to return KPI records grouped by type"""
        if self.env.context.get('kpi_dashboard'):
            # Generate KPI records
            kpis = self._get_default_kpis()
            result = []
            for kpi in kpis:
                result.append({
                    'kpi_type': kpi.kpi_type,
                    'kpi_type_count': 1,
                    '__count': 1,
                    '__domain': [('kpi_type', '=', kpi.kpi_type)],
                })
            return result
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

