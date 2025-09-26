# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_sale_order_id = fields.Many2one(
        'sale.order',
        string="Last Sale Order",
        compute='_compute_last_sale_order',
        store=True
    )
    last_sale_order_date = fields.Datetime(
        string="Last Sale Order Date",
        compute='_compute_last_sale_order',
        store=True
    )
    last_purchase_order_id = fields.Many2one(
        'purchase.order',
        string="Last Purchase Order",
        compute='_compute_last_purchase_order',
        store=True
    )
    last_purchase_order_date = fields.Datetime(
        string="Last Purchase Order Date",
        compute='_compute_last_purchase_order',
        store=True
    )

    purchase_order_ids = fields.One2many('purchase.order', 'partner_id', 'Purchase Order')


    @api.depends('sale_order_ids.date_order')
    def _compute_last_sale_order(self):
        for partner in self:
            last_sale_order = self.env['sale.order'].search(
                [('partner_id', '=', partner.id), ('state', '=', 'sale')],
                order='date_order desc',
                limit=1
            )
            # if last_sale_order.state == 'sale':
            partner.last_sale_order_id = last_sale_order.id if last_sale_order else False
            partner.last_sale_order_date = last_sale_order.date_order if last_sale_order else False


    @api.depends('purchase_order_ids.date_order','purchase_order_ids.state')
    def _compute_last_purchase_order(self):
        for partner in self:
            last_purchase_order = self.env['purchase.order'].search(
                [('partner_id', '=', partner.id), ('state', '=', 'purchase')],
                order='date_order desc',
                limit=1
            )
            # if last_purchase_order.state == 'purchase':
            partner.last_purchase_order_id = last_purchase_order.id if last_purchase_order else False
            partner.last_purchase_order_date = last_purchase_order.date_approve if last_purchase_order else False
            # partner.last_purchase_order_date = last_purchase_order.date_order if last_purchase_order else False
