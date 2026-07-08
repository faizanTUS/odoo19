# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

ANSWERED_STATUSES = ('answered', 'completed')
MISSED_STATUSES = ('no-answer', 'busy', 'failed')
ACTIVE_STATUSES = ('initiated', 'ringing')

DIRECTION_LABELS = {
    'inbound': 'Incoming',
    'outbound': 'Outgoing',
}

STATUS_LABELS = {
    'initiated': 'Initiated',
    'ringing': 'Ringing',
    'answered': 'Answered',
    'completed': 'Completed',
    'failed': 'Failed',
    'busy': 'Busy',
    'no-answer': 'No Answer',
    'unknown': 'Unknown',
}


class RingCentralDashboard(models.AbstractModel):
    _name = 'ringcentral.dashboard'
    _description = 'RingCentral Dashboard Data'

    # -------------------------------------------------------------------------
    # Date helpers
    # -------------------------------------------------------------------------

    @api.model
    def _get_date_bounds(self, preset='this_month', date_from=False, date_to=False):
        """Return (dt_start, dt_end_exclusive, period_label) in UTC for the user."""
        now = fields.Datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if preset == 'today':
            start = today
            end = today + timedelta(days=1)
            label = 'Today'
        elif preset == 'yesterday':
            start = today - timedelta(days=1)
            end = today
            label = 'Yesterday'
        elif preset == 'this_week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=7)
            label = 'This Week'
        elif preset == 'this_month':
            start = today.replace(day=1)
            end = start + relativedelta(months=1)
            label = 'This Month'
        elif preset == 'last_month':
            end = today.replace(day=1)
            start = end - relativedelta(months=1)
            label = 'Last Month'
        elif preset == 'this_quarter':
            quarter_month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=quarter_month, day=1)
            end = start + relativedelta(months=3)
            label = 'This Quarter'
        elif preset == 'this_year':
            start = today.replace(month=1, day=1)
            end = start + relativedelta(years=1)
            label = 'This Year'
        elif preset == 'custom' and date_from and date_to:
            start = fields.Datetime.to_datetime(date_from)
            if start:
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = fields.Datetime.to_datetime(date_to)
            if end_dt:
                end = end_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            else:
                end = today + timedelta(days=1)
            label = f"{fields.Date.to_string(start)} – {fields.Date.to_string(end_dt)}"
        else:
            start = today.replace(day=1)
            end = start + relativedelta(months=1)
            label = 'This Month'

        return start, end, label

    @api.model
    def _get_previous_period_bounds(self, dt_start, dt_end):
        """Return previous period bounds with the same duration as current."""
        duration = dt_end - dt_start
        prev_end = dt_start
        prev_start = prev_end - duration
        return prev_start, prev_end

    # -------------------------------------------------------------------------
    # Domain builders
    # -------------------------------------------------------------------------

    @api.model
    def _build_base_domain(self, filters, dt_start=None, dt_end=None):
        filters = filters or {}
        domain = []
        if dt_start:
            domain.append(('start_time', '>=', dt_start))
        if dt_end:
            domain.append(('start_time', '<', dt_end))

        user_id = filters.get('user_id')
        if user_id:
            domain.append(('user_id', '=', int(user_id)))

        company_id = filters.get('company_id')
        if company_id:
            domain.append(('company_id', '=', int(company_id)))

        direction = filters.get('direction')
        if direction:
            domain.append(('direction', '=', direction))

        status = filters.get('status')
        if status:
            domain.append(('status', '=', status))

        return domain

    @api.model
    def _merge_domains(self, *domains):
        result = []
        for domain in domains:
            if domain:
                result.extend(domain)
        return result

    @api.model
    def _domain_to_list(self, domain):
        """Ensure domain is JSON-serializable."""
        return [list(item) if isinstance(item, (list, tuple)) else item for item in domain]

    # -------------------------------------------------------------------------
    # Formatting helpers
    # -------------------------------------------------------------------------

    @api.model
    def _format_duration(self, seconds):
        seconds = int(seconds or 0)
        if seconds <= 0:
            return '0s'
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours:
            return f'{hours}h {minutes}m'
        if minutes:
            return f'{minutes}m {secs}s'
        return f'{secs}s'

    @api.model
    def _format_percent(self, value):
        return f'{value:.1f}%'

    @api.model
    def _count_calls(self, domain):
        return self.env['ringcentral.call.history'].search_count(domain)

    @api.model
    def _duration_aggregate(self, domain, operator='sum'):
        CallHistory = self.env['ringcentral.call.history']
        result = CallHistory._read_group(
            domain=domain + [('duration', '>', 0)],
            groupby=[],
            aggregates=[f'duration:{operator}'],
        )
        if not result:
            return 0
        return int(result[0][0] or 0)

    # -------------------------------------------------------------------------
    # KPI block
    # -------------------------------------------------------------------------

    @api.model
    def _build_kpi(self, key, label, icon, accent, value, action_domain, action_name, delta=None):
        return {
            'key': key,
            'label': label,
            'icon': icon,
            'accent': accent,
            'value': value,
            'delta': delta,
            'action_domain': self._domain_to_list(action_domain),
            'action_name': action_name,
        }

    @api.model
    def _aggregate_kpi_counts(self, domain):
        """Return KPI count buckets from a single _read_group pass."""
        rows = self.env['ringcentral.call.history']._read_group(
            domain=domain,
            groupby=['direction', 'status'],
            aggregates=['__count'],
        )
        totals = {
            'total': 0,
            'inbound': 0,
            'outbound': 0,
            'answered': 0,
            'missed': 0,
            'active': 0,
            'failed': 0,
        }
        for direction, status, count in rows:
            totals['total'] += count
            if direction == 'inbound':
                totals['inbound'] += count
            elif direction == 'outbound':
                totals['outbound'] += count
            if status in ANSWERED_STATUSES:
                totals['answered'] += count
            if status in MISSED_STATUSES:
                totals['missed'] += count
            if status in ACTIVE_STATUSES:
                totals['active'] += count
            if status == 'failed':
                totals['failed'] += count
        return totals

    @api.model
    def _compute_kpis(self, base_domain, prev_domain):
        current = self._aggregate_kpi_counts(base_domain)
        previous = self._aggregate_kpi_counts(prev_domain)
        duration_domain = base_domain + [('duration', '>', 0)]
        total_duration = self._duration_aggregate(duration_domain, 'sum')
        avg_duration = self._duration_aggregate(duration_domain, 'avg')

        def count_delta(key):
            return current[key] - previous[key]

        inbound_domain = base_domain + [('direction', '=', 'inbound')]
        outbound_domain = base_domain + [('direction', '=', 'outbound')]
        answered_domain = base_domain + [('status', 'in', list(ANSWERED_STATUSES))]
        missed_domain = base_domain + [('status', 'in', list(MISSED_STATUSES))]

        success_rate = (current['answered'] / current['total'] * 100) if current['total'] else 0

        return [
            self._build_kpi(
                'total_calls', 'Total Calls', 'fa-phone', '#714B67', str(current['total']),
                base_domain, 'All Calls', count_delta('total'),
            ),
            self._build_kpi(
                'inbound_calls', 'Incoming Calls', 'fa-arrow-down', '#17a2b8',
                str(current['inbound']),
                inbound_domain, 'Incoming Calls', count_delta('inbound'),
            ),
            self._build_kpi(
                'outbound_calls', 'Outgoing Calls', 'fa-arrow-up', '#28a745',
                str(current['outbound']),
                outbound_domain, 'Outgoing Calls', count_delta('outbound'),
            ),
            self._build_kpi(
                'answered_calls', 'Answered Calls', 'fa-check-circle', '#28a745',
                str(current['answered']),
                answered_domain, 'Answered Calls', count_delta('answered'),
            ),
            self._build_kpi(
                'missed_calls', 'Missed Calls', 'fa-times-circle', '#dc3545',
                str(current['missed']),
                missed_domain, 'Missed Calls', count_delta('missed'),
            ),
            self._build_kpi(
                'total_duration', 'Total Duration', 'fa-hourglass', '#6f42c1',
                self._format_duration(total_duration),
                duration_domain, 'Calls with Duration', None,
            ),
            self._build_kpi(
                'avg_duration', 'Avg Duration', 'fa-clock-o', '#ffc107',
                self._format_duration(avg_duration),
                duration_domain, 'Calls with Duration', None,
            ),
            self._build_kpi(
                'success_rate', 'Success Rate', 'fa-percent', '#714B67',
                self._format_percent(success_rate),
                answered_domain, 'Answered Calls', None,
            ),
        ]

    # -------------------------------------------------------------------------
    # Charts
    # -------------------------------------------------------------------------

    @api.model
    def _format_group_date(self, value, granularity='day'):
        if not value:
            return ''
        if granularity == 'hour':
            return value.strftime('%H:00')
        if granularity == 'week':
            return value.strftime('%b %d')
        if granularity == 'month':
            return value.strftime('%b %Y')
        return value.strftime('%b %d')

    @api.model
    def _chart_call_trend(self, base_domain):
        CallHistory = self.env['ringcentral.call.history']
        rows = CallHistory._read_group(
            domain=base_domain,
            groupby=['start_time:day', 'direction'],
            aggregates=['__count'],
            order='start_time:day',
        )
        day_order = []
        inbound_map = defaultdict(int)
        outbound_map = defaultdict(int)
        domain_map = {}

        for row in rows:
            day, direction, count = row[0], row[1], row[2]
            if day not in day_order:
                day_order.append(day)
            label = self._format_group_date(day)
            if direction == 'inbound':
                inbound_map[label] += count
            elif direction == 'outbound':
                outbound_map[label] += count
            domain_map[(label, direction)] = base_domain + [
                ('start_time', '>=', day),
                ('start_time', '<', day + timedelta(days=1)),
                ('direction', '=', direction),
            ]

        labels = [self._format_group_date(d) for d in day_order]
        inbound_data = [inbound_map.get(l, 0) for l in labels]
        outbound_data = [outbound_map.get(l, 0) for l in labels]
        action_domains = [
            self._domain_to_list(domain_map.get((l, 'inbound'), base_domain + [('direction', '=', 'inbound')]))
            for l in labels
        ]

        return {
            'labels': labels,
            'datasets': [
                {'label': 'Incoming', 'data': inbound_data, 'color': '#17a2b8'},
                {'label': 'Outgoing', 'data': outbound_data, 'color': '#28a745'},
            ],
            'action_domains': action_domains,
        }

    @api.model
    def _chart_direction_bar(self, base_domain):
        CallHistory = self.env['ringcentral.call.history']
        rows = CallHistory._read_group(
            domain=base_domain,
            groupby=['direction'],
            aggregates=['__count'],
        )
        labels, data, domains = [], [], []
        colors = {'inbound': '#17a2b8', 'outbound': '#28a745'}
        bg_colors = []
        for direction, count in rows:
            if not direction:
                continue
            labels.append(DIRECTION_LABELS.get(direction, direction))
            data.append(count)
            domains.append(self._domain_to_list(base_domain + [('direction', '=', direction)]))
            bg_colors.append(colors.get(direction, '#6c757d'))
        return {
            'labels': labels,
            'data': data,
            'colors': bg_colors,
            'action_domains': domains,
        }

    @api.model
    def _chart_status_doughnut(self, base_domain):
        CallHistory = self.env['ringcentral.call.history']
        rows = CallHistory._read_group(
            domain=base_domain,
            groupby=['status'],
            aggregates=['__count'],
            order='__count desc',
        )
        palette = ['#714B67', '#17a2b8', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14', '#6c757d']
        labels, data, domains, colors = [], [], [], []
        for idx, (status, count) in enumerate(rows):
            if not status:
                continue
            labels.append(STATUS_LABELS.get(status, status))
            data.append(count)
            domains.append(self._domain_to_list(base_domain + [('status', '=', status)]))
            colors.append(palette[idx % len(palette)])
        return {
            'labels': labels,
            'data': data,
            'colors': colors,
            'action_domains': domains,
        }

    @api.model
    def _chart_top_users(self, base_domain, limit=10):
        CallHistory = self.env['ringcentral.call.history']
        rows = CallHistory._read_group(
            domain=base_domain + [('user_id', '!=', False)],
            groupby=['user_id'],
            aggregates=['__count'],
            order='__count desc',
            limit=limit,
        )
        labels, data, domains, user_ids = [], [], [], []
        for user, count in rows:
            if not user:
                continue
            labels.append(user.name)
            data.append(count)
            user_ids.append(user.id)
            domains.append(self._domain_to_list(base_domain + [('user_id', '=', user.id)]))
        return {
            'labels': labels,
            'data': data,
            'user_ids': user_ids,
            'action_domains': domains,
        }

    @api.model
    def _chart_call_volume(self, base_domain, granularity='day'):
        groupby_field = f'start_time:{granularity}'
        CallHistory = self.env['ringcentral.call.history']
        rows = CallHistory._read_group(
            domain=base_domain,
            groupby=[groupby_field],
            aggregates=['__count'],
            order=groupby_field,
        )
        labels, data, domains = [], [], []
        for row in rows:
            period_start = row[0]
            count = row[1]
            label = self._format_group_date(period_start, granularity)
            labels.append(label)
            data.append(count)
            if granularity == 'day':
                period_end = period_start + timedelta(days=1)
            elif granularity == 'week':
                period_end = period_start + timedelta(weeks=1)
            else:
                period_end = period_start + relativedelta(months=1)
            domains.append(self._domain_to_list(base_domain + [
                ('start_time', '>=', period_start),
                ('start_time', '<', period_end),
            ]))
        return {
            'labels': labels,
            'data': data,
            'action_domains': domains,
        }

    @api.model
    def _chart_duration_trend(self, base_domain):
        CallHistory = self.env['ringcentral.call.history']
        rows = CallHistory._read_group(
            domain=base_domain + [('duration', '>', 0)],
            groupby=['start_time:day'],
            aggregates=['duration:avg'],
            order='start_time:day',
        )
        labels, data, domains = [], [], []
        for day, avg_val in rows:
            if not day:
                continue
            labels.append(self._format_group_date(day))
            data.append(round(avg_val or 0))
            domains.append(self._domain_to_list(base_domain + [
                ('start_time', '>=', day),
                ('start_time', '<', day + timedelta(days=1)),
                ('duration', '>', 0),
            ]))
        return {
            'labels': labels,
            'data': data,
            'action_domains': domains,
        }

    @api.model
    def _chart_missed_vs_answered(self, base_domain):
        answered = self._count_calls(base_domain + [('status', 'in', list(ANSWERED_STATUSES))])
        missed = self._count_calls(base_domain + [('status', 'in', list(MISSED_STATUSES))])
        return {
            'labels': ['Answered', 'Missed'],
            'data': [answered, missed],
            'colors': ['#28a745', '#dc3545'],
            'action_domains': [
                self._domain_to_list(base_domain + [('status', 'in', list(ANSWERED_STATUSES))]),
                self._domain_to_list(base_domain + [('status', 'in', list(MISSED_STATUSES))]),
            ],
        }

    @api.model
    def _sanitize_filters(self, filters):
        """Enforce ORM-level visibility rules on dashboard filters."""
        filters = dict(filters or {})
        if not self._is_dashboard_manager():
            filters['user_id'] = self.env.user.id
            if not filters.get('company_id'):
                filters['company_id'] = self.env.company.id
        return filters

    @api.model
    def _compute_charts(self, base_domain, granularity='day', is_manager=True):
        charts = {
            'call_trend': self._chart_call_trend(base_domain),
            'direction_bar': self._chart_direction_bar(base_domain),
            'status_doughnut': self._chart_status_doughnut(base_domain),
            'call_volume': self._chart_call_volume(base_domain, granularity),
            'duration_trend': self._chart_duration_trend(base_domain),
            'missed_vs_answered': self._chart_missed_vs_answered(base_domain),
        }
        if is_manager:
            charts['top_users'] = self._chart_top_users(base_domain)
        else:
            charts['top_users'] = {'labels': [], 'data': [], 'action_domains': []}
        return charts

    @api.model
    def _compute_analytics(self, base_domain, is_manager=True):
        CallHistory = self.env['ringcentral.call.history']
        total = self._count_calls(base_domain)
        answered = self._count_calls(base_domain + [('status', 'in', list(ANSWERED_STATUSES))])
        missed = self._count_calls(base_domain + [('status', 'in', list(MISSED_STATUSES))])

        success_rate = (answered / total * 100) if total else 0
        missed_rate = (missed / total * 100) if total else 0

        # Approximate response time as avg duration on inbound answered/completed calls.
        inbound_answered_domain = base_domain + [
            ('direction', '=', 'inbound'),
            ('status', 'in', list(ANSWERED_STATUSES)),
            ('duration', '>', 0),
        ]
        avg_response = self._duration_aggregate(inbound_answered_domain, 'avg')
        avg_duration = self._duration_aggregate(base_domain + [('duration', '>', 0)], 'avg')

        hourly_rows = CallHistory._read_group(
            domain=base_domain,
            groupby=['start_time:hour'],
            aggregates=['__count'],
            order='__count desc',
            limit=3,
        )
        peak_hours = []
        for hour_start, count in hourly_rows:
            if hour_start:
                peak_hours.append({
                    'hour': hour_start.strftime('%H:00'),
                    'count': count,
                    'action_domain': self._domain_to_list(base_domain + [
                        ('start_time', '>=', hour_start),
                        ('start_time', '<', hour_start + timedelta(hours=1)),
                    ]),
                })

        top_agents = []
        if is_manager:
            top_agents_rows = CallHistory._read_group(
                domain=base_domain + [
                    ('user_id', '!=', False),
                    ('status', 'in', list(ANSWERED_STATUSES)),
                ],
                groupby=['user_id'],
                aggregates=['__count'],
                order='__count desc',
                limit=5,
            )
            for user, count in top_agents_rows:
                if not user:
                    continue
                top_agents.append({
                    'id': user.id,
                    'name': user.name,
                    'count': count,
                    'action_domain': self._domain_to_list(base_domain + [
                        ('user_id', '=', user.id),
                        ('status', 'in', list(ANSWERED_STATUSES)),
                    ]),
                })

        contact_counts = defaultdict(int)
        contact_names = {}
        contact_domains = {}
        for partner_field in ('from_partner_id', 'to_partner_id'):
            rows = CallHistory._read_group(
                domain=base_domain + [(partner_field, '!=', False)],
                groupby=[partner_field],
                aggregates=['__count'],
                order='__count desc',
                limit=10,
            )
            for partner, count in rows:
                if not partner:
                    continue
                contact_counts[partner.id] += count
                contact_names[partner.id] = partner.display_name
                contact_domains[partner.id] = self._domain_to_list(base_domain + [
                    '|',
                    ('from_partner_id', '=', partner.id),
                    ('to_partner_id', '=', partner.id),
                ])

        top_contacts = sorted(
            contact_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]
        most_contacted = [
            {
                'id': partner_id,
                'name': contact_names[partner_id],
                'count': count,
                'action_domain': contact_domains[partner_id],
            }
            for partner_id, count in top_contacts
        ]

        daily_trend = self._chart_call_volume(base_domain, 'day')
        weekly_trend = self._chart_call_volume(base_domain, 'week')
        monthly_trend = self._chart_call_volume(base_domain, 'month')

        return {
            'success_rate': round(success_rate, 1),
            'missed_rate': round(missed_rate, 1),
            'avg_response_time': self._format_duration(avg_response),
            'avg_response_seconds': avg_response,
            'avg_call_duration': self._format_duration(avg_duration),
            'avg_duration_seconds': avg_duration,
            'peak_hours': peak_hours,
            'top_agents': top_agents,
            'most_contacted': most_contacted,
            'daily_trend': daily_trend,
            'weekly_trend': weekly_trend,
            'monthly_trend': monthly_trend,
            'success_rate_domain': self._domain_to_list(
                base_domain + [('status', 'in', list(ANSWERED_STATUSES))]
            ),
            'missed_rate_domain': self._domain_to_list(
                base_domain + [('status', 'in', list(MISSED_STATUSES))]
            ),
        }

    # -------------------------------------------------------------------------
    # Filter options
    # -------------------------------------------------------------------------

    @api.model
    def _is_dashboard_manager(self):
        """Users who can view and filter across all RingCentral users."""
        user = self.env.user
        return (
            user.has_group('ringcentral_integration.group_ringcentral_admin')
            or user.has_group('base.group_system')
        )

    @api.model
    def _get_filter_users(self):
        """Build user list for the dashboard filter dropdown."""
        user = self.env.user
        Users = self.env['res.users'].sudo()

        if not self._is_dashboard_manager():
            return [{'id': user.id, 'name': user.name}]

        user_ids = set()
        admin_group = self.env.ref(
            'ringcentral_integration.group_ringcentral_admin', raise_if_not_found=False
        )
        rc_user_group = self.env.ref(
            'ringcentral_integration.group_ringcentral_user', raise_if_not_found=False
        )
        group_ids = []
        if admin_group:
            group_ids.append(admin_group.id)
        if rc_user_group:
            group_ids.append(rc_user_group.id)

        if group_ids:
            rc_domain = [
                ('share', '=', False),
                ('active', '=', True),
                ('all_group_ids', 'in', group_ids),
            ]
            allowed_company_ids = self.env.companies.ids
            if allowed_company_ids:
                rc_domain.append(('company_ids', 'in', allowed_company_ids))
            rc_users = Users.search(rc_domain)
            user_ids.update(rc_users.ids)

        call_domain = [('user_id', '!=', False)]
        allowed_company_ids = self.env.companies.ids
        if allowed_company_ids:
            call_domain.append(('company_id', 'in', allowed_company_ids))
        call_rows = self.env['ringcentral.call.history']._read_group(
            domain=call_domain,
            groupby=['user_id'],
            aggregates=['__count'],
        )
        user_ids.update(row[0].id for row in call_rows if row[0])

        if not user_ids:
            user_ids.add(user.id)

        users = Users.search([('id', 'in', list(user_ids))], order='name')
        return [{'id': u.id, 'name': u.name} for u in users]

    @api.model
    def _get_filter_companies(self):
        """Companies available in the dashboard company filter."""
        if not self.env.user.has_group('base.group_multi_company'):
            return []
        return [
            {'id': company.id, 'name': company.name}
            for company in self.env.companies.sorted('name')
        ]

    @api.model
    def get_filter_options(self):
        CallHistory = self.env['ringcentral.call.history']
        is_manager = self._is_dashboard_manager()
        is_multi_company = self.env.user.has_group('base.group_multi_company')

        direction_field = CallHistory._fields['direction']
        status_field = CallHistory._fields['status']

        return {
            'is_admin': is_manager,
            'can_filter_users': is_manager,
            'is_multi_company': is_multi_company,
            'users': self._get_filter_users(),
            'companies': self._get_filter_companies(),
            'directions': [
                {'value': val, 'label': label}
                for val, label in direction_field.selection
            ],
            'statuses': [
                {'value': val, 'label': label}
                for val, label in status_field.selection
            ],
            'date_presets': [
                {'value': 'today', 'label': 'Today'},
                {'value': 'yesterday', 'label': 'Yesterday'},
                {'value': 'this_week', 'label': 'This Week'},
                {'value': 'this_month', 'label': 'This Month'},
                {'value': 'last_month', 'label': 'Last Month'},
                {'value': 'this_quarter', 'label': 'This Quarter'},
                {'value': 'this_year', 'label': 'This Year'},
                {'value': 'custom', 'label': 'Custom Range'},
            ],
        }

    # -------------------------------------------------------------------------
    # Main API
    # -------------------------------------------------------------------------

    @api.model
    def get_dashboard_data(self, filters=None):
        self.env['ringcentral.call.history'].check_access('read')
        filters = self._sanitize_filters(filters)
        is_manager = self._is_dashboard_manager()

        preset = filters.get('date_preset', 'this_month')
        dt_start, dt_end, period_label = self._get_date_bounds(
            preset,
            filters.get('date_from'),
            filters.get('date_to'),
        )
        prev_start, prev_end = self._get_previous_period_bounds(dt_start, dt_end)

        base_domain = self._build_base_domain(filters, dt_start, dt_end)
        prev_domain = self._build_base_domain(filters, prev_start, prev_end)
        granularity = filters.get('trend_granularity') or 'day'

        return {
            'period_label': period_label,
            'date_preset': preset,
            'kpis': self._compute_kpis(base_domain, prev_domain),
            'charts': self._compute_charts(base_domain, granularity, is_manager=is_manager),
            'analytics': self._compute_analytics(base_domain, is_manager=is_manager),
            'filter_options': self.get_filter_options(),
            'is_admin': is_manager,
        }
