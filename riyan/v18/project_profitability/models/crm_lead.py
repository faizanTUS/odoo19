# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    profitability_ids = fields.One2many(
        'lead.profitability',
        'lead_id',
        string='Profitability History'
    )
    current_profitability_id = fields.Many2one(
        'lead.profitability',
        string='Current Profitability',
        compute='_compute_current_profitability'
    )

    @api.depends('profitability_ids')
    def _compute_current_profitability(self):
        for lead in self:
            latest = lead.profitability_ids.sorted('date', reverse=True)
            lead.current_profitability_id = latest[0] if latest else False

    def get_lead_profitability_data(self):
        """
        Compute profitability data on-the-fly for dashboard/export.
        SO Total = sale order amount_total
        Cost = total of related POs (purchase order lines with analytic to project)
        Budget = from analytic budget (budget.line/budget.analytic in Odoo 18) for project
        No lead.profitability records required - computed on every refresh.
        """
        self.ensure_one()
        company = self.env.company

        # Get SO and project
        so = self.env['sale.order'].search([
            ('opportunity_id', '=', self.id),
            ('company_id', '=', company.id)
        ], limit=1)
        project = False
        analytic_account = False
        if so:
            if hasattr(self.env['project.project'], 'sale_order_id'):
                project = self.env['project.project'].search([
                    ('sale_order_id', '=', so.id),
                    ('company_id', '=', company.id)
                ], limit=1)
            if not project and hasattr(self.env['project.project'], 'sale_line_id'):
                projects = so.order_line.mapped('project_id')
                project = projects[0] if projects else False
            if project:
                analytic_account = project.account_id

        # SO Total = sale order amount_total
        so_total = so.amount_total if so else (self.expected_revenue or 0.0)

        # Revenue = invoiced amount from customer invoices (SO origin)
        invoiced_amount = 0.0
        paid_amount = 0.0
        if so and self.partner_id:
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('partner_id', '=', self.partner_id.id),
                ('invoice_origin', 'ilike', so.name),
                ('company_id', '=', company.id),
            ])
            invoiced_amount = sum(invoices.mapped('amount_total'))
            paid_amount = sum(inv.amount_total for inv in invoices if inv.payment_state == 'paid')
        revenue_recognized = invoiced_amount

        # Cost breakdown: timesheet, expense (hr.expense), vendor_bills (POs), other
        # From analytic lines when project exists, plus POs for vendor allocation
        timesheet_cost = expense_cost = vendor_bill_cost = other_cost = 0.0
        if analytic_account:
            account_id = analytic_account.id
            analytic_lines = self.env['account.analytic.line'].search([
                ('account_id', '=', account_id),
            ])
            # Timesheet (employee_id)
            ts_lines = analytic_lines.filtered(
                lambda l: l.amount < 0 and getattr(l, 'employee_id', None)
            )
            timesheet_cost = abs(sum(ts_lines.mapped('amount')))
            # Expense (hr.expense - expense_id)
            exp_lines = analytic_lines.filtered(
                lambda l: l.amount < 0 and getattr(l, 'expense_id', None)
            )
            expense_cost = abs(sum(exp_lines.mapped('amount')))
            # Vendor bills (move_line_id, not expense, not employee)
            vendor_lines = analytic_lines.filtered(
                lambda l: (
                    l.amount < 0 and getattr(l, 'move_line_id', None) and
                    not getattr(l, 'expense_id', None) and not getattr(l, 'employee_id', None)
                )
            )
            vendor_bill_cost = abs(sum(vendor_lines.mapped('amount')))
            # Other
            other_lines = analytic_lines.filtered(
                lambda l: (
                    l.amount < 0 and not getattr(l, 'employee_id', None) and
                    not getattr(l, 'expense_id', None) and not getattr(l, 'move_line_id', None)
                )
            )
            other_cost = abs(sum(other_lines.mapped('amount')))
        # Fallback: vendor cost from POs when no analytic lines (e.g. PO not yet billed)
        if analytic_account and vendor_bill_cost == 0 and 'purchase.order.line' in self.env:
            account_id = analytic_account.id
            polines = self.env['purchase.order.line'].search([
                ('order_id.state', 'in', ('purchase', 'done')),
                ('order_id.company_id', '=', company.id),
                ('display_type', '=', False),
            ])
            for line in polines:
                dist = getattr(line, 'analytic_distribution', None) or {}
                if isinstance(dist, dict):
                    pct = dist.get(str(account_id)) or dist.get(account_id) or 0
                    if pct:
                        vendor_bill_cost += (line.price_subtotal or 0) * (float(pct) / 100)
                elif getattr(line, 'analytic_account_id', None) and line.analytic_account_id.id == account_id:
                    vendor_bill_cost += line.price_subtotal or 0
        total_cost = timesheet_cost + expense_cost + vendor_bill_cost + other_cost

        # Budget = from analytic budget
        budget_revenue = budget_cost = budget_margin = 0.0
        if analytic_account:
            # ── Odoo 18: budget.analytic + budget.line ──
            # budget_amount is always positive; budget_type ('revenue'/'expense'/'both')
            # distinguishes direction. auto_account_id searches all analytic plan columns.
            if 'budget.line' in self.env:
                budget_lines = self.env['budget.line'].search([
                    ('auto_account_id', '=', analytic_account.id),
                    ('budget_analytic_id.state', 'not in', ['draft', 'canceled']),
                ])
                budget_revenue = sum(
                    bl.budget_amount for bl in budget_lines
                    if bl.budget_analytic_id.budget_type in ('revenue', 'both')
                )
                budget_cost = sum(
                    bl.budget_amount for bl in budget_lines
                    if bl.budget_analytic_id.budget_type in ('expense', 'both')
                )
            # ── Odoo 17 fallback: crossovered.budget.lines ──
            elif 'crossovered.budget.lines' in self.env:
                budget_lines = self.env['crossovered.budget.lines'].search([
                    ('analytic_account_id', '=', analytic_account.id)
                ])
                budget_revenue = sum(l.planned_amount for l in budget_lines if l.planned_amount > 0)
                budget_cost = abs(sum(l.planned_amount for l in budget_lines if l.planned_amount < 0))
            budget_margin = budget_revenue - budget_cost

        # Profitability
        gross_margin = revenue_recognized - total_cost
        # Margin %: use revenue as base; when no revenue, use so_total if available
        if revenue_recognized:
            margin_pct = (gross_margin / revenue_recognized * 100)
        elif so_total:
            margin_pct = (gross_margin / so_total * 100)
        else:
            margin_pct = 0.0
        progress = (revenue_recognized / so_total * 100) if so_total else 0.0

        # Status
        if margin_pct >= 30:
            prof_status = 'excellent'
        elif margin_pct >= 20:
            prof_status = 'good'
        elif margin_pct >= 10:
            prof_status = 'average'
        elif margin_pct >= 0:
            prof_status = 'poor'
        else:
            prof_status = 'loss'

        if budget_cost > 0:
            ratio = total_cost / budget_cost
            budget_status = 'over' if ratio > 1.1 else ('under' if ratio < 0.9 else 'on_track')
        else:
            budget_status = 'on_track'

        return {
            'project_name': self.name,
            'customer': self.partner_id.name or '',
            'lead_name': self.name,
            'lead_value': self.expected_revenue or 0.0,
            'so_reference': so.name if so else '',
            'so_total': so_total,
            'lead_id': self.id,
            'so_id': so.id if so else None,
            'stage_name': self.stage_id.name if self.stage_id else '',
            'revenue': {
                'invoiced': invoiced_amount,
                'paid': paid_amount,
                'recognized': revenue_recognized,
            },
            'costs': {
                'timesheet': timesheet_cost,
                'expense': expense_cost,
                'vendor_bills': vendor_bill_cost,
                'other': other_cost,
                'total': total_cost,
            },
            'budget': {
                'revenue': budget_revenue,
                'cost': budget_cost,
                'margin': budget_margin,
            },
            'profitability': {
                'margin': gross_margin,
                'margin_percentage': margin_pct,
                'status': prof_status,
            },
            'progress': progress,
        }

    def action_view_lead_profitability(self):
        self.ensure_one()
        return {
            'name': 'Lead Profitability',
            'type': 'ir.actions.act_window',
            'res_model': 'lead.profitability',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }

    def action_calculate_lead_profitability(self):
        self.ensure_one()
        prof = self.env['lead.profitability'].create({
            'lead_id': self.id,
            'date': fields.Date.today(),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lead.profitability',
            'res_id': prof.id,
            'view_mode': 'form',
            'target': 'new',
        }
