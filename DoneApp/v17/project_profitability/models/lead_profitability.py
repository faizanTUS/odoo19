# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Lead-centric profitability: Status → Customer → Lead → SO → Invoice"""
from odoo import models, fields, api


class LeadProfitability(models.Model):
    _name = 'lead.profitability'
    _description = 'Lead Profitability Report (Status → Customer → Lead → SO → Invoice)'
    _rec_name = 'lead_id'
    _order = 'date desc'

    lead_id = fields.Many2one('crm.lead', string='Lead / Opportunity', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Customer', related='lead_id.partner_id', store=True)
    stage_id = fields.Many2one('crm.stage', string='Status', related='lead_id.stage_id', store=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', compute='_compute_sale_order', store=True)
    project_id = fields.Many2one('project.project', string='Project', compute='_compute_project', store=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        compute='_compute_analytic_account',
        store=True
    )

    date = fields.Date(string='Calculation Date', default=fields.Date.today)

    # Revenue
    lead_value = fields.Monetary(string='Lead Expected Revenue', related='lead_id.expected_revenue', store=True)
    so_total = fields.Monetary(string='Sales Order Total', compute='_compute_so_total', store=True)
    invoiced_amount = fields.Monetary(string='Invoiced Amount', compute='_compute_financials', store=True)
    paid_amount = fields.Monetary(string='Paid Amount', compute='_compute_financials', store=True)
    revenue_recognized = fields.Monetary(string='Revenue Recognized', compute='_compute_financials', store=True)

    # Costs (from analytic account when project exists)
    timesheet_cost = fields.Monetary(string='Timesheet Cost', compute='_compute_financials', store=True)
    expense_cost = fields.Monetary(string='Expense Cost', compute='_compute_financials', store=True)
    vendor_bill_cost = fields.Monetary(string='Vendor Bill Cost', compute='_compute_financials', store=True)
    other_cost = fields.Monetary(string='Other Costs', compute='_compute_financials', store=True)
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_totals', store=True)

    # Budget
    budget_revenue = fields.Monetary(string='Budgeted Revenue', compute='_compute_budget', store=True)
    budget_cost = fields.Monetary(string='Budgeted Cost', compute='_compute_budget', store=True)
    budget_margin = fields.Monetary(string='Budgeted Margin', compute='_compute_budget', store=True)

    # Profitability
    gross_margin = fields.Monetary(string='Gross Margin', compute='_compute_totals', store=True)
    margin_percentage = fields.Float(string='Margin %', compute='_compute_totals', store=True, digits=(16, 2))
    progress = fields.Float(string='Progress %', compute='_compute_progress', store=True, digits=(16, 2))

    # Status
    profitability_status = fields.Selection([
        ('excellent', 'Excellent (>30%)'),
        ('good', 'Good (20-30%)'),
        ('average', 'Average (10-20%)'),
        ('poor', 'Poor (0-10%)'),
        ('loss', 'Loss Making (<0%)')
    ], string='Profitability Status', compute='_compute_status', store=True)
    budget_status = fields.Selection([
        ('under', 'Under Budget'),
        ('on_track', 'On Budget'),
        ('over', 'Over Budget')
    ], string='Budget Status', compute='_compute_status', store=True)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('lead_id')
    def _compute_sale_order(self):
        for record in self:
            so = False
            if record.lead_id:
                so = self.env['sale.order'].search([
                    ('opportunity_id', '=', record.lead_id.id),
                    ('company_id', '=', record.company_id.id)
                ], limit=1)
            record.sale_order_id = so

    @api.depends('sale_order_id')
    def _compute_project(self):
        for record in self:
            project = False
            if record.sale_order_id and hasattr(self.env['project.project'], 'sale_order_id'):
                project = self.env['project.project'].search([
                    ('sale_order_id', '=', record.sale_order_id.id),
                    ('company_id', '=', record.company_id.id)
                ], limit=1)
            if not project and record.sale_order_id and hasattr(self.env['project.project'], 'sale_line_id'):
                # project_sale: project from sale_line_id
                projects = record.sale_order_id.order_line.mapped('project_id')
                project = projects[0] if projects else False
            record.project_id = project

    @api.depends('project_id')
    def _compute_analytic_account(self):
        for record in self:
            record.analytic_account_id = record.project_id.analytic_account_id if record.project_id else False

    @api.depends('sale_order_id')
    def _compute_so_total(self):
        for record in self:
            record.so_total = record.sale_order_id.amount_total if record.sale_order_id else 0.0

    @api.depends('lead_id', 'sale_order_id', 'analytic_account_id', 'date', 'partner_id')
    def _compute_financials(self):
        for record in self:
            record.update({
                'invoiced_amount': 0.0,
                'paid_amount': 0.0,
                'revenue_recognized': 0.0,
                'timesheet_cost': 0.0,
                'expense_cost': 0.0,
                'vendor_bill_cost': 0.0,
                'other_cost': 0.0,
            })

            # Invoiced amount: from invoices linked to SO (invoice_origin)
            if record.sale_order_id and record.partner_id:
                invoices = self.env['account.move'].search([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_date', '<=', record.date),
                    ('partner_id', '=', record.partner_id.id),
                    ('invoice_origin', 'ilike', record.sale_order_id.name),
                ])
                record.invoiced_amount = sum(invoices.mapped('amount_total'))
                record.paid_amount = sum(inv.amount_total for inv in invoices if inv.payment_state == 'paid')

            # Revenue & costs from analytic lines (when project/analytic exists)
            if record.analytic_account_id:
                lines = self.env['account.analytic.line'].search([
                    ('account_id', '=', record.analytic_account_id.id),
                    ('date', '<=', record.date)
                ])
                revenue_lines = lines.filtered(lambda l: l.amount > 0)
                record.revenue_recognized = sum(revenue_lines.mapped('amount'))

                timesheet = lines.filtered(lambda l: l.amount < 0 and getattr(l, 'employee_id', None))
                record.timesheet_cost = abs(sum(timesheet.mapped('amount')))

                expense = lines.filtered(lambda l: l.amount < 0 and getattr(l, 'expense_id', None))
                record.expense_cost = abs(sum(expense.mapped('amount')))

                vendor = lines.filtered(lambda l: (
                    l.amount < 0 and getattr(l, 'move_line_id', None) and
                    not getattr(l, 'expense_id', None) and not getattr(l, 'employee_id', None)
                ))
                record.vendor_bill_cost = abs(sum(vendor.mapped('amount')))

                other = lines.filtered(lambda l: (
                    l.amount < 0 and not getattr(l, 'employee_id', None) and
                    not getattr(l, 'expense_id', None) and not getattr(l, 'move_line_id', None)
                ))
                record.other_cost = abs(sum(other.mapped('amount')))
            elif record.invoiced_amount:
                # No analytic account: use invoiced amount as revenue recognized
                record.revenue_recognized = record.invoiced_amount

    @api.depends('revenue_recognized', 'timesheet_cost', 'expense_cost', 'vendor_bill_cost', 'other_cost')
    def _compute_totals(self):
        for record in self:
            record.total_cost = (
                record.timesheet_cost + record.expense_cost +
                record.vendor_bill_cost + record.other_cost
            )
            record.gross_margin = record.revenue_recognized - record.total_cost
            record.margin_percentage = (
                (record.gross_margin / record.revenue_recognized * 100)
                if record.revenue_recognized else 0.0
            )

    @api.depends('revenue_recognized', 'so_total')
    def _compute_progress(self):
        for record in self:
            record.progress = (
                (record.revenue_recognized / record.so_total * 100)
                if record.so_total else 0.0
            )

    @api.depends('analytic_account_id')
    def _compute_budget(self):
        for record in self:
            record.budget_revenue = record.budget_cost = record.budget_margin = 0.0
            if not record.analytic_account_id:
                continue

            # ── Odoo 18: budget.analytic + budget.line ──
            # budget_amount is always positive; budget_type ('revenue'/'expense'/'both')
            # distinguishes direction. auto_account_id searches all analytic plan columns.
            if 'budget.line' in self.env:
                budget_lines = self.env['budget.line'].search([
                    ('auto_account_id', '=', record.analytic_account_id.id),
                    ('budget_analytic_id.state', 'not in', ['draft', 'canceled']),
                ])
                record.budget_revenue = sum(
                    bl.budget_amount for bl in budget_lines
                    if bl.budget_analytic_id.budget_type in ('revenue', 'both')
                )
                record.budget_cost = sum(
                    bl.budget_amount for bl in budget_lines
                    if bl.budget_analytic_id.budget_type in ('expense', 'both')
                )

            # ── Odoo 17 fallback: crossovered.budget.lines ──
            elif 'crossovered.budget.lines' in self.env:
                budget_lines = self.env['crossovered.budget.lines'].search([
                    ('analytic_account_id', '=', record.analytic_account_id.id)
                ])
                record.budget_revenue = sum(l.planned_amount for l in budget_lines if l.planned_amount > 0)
                record.budget_cost = abs(sum(l.planned_amount for l in budget_lines if l.planned_amount < 0))

            record.budget_margin = record.budget_revenue - record.budget_cost

    @api.depends('margin_percentage', 'total_cost', 'budget_cost')
    def _compute_status(self):
        for record in self:
            if record.margin_percentage >= 30:
                record.profitability_status = 'excellent'
            elif record.margin_percentage >= 20:
                record.profitability_status = 'good'
            elif record.margin_percentage >= 10:
                record.profitability_status = 'average'
            elif record.margin_percentage >= 0:
                record.profitability_status = 'poor'
            else:
                record.profitability_status = 'loss'

            if record.budget_cost > 0:
                ratio = record.total_cost / record.budget_cost
                record.budget_status = 'over' if ratio > 1.1 else ('under' if ratio < 0.9 else 'on_track')
            else:
                record.budget_status = 'on_track'

    def get_profitability_data(self):
        """Return data dict for dashboard/export (same structure as project)"""
        self.ensure_one()
        return {
            'project_name': self.lead_id.name,
            'customer': self.partner_id.name or '',
            'lead_name': self.lead_id.name,
            'lead_value': self.lead_value,
            'so_reference': self.sale_order_id.name if self.sale_order_id else '',
            'so_total': self.so_total,
            'lead_id': self.lead_id.id,
            'so_id': self.sale_order_id.id if self.sale_order_id else None,
            'stage_name': self.stage_id.name if self.stage_id else '',
            'revenue': {
                'invoiced': self.invoiced_amount,
                'paid': self.paid_amount,
                'recognized': self.revenue_recognized,
            },
            'costs': {
                'timesheet': self.timesheet_cost,
                'expense': self.expense_cost,
                'vendor_bills': self.vendor_bill_cost,
                'other': self.other_cost,
                'total': self.total_cost,
            },
            'budget': {
                'revenue': self.budget_revenue,
                'cost': self.budget_cost,
                'margin': self.budget_margin,
            },
            'profitability': {
                'margin': self.gross_margin,
                'margin_percentage': self.margin_percentage,
                'status': self.profitability_status,
            },
            'progress': self.progress,
        }

    @api.model
    def create_snapshot_for_all_leads(self):
        """Create profitability snapshot for all opportunities"""
        leads = self.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('company_id', '=', self.env.company.id),
        ])
        for lead in leads:
            self.create({'lead_id': lead.id, 'date': fields.Date.today()})
        return True
