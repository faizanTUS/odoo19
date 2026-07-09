# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Manual link to SO (used when project_sale is not installed; project_sale may add its own)
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        help='Link to sales order for profitability tracking (Lead → SO → Project flow)'
    )

    profitability_ids = fields.One2many(
        'project.profitability',
        'project_id',
        string='Profitability History'
    )

    current_profitability_id = fields.Many2one(
        'project.profitability',
        string='Current Profitability',
        compute='_compute_current_profitability'
    )

    # Quick access fields
    current_margin = fields.Monetary(
        string='Current Margin',
        related='current_profitability_id.gross_margin'
    )
    current_margin_percentage = fields.Float(
        string='Current Margin %',
        related='current_profitability_id.margin_percentage'
    )
    current_revenue = fields.Monetary(
        string='Current Revenue',
        related='current_profitability_id.revenue_recognized'
    )
    current_cost = fields.Monetary(
        string='Current Cost',
        related='current_profitability_id.total_cost'
    )
    profitability_status = fields.Selection(
        related='current_profitability_id.profitability_status',
        string='Profitability Status'
    )
    budget_status = fields.Selection(
        related='current_profitability_id.budget_status',
        string='Budget Status'
    )

    @api.depends('profitability_ids')
    def _compute_current_profitability(self):
        for project in self:
            latest = project.profitability_ids.sorted('date', reverse=True)
            project.current_profitability_id = latest[0] if latest else False

    def action_view_profitability(self):
        """Open profitability view for this project"""
        self.ensure_one()
        return {
            'name': 'Project Profitability',
            'type': 'ir.actions.act_window',
            'res_model': 'project.profitability',
            'view_mode': 'list,form,graph,pivot',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_calculate_profitability(self):
        """Calculate current profitability snapshot"""
        self.ensure_one()
        profitability = self.env['project.profitability'].create({
            'project_id': self.id,
            'date': fields.Date.today(),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.profitability',
            'res_id': profitability.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def get_profitability_data(self):
        """Return profitability data as dictionary (for API/widgets)"""
        self.ensure_one()
        if not self.current_profitability_id:
            return {}

        prof = self.current_profitability_id
        return {
            'project_name': self.name,
            'customer': self.partner_id.name if self.partner_id else '',
            'lead_value': prof.lead_value,
            'so_total': prof.so_total,
            'lead_name': prof.opportunity_id.name if prof.opportunity_id else '',
            'so_reference': prof.sale_order_id.name if prof.sale_order_id else '',
            'lead_id': prof.opportunity_id.id if prof.opportunity_id else None,
            'so_id': prof.sale_order_id.id if prof.sale_order_id else None,
            'revenue': {
                'invoiced': prof.invoiced_amount,
                'paid': prof.paid_amount,
                'recognized': prof.revenue_recognized,
            },
            'costs': {
                'timesheet': prof.timesheet_cost,
                'expense': prof.expense_cost,
                'vendor_bills': prof.vendor_bill_cost,
                'other': prof.other_cost,
                'total': prof.total_cost,
            },
            'budget': {
                'revenue': prof.budget_revenue,
                'cost': prof.budget_cost,
                'margin': prof.budget_margin,
            },
            'profitability': {
                'margin': prof.gross_margin,
                'margin_percentage': prof.margin_percentage,
                'status': prof.profitability_status,
            },
            'progress': (prof.revenue_recognized / prof.so_total * 100) if prof.so_total else 0.0,
            'variance': {
                'revenue': prof.revenue_variance,
                'cost': prof.cost_variance,
                'margin': prof.margin_variance,
                'cost_percentage': prof.cost_variance_percentage,
            },
            'kpis': {
                'hours_logged': prof.hours_logged,
                'hours_budgeted': prof.hours_budgeted,
                'billing_rate': prof.billing_rate,
                'cost_rate': prof.cost_rate,
            }
        }
