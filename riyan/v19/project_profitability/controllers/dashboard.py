# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from typing import Any
from odoo import http, fields
from odoo.http import request
from dateutil.relativedelta import relativedelta


class ProfitabilityDashboard(http.Controller):

    @http.route('/project/profitability/dashboard', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """Get complete dashboard data"""

        # Lead-centric: get all opportunities and compute profitability on-the-fly
        opportunities = request.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('company_id', '=', request.env.company.id),
        ])
        lead_data_list: list[dict[str, Any]] = [lead.get_lead_profitability_data() for lead in opportunities]

        # Calculate overall KPIs from lead data
        total_revenue = sum(d['revenue']['recognized'] for d in lead_data_list)
        total_cost = sum(d['costs']['total'] for d in lead_data_list)
        total_margin = total_revenue - total_cost
        avg_margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0

        # Top/bottom performers by margin - only leads with meaningful data
        meaningful_leads = [
            d for d in lead_data_list
            if (d.get('so_total') or 0) > 0 or (d.get('revenue', {}).get('recognized') or 0) > 0 or (d.get('costs', {}).get('total') or 0) > 0
        ]
        sorted_by_margin: list[dict[str, Any]] = sorted(
            meaningful_leads,
            key=lambda d: (d.get('profitability', {}).get('margin') or 0, d.get('profitability', {}).get('margin_percentage') or 0),
            reverse=True
        )
        top_5: list[dict[str, Any]] = list(sorted_by_margin[:5])
        # Bottom 5: exclude top 5, take 5 worst, show worst first
        rest: list[dict[str, Any]] = list(sorted_by_margin[5:])
        bottom_5: list[dict[str, Any]] = list(rest[-5:][::-1]) if len(rest) >= 5 else list(rest[::-1])

        # Budget alerts (over budget)
        # Add 'variance' key so OWL template can safely access p.variance.cost
        over_budget = []
        for d in lead_data_list:
            budget_cost = (d.get('budget') or {}).get('cost') or 0
            actual_cost = (d.get('costs') or {}).get('total') or 0
            if budget_cost > 0 and actual_cost / budget_cost > 1.1:
                d_copy = dict(d)
                d_copy['variance'] = {
                    'cost': budget_cost - actual_cost,       # negative = over budget
                    'revenue': (d.get('budget') or {}).get('revenue', 0) - (d.get('revenue') or {}).get('recognized', 0),
                }
                over_budget.append(d_copy)

        # Lead & SO details (same as lead_data_list - computed on-the-fly)
        lead_so_details = lead_data_list

        # Group by customer for Lead & Sales Order Details table
        from collections import OrderedDict
        lead_so_by_customer = OrderedDict()
        for row in lead_so_details:
            customer = row.get('customer') or '—'
            if customer not in lead_so_by_customer:
                lead_so_by_customer[customer] = []
            lead_so_by_customer[customer].append(row)

        lead_so_details_by_customer = [
            {'customer': customer, 'projects': projects_list}
            for customer, projects_list in lead_so_by_customer.items()
        ]

        return {
            'kpis': {
                'active_projects': len(opportunities),
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_margin': total_margin,
                'avg_margin_percentage': avg_margin_pct,
            },
            'top_performers': top_5,
            'bottom_performers': bottom_5,
            'over_budget_projects': over_budget,
            'lead_so_details': lead_so_details,
            'lead_so_details_by_customer': lead_so_details_by_customer,
            'currency_symbol': request.env.company.currency_id.symbol,
        }

    @http.route('/project/profitability/trend', type='json', auth='user')
    def get_trend_data(self, project_id=None, period='month', **kwargs):
        """Get trend data for charts"""

        date_from = fields.Date.today() - relativedelta(months=12)
        domain = [('date', '>=', date_from)]
        if project_id:
            domain.append(('project_id', '=', int(project_id)))

        profitability_records = request.env['project.profitability'].search(
            domain,
            order='date asc'
        )

        # Group by period
        trend_data = []
        for record in profitability_records:
            trend_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'project': record.project_id.name,
                'revenue': record.revenue_recognized,
                'cost': record.total_cost,
                'margin': record.gross_margin,
                'margin_percentage': record.margin_percentage,
            })

        return trend_data

    @http.route('/project/profitability/export', type='http', auth='user')
    def export_profitability(self, **kwargs):
        """Export profitability data to Excel - same structure as Lead & Sales Order Details table"""
        import io
        import xlsxwriter

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Lead & Sales Order Details')

        # Headers - Status → Customer → Lead → SO → Invoice (same as dashboard table)
        headers = [
            'Status', 'Customer', 'Lead / Opportunity', 'Lead Expected Revenue',
            'Sales Order', 'SO Total', 'Revenue', 'Expense', 'Budget Rev', 'Budget Cost',
            'Margin', 'Margin %', 'Progress'
        ]
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#01F9C6',  # light blue (you can change)
            'border': 1
        })

        for col, header in enumerate(headers):
            worksheet.write(0, col, header,header_format)

        # Build export data - same as dashboard, computed on-the-fly for all leads
        opportunities = request.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('company_id', '=', request.env.company.id),
        ], order='partner_id, name')
        export_rows = [lead.get_lead_profitability_data() for lead in opportunities]
        export_rows.sort(key=lambda r: (r.get('customer', ''), r.get('project_name', '')))

        row = 1
        for data in export_rows:
            worksheet.write(row, 0, data.get('stage_name', '') or '-')
            worksheet.write(row, 1, data.get('customer', ''))
            worksheet.write(row, 2, data.get('lead_name', '') or data.get('project_name', '') or '-')
            worksheet.write(row, 3, data.get('lead_value', 0.0))
            worksheet.write(row, 4, data.get('so_reference', '') or '-')
            worksheet.write(row, 5, data.get('so_total', 0.0))
            rev = data.get('revenue', {}) or {}
            worksheet.write(row, 6, rev.get('recognized', 0.0))
            costs = data.get('costs', {}) or {}
            worksheet.write(row, 7, costs.get('total', 0.0))
            budget = data.get('budget', {}) or {}
            worksheet.write(row, 8, budget.get('revenue', 0.0))
            worksheet.write(row, 9, budget.get('cost', 0.0))
            prof = data.get('profitability', {}) or {}
            worksheet.write(row, 10, prof.get('margin', 0.0))
            worksheet.write(row, 11, prof.get('margin_percentage', 0.0))
            worksheet.write(row, 12, data.get('progress', 0.0))
            row += 1

        workbook.close()
        output.seek(0)

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=lead_sales_order_details.xlsx;')
            ]
        )
