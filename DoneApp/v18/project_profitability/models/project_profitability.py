# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectProfitability(models.Model):
    _name = 'project.profitability'
    _description = 'Project Profitability Tracking'
    _rec_name = 'project_id'
    _order = 'date desc'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', related='project_id.partner_id', store=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        related='project_id.account_id',
        store=True
    )
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', compute='_compute_sale_order', store=True)
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', compute='_compute_opportunity', store=True)

    date = fields.Date(string='Calculation Date', default=fields.Date.today)

    # Revenue Fields (opportunity_id/lead_value require crm module)
    lead_value = fields.Monetary(string='Lead Expected Revenue', compute='_compute_lead_value', store=True)
    so_total = fields.Monetary(string='Sales Order Total', compute='_compute_so_total', store=True)
    invoiced_amount = fields.Monetary(string='Invoiced Amount', compute='_compute_financials', store=True)
    paid_amount = fields.Monetary(string='Paid Amount', compute='_compute_financials', store=True)
    revenue_recognized = fields.Monetary(string='Revenue Recognized', compute='_compute_financials', store=True)

    # Cost Fields
    timesheet_cost = fields.Monetary(string='Timesheet Cost', compute='_compute_financials', store=True)
    expense_cost = fields.Monetary(string='Expense Cost', compute='_compute_financials', store=True)
    vendor_bill_cost = fields.Monetary(string='Vendor Bill Cost', compute='_compute_financials', store=True)
    other_cost = fields.Monetary(string='Other Costs', compute='_compute_financials', store=True)
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_totals', store=True)

    # Budget Fields
    budget_revenue = fields.Monetary(string='Budgeted Revenue', compute='_compute_budget', store=True)
    budget_cost = fields.Monetary(string='Budgeted Cost', compute='_compute_budget', store=True)
    budget_margin = fields.Monetary(string='Budgeted Margin', compute='_compute_budget', store=True)

    # Profitability Fields
    gross_margin = fields.Monetary(string='Gross Margin', compute='_compute_totals', store=True)
    margin_percentage = fields.Float(string='Margin %', compute='_compute_totals', store=True, digits=(16, 2))

    # Variance Fields
    revenue_variance = fields.Monetary(string='Revenue Variance', compute='_compute_variance', store=True)
    cost_variance = fields.Monetary(string='Cost Variance', compute='_compute_variance', store=True)
    margin_variance = fields.Monetary(string='Margin Variance', compute='_compute_variance', store=True)
    cost_variance_percentage = fields.Float(string='Cost Variance %', compute='_compute_variance', store=True)

    # Status Fields
    profitability_status = fields.Selection([
        ('excellent', 'Excellent (>30%)'),
        ('good', 'Good (20-30%)'),
        ('average', 'Average (10-20%)'),
        ('poor', 'Poor (0-10%)'),
        ('loss', 'Loss Making (<0%)')
    ], string='Status', compute='_compute_status', store=True)

    budget_status = fields.Selection([
        ('under', 'Under Budget'),
        ('on_track', 'On Budget'),
        ('over', 'Over Budget')
    ], string='Budget Status', compute='_compute_status', store=True)

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    # Additional KPIs
    hours_logged = fields.Float(string='Hours Logged', compute='_compute_hours', store=True)
    hours_budgeted = fields.Float(string='Hours Budgeted', compute='_compute_hours', store=True)
    billing_rate = fields.Monetary(string='Average Billing Rate', compute='_compute_rates', store=True)
    cost_rate = fields.Monetary(string='Average Cost Rate', compute='_compute_rates', store=True)

    @api.depends('project_id', 'project_id.sale_order_id')
    def _compute_sale_order(self):
        for record in self:
            sale_order_id = False
            if record.project_id:
                # 1. Manual link (project_profitability adds sale_order_id to project)
                if hasattr(record.project_id, 'sale_order_id') and record.project_id.sale_order_id:
                    sale_order_id = record.project_id.sale_order_id
                # 2. project_sale: sale_line_id on project
                elif hasattr(record.project_id, 'sale_line_id') and record.project_id.sale_line_id:
                    sale_order_id = record.project_id.sale_line_id.order_id
                # 3. project_sale: sale_line_id on tasks
                elif hasattr(self.env['project.task'], 'sale_line_id'):
                    sale_lines = record.project_id.task_ids.mapped('sale_line_id').filtered(lambda r: r)
                    if sale_lines:
                        sale_order_id = sale_lines[0].order_id
            record.sale_order_id = sale_order_id

    @api.depends('sale_order_id')
    def _compute_opportunity(self):
        for record in self:
            opportunity_id = False
            if record.sale_order_id and hasattr(record.sale_order_id, 'opportunity_id'):
                opportunity_id = record.sale_order_id.opportunity_id
            record.opportunity_id = opportunity_id

    @api.depends('opportunity_id')
    def _compute_lead_value(self):
        for record in self:
            record.lead_value = record.opportunity_id.expected_revenue if record.opportunity_id else 0.0

    @api.depends('sale_order_id')
    def _compute_so_total(self):
        for record in self:
            record.so_total = record.sale_order_id.amount_total if record.sale_order_id else 0.0

    @api.depends('analytic_account_id', 'date')
    def _compute_financials(self):
        for record in self:
            if not record.analytic_account_id:
                record.update({
                    'invoiced_amount': 0.0,
                    'paid_amount': 0.0,
                    'revenue_recognized': 0.0,
                    'timesheet_cost': 0.0,
                    'expense_cost': 0.0,
                    'vendor_bill_cost': 0.0,
                    'other_cost': 0.0,
                })
                continue

            # Get all analytic lines up to the calculation date
            analytic_lines = self.env['account.analytic.line'].search([
                ('account_id', '=', record.analytic_account_id.id),
                ('date', '<=', record.date)
            ])

            # Revenue (positive amounts)
            revenue_lines = analytic_lines.filtered(lambda l: l.amount > 0)
            record.revenue_recognized = sum(revenue_lines.mapped('amount'))

            # Timesheet costs (has employee_id)
            timesheet_lines = analytic_lines.filtered(
                lambda l: l.amount < 0 and getattr(l, 'employee_id', None)
            )
            record.timesheet_cost = abs(sum(timesheet_lines.mapped('amount')))

            # Expense costs (has expense_id - from hr.expense)
            expense_lines = analytic_lines.filtered(
                lambda l: l.amount < 0 and getattr(l, 'expense_id', None)
            )
            record.expense_cost = abs(sum(expense_lines.mapped('amount')))

            # Vendor bill costs (has move_line_id, not expense, not employee)
            vendor_lines = analytic_lines.filtered(
                lambda l: (
                    l.amount < 0 and
                    getattr(l, 'move_line_id', None) and
                    not getattr(l, 'expense_id', None) and
                    not getattr(l, 'employee_id', None)
                )
            )
            record.vendor_bill_cost = abs(sum(vendor_lines.mapped('amount')))

            # Other costs
            other_lines = analytic_lines.filtered(
                lambda l: (
                    l.amount < 0 and
                    not getattr(l, 'employee_id', None) and
                    not getattr(l, 'expense_id', None) and
                    not getattr(l, 'move_line_id', None)
                )
            )
            record.other_cost = abs(sum(other_lines.mapped('amount')))

            # Invoice amounts
            if record.project_id.partner_id:
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', record.project_id.partner_id.id),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_date', '<=', record.date)
                ])

                # Filter invoices related to this project (analytic_distribution: {account_id: percentage})
                account_id = record.analytic_account_id.id
                project_invoices = invoices.filtered(
                    lambda inv: any(
                        line.analytic_distribution and
                        isinstance(line.analytic_distribution, dict) and
                        (account_id in line.analytic_distribution or
                         str(account_id) in [str(k) for k in line.analytic_distribution.keys()])
                        for line in inv.invoice_line_ids
                    )
                )

                record.invoiced_amount = sum(project_invoices.mapped('amount_total'))
                record.paid_amount = sum(
                    inv.amount_total for inv in project_invoices
                    if inv.payment_state == 'paid'
                )

    @api.depends('revenue_recognized', 'timesheet_cost', 'expense_cost', 'vendor_bill_cost', 'other_cost')
    def _compute_totals(self):
        for record in self:
            record.total_cost = (
                record.timesheet_cost +
                record.expense_cost +
                record.vendor_bill_cost +
                record.other_cost
            )
            record.gross_margin = record.revenue_recognized - record.total_cost

            if record.revenue_recognized > 0:
                record.margin_percentage = (record.gross_margin / record.revenue_recognized) * 100
            else:
                record.margin_percentage = 0.0

    @api.depends('analytic_account_id')
    def _compute_budget(self):
        for record in self:
            if not record.analytic_account_id:
                record.update({
                    'budget_revenue': 0.0,
                    'budget_cost': 0.0,
                    'budget_margin': 0.0,
                })
                continue

            revenue_budget = 0.0
            cost_budget = 0.0

            # ── Odoo 18: account_budget module uses 'budget.line' + 'budget.analytic' ──
            # budget.line inherits analytic.plan.fields.mixin, so analytic account is
            # linked via auto_account_id (searches across all analytic plan columns).
            # budget_amount is always POSITIVE; revenue/expense distinction is via
            # budget_analytic_id.budget_type ('revenue' / 'expense' / 'both').
            if 'budget.line' in self.env:
                budget_lines = self.env['budget.line'].search([
                    ('auto_account_id', '=', record.analytic_account_id.id),
                    ('budget_analytic_id.state', 'not in', ['draft', 'canceled']),
                ])
                revenue_budget = sum(
                    bl.budget_amount
                    for bl in budget_lines
                    if bl.budget_analytic_id.budget_type in ('revenue', 'both')
                )
                cost_budget = sum(
                    bl.budget_amount
                    for bl in budget_lines
                    if bl.budget_analytic_id.budget_type in ('expense', 'both')
                )

            # ── Odoo 17 fallback: crossovered.budget.lines ──
            # planned_amount > 0 => revenue, planned_amount < 0 => expense
            elif 'crossovered.budget.lines' in self.env:
                budget_lines_v17 = self.env['crossovered.budget.lines'].search([
                    ('analytic_account_id', '=', record.analytic_account_id.id),
                ])
                revenue_budget = sum(
                    line.planned_amount for line in budget_lines_v17
                    if line.planned_amount > 0
                )
                cost_budget = abs(sum(
                    line.planned_amount for line in budget_lines_v17
                    if line.planned_amount < 0
                ))

            record.budget_revenue = revenue_budget
            record.budget_cost = cost_budget
            record.budget_margin = revenue_budget - cost_budget

    @api.depends('revenue_recognized', 'total_cost', 'budget_revenue', 'budget_cost')
    def _compute_variance(self):
        for record in self:
            record.revenue_variance = record.revenue_recognized - record.budget_revenue
            record.cost_variance = record.budget_cost - record.total_cost
            record.margin_variance = record.gross_margin - record.budget_margin

            if record.budget_cost > 0:
                record.cost_variance_percentage = (record.cost_variance / record.budget_cost) * 100
            else:
                record.cost_variance_percentage = 0.0

    @api.depends('margin_percentage', 'total_cost', 'budget_cost')
    def _compute_status(self):
        for record in self:
            # Profitability Status
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

            # Budget Status
            if record.budget_cost > 0:
                cost_ratio = record.total_cost / record.budget_cost
                if cost_ratio > 1.1:  # Over 110%
                    record.budget_status = 'over'
                elif cost_ratio < 0.9:  # Under 90%
                    record.budget_status = 'under'
                else:
                    record.budget_status = 'on_track'
            else:
                record.budget_status = 'on_track'

    @api.depends('analytic_account_id', 'date')
    def _compute_hours(self):
        for record in self:
            if not record.analytic_account_id:
                record.hours_logged = 0.0
                record.hours_budgeted = 0.0
                continue

            # Hours logged from timesheets (employee_id exists only with hr_timesheet)
            AnalyticLine = self.env['account.analytic.line']
            domain = [
                ('account_id', '=', record.analytic_account_id.id),
                ('date', '<=', record.date),
            ]
            if 'employee_id' in AnalyticLine._fields:
                domain.append(('employee_id', '!=', False))
            timesheet_lines = AnalyticLine.search(domain)
            record.hours_logged = sum(timesheet_lines.mapped('unit_amount'))

            # Budgeted hours (project may have allocated_hours from project_enterprise/sale)
            record.hours_budgeted = getattr(record.project_id, 'allocated_hours', 0.0) or 0.0

    @api.depends('revenue_recognized', 'total_cost', 'hours_logged')
    def _compute_rates(self):
        for record in self:
            if record.hours_logged > 0:
                record.billing_rate = record.revenue_recognized / record.hours_logged
                record.cost_rate = record.total_cost / record.hours_logged
            else:
                record.billing_rate = 0.0
                record.cost_rate = 0.0

    def action_refresh_calculations(self):
        """Manually refresh all calculations"""
        self.invalidate_recordset()
        self._compute_sale_order()
        self._compute_opportunity()
        self._compute_lead_value()
        self._compute_so_total()
        self._compute_financials()
        self._compute_totals()
        self._compute_budget()
        self._compute_variance()
        self._compute_status()
        self._compute_hours()
        self._compute_rates()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Profitability calculations refreshed successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def create_snapshot_for_all_projects(self):
        """Create profitability snapshot for all active projects"""
        projects = self.env['project.project'].search([
            ('active', '=', True),
            ('account_id', '!=', False)
        ])

        for project in projects:
            self.create({
                'project_id': project.id,
                'date': fields.Date.today(),
            })

        return True

    @api.model
    def scheduled_profitability_calculation(self):
        """Scheduled action to calculate profitability daily/weekly"""
        return self.create_snapshot_for_all_projects()

    @api.model
    def create_demo_data(self):
        """Create demo data following full Odoo 18 flow:
        Lead → Opportunity → Sales Order → Project → Budget
        """
        from datetime import timedelta

        company = self.env.company
        today = fields.Date.today()
        SaleOrder = self.env['sale.order']
        CrmLead = self.env['crm.lead']

        # Skip if demo data already exists
        existing = self.env['project.project'].search([
            ('name', '=', 'Website Redesign'),
            ('account_id', '!=', False)
        ], limit=1)
        if existing:
            return True  # Demo data already loaded

        # Get analytic plan (analytic accounting must be enabled)
        plan = self.env['account.analytic.plan'].search([], limit=1)
        if not plan:
            return False  # Analytic accounting not configured

        # Get or create a service product for SO lines
        product = self.env['product.product'].search([
            ('type', '=', 'service'),
            ('company_id', 'in', [False, company.id])
        ], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Consulting Service',
                'type': 'service',
                'list_price': 100.0,
                'company_id': company.id,
            })

        # Demo: (project_name, partner_name, so_total, timesheet_cost, other_cost, budget_cost)
        demo_projects_data = [
            ('Website Redesign', 'Azure Interior', 45000.0, 12000.0, 3500.0, 18000.0),
            ('Mobile App Development', 'Deco Addict', 78000.0, 28000.0, 8500.0, 40000.0),
            ('ERP Implementation', 'Ready Mat', 125000.0, 45000.0, 12000.0, 60000.0),
            ('Marketing Campaign Q1', 'The Jackson Group', 32000.0, 8000.0, 4200.0, 15000.0),
            ('Support Contract Renewal', 'Chesterfield', 18000.0, 4500.0, 1200.0, 6000.0),
        ]

        budget_from = today - timedelta(days=90)
        budget_to = today + timedelta(days=90)

        for name, partner_name, so_total, timesheet_cost, other_cost, budget_cost in demo_projects_data:
            # 1. Get or create partner
            partner = self.env['res.partner'].search([
                ('name', 'ilike', partner_name),
                ('company_id', 'in', [False, company.id])
            ], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': partner_name,
                    'company_id': company.id,
                })

            # 2. Create CRM Lead (type='lead' - initial stage)
            lead = CrmLead.create({
                'name': f'{name} - Lead',
                'partner_id': partner.id,
                'expected_revenue': so_total,
                'type': 'lead',
                'company_id': company.id,
            })

            # 3. Convert Lead to Opportunity (Odoo 18 workflow)
            lead.write({'type': 'opportunity', 'expected_revenue': so_total})
            opportunity = lead

            # 4. Create Sales Order linked to Opportunity
            so_vals = {
                'partner_id': partner.id,
                'company_id': company.id,
            }
            if 'opportunity_id' in SaleOrder._fields:
                so_vals['opportunity_id'] = opportunity.id
            so = SaleOrder.create(so_vals)
            self.env['sale.order.line'].create({
                'order_id': so.id,
                'product_id': product.id,
                'name': f'{name} - Service',
                'product_uom_qty': 1,
                'price_unit': so_total,
            })
            so.action_confirm()

            # 5. Create analytic account and project
            analytic_account = self.env['account.analytic.account'].create({
                'name': f'{name} - Analytic',
                'plan_id': plan.id,
                'company_id': company.id,
                'partner_id': partner.id,
            })

            project_vals = {
                'name': name,
                'partner_id': partner.id,
                'account_id': analytic_account.id,
                'company_id': company.id,
            }
            if hasattr(self.env['project.project'], 'sale_order_id'):
                project_vals['sale_order_id'] = so.id
            project = self.env['project.project'].create(project_vals)

            # 6. Create analytic lines (Revenue, Timesheet, Other costs)
            self.env['account.analytic.line'].create({
                'name': f'Revenue - {name}',
                'account_id': analytic_account.id,
                'date': today - timedelta(days=30),
                'amount': so_total,
                'unit_amount': 0,
                'company_id': company.id,
            })

            line_vals = {
                'name': f'Timesheet - {name}',
                'account_id': analytic_account.id,
                'date': today - timedelta(days=15),
                'amount': -timesheet_cost,
                'unit_amount': timesheet_cost / 50 if timesheet_cost else 0,
                'company_id': company.id,
            }
            if 'employee_id' in self.env['account.analytic.line']._fields:
                employee = self.env['hr.employee'].search([('company_id', '=', company.id)], limit=1)
                if employee:
                    line_vals['employee_id'] = employee.id
            self.env['account.analytic.line'].create(line_vals)

            self.env['account.analytic.line'].create({
                'name': f'Other costs - {name}',
                'account_id': analytic_account.id,
                'date': today - timedelta(days=7),
                'amount': -other_cost,
                'unit_amount': 0,
                'company_id': company.id,
            })

            # 7. Create Budget
            # ── Odoo 18: budget.analytic + budget.line ──
            # budget_amount is always positive; budget_type distinguishes revenue vs expense.
            # auto_account_id is a computed magic field on budget.line that links to the
            # analytic account via the appropriate analytic plan column.
            if 'budget.analytic' in self.env:
                try:
                    # Revenue Budget
                    budget_revenue = self.env['budget.analytic'].create({
                        'name': f'{name} - Revenue Budget',
                        'company_id': company.id,
                        'date_from': budget_from,
                        'date_to': budget_to,
                        'budget_type': 'revenue',
                    })
                    self.env['budget.line'].create({
                        'budget_analytic_id': budget_revenue.id,
                        'budget_amount': so_total,
                        'auto_account_id': analytic_account.id,
                    })
                    budget_revenue.action_budget_confirm()

                    # Expense Budget
                    budget_expense = self.env['budget.analytic'].create({
                        'name': f'{name} - Expense Budget',
                        'company_id': company.id,
                        'date_from': budget_from,
                        'date_to': budget_to,
                        'budget_type': 'expense',
                    })
                    self.env['budget.line'].create({
                        'budget_analytic_id': budget_expense.id,
                        'budget_amount': budget_cost,
                        'auto_account_id': analytic_account.id,
                    })
                    budget_expense.action_budget_confirm()

                except Exception:
                    pass  # Skip if budget structure differs

            # ── Odoo 17 fallback: crossovered.budget + crossovered.budget.lines ──
            # planned_amount > 0 => revenue budget, planned_amount < 0 => expense budget
            elif 'crossovered.budget' in self.env:
                try:
                    CrossoveredBudget = self.env['crossovered.budget']
                    CrossoveredBudgetLine = self.env['crossovered.budget.lines']

                    budget_vals = {
                        'name': f'{name} - Revenue Budget',
                        'company_id': company.id,
                    }
                    if 'date_from' in CrossoveredBudget._fields:
                        budget_vals['date_from'] = budget_from
                    if 'date_to' in CrossoveredBudget._fields:
                        budget_vals['date_to'] = budget_to

                    budget_revenue = CrossoveredBudget.create(budget_vals)
                    line_vals = {
                        'crossovered_budget_id': budget_revenue.id,
                        'analytic_account_id': analytic_account.id,
                        'planned_amount': so_total,
                    }
                    for date_field in ('date_from', 'date_to', 'start_date', 'end_date'):
                        if date_field in CrossoveredBudgetLine._fields:
                            line_vals[date_field] = (
                                budget_from if 'from' in date_field or 'start' in date_field
                                else budget_to
                            )
                    CrossoveredBudgetLine.create(line_vals)
                    for method in ('action_budget_open', 'action_budget_confirm', 'action_confirm'):
                        if hasattr(budget_revenue, method):
                            getattr(budget_revenue, method)()
                            break

                    budget_vals['name'] = f'{name} - Expense Budget'
                    budget_expense = CrossoveredBudget.create(budget_vals)
                    expense_line_vals = dict(line_vals)
                    expense_line_vals['crossovered_budget_id'] = budget_expense.id
                    expense_line_vals['planned_amount'] = -budget_cost
                    CrossoveredBudgetLine.create(expense_line_vals)
                    for method in ('action_budget_open', 'action_budget_confirm', 'action_confirm'):
                        if hasattr(budget_expense, method):
                            getattr(budget_expense, method)()
                            break

                except Exception:
                    pass  # Skip if structure differs

            # 8. Create profitability snapshot
            self.create({
                'project_id': project.id,
                'date': today,
            })

        return True
