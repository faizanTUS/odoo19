# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class SalePriceHistory(models.Model):
    _name = 'sale.price.history'
    _description = 'Sale Price History'
    _order = 'date desc'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    order_id = fields.Many2one('sale.order', string='Sales Order')
    price = fields.Float(string='Sale Price', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sale', 'Confirmed'),
        ('done', 'Locked')
    ], string='Order State', related='order_id.state', store=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_price_history_ids = fields.One2many(
        'sale.price.history',
        'product_id',
        string='Sales Price History',
        compute='_compute_sale_price_history'
    )

    @api.depends('product_variant_ids')
    def _compute_sale_price_history(self):
        limit = int(self.env['ir.config_parameter'].sudo().get_param('sale_price_history.item_limit', 10))
        filter_confirmed = self.env['ir.config_parameter'].sudo().get_param('sale_price_history.filter_confirmed', 'False') == 'True'
        filter_sent = self.env['ir.config_parameter'].sudo().get_param('sale_price_history.filter_sent', 'False') == 'True'
        filter_draft = self.env['ir.config_parameter'].sudo().get_param('sale_price_history.filter_draft', 'False') == 'True'

        for record in self:
            domain = [('product_id', 'in', record.product_variant_ids.ids)]
            if filter_sent:
                domain.append(('state', '=','sent'))
            elif filter_draft:
                domain.append(('state', '=', 'draft'))
            elif filter_confirmed:
                domain.append(('state', '=', 'sale'))

            _logger.info(f"DOMAIN: {domain}")
            record.sale_price_history_ids = self.env['sale.price.history'].search(domain, limit=limit)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):

        line = super(SaleOrderLine, self).create(vals)
        line._create_sale_price_history()

        return line

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if any(key in vals for key in ['price_unit', 'product_id']):
            for line in self:
                _logger.info(f"Order state during write: {line.order_id.state}")
                line._create_sale_price_history()

        return res

    def unlink(self):
        for line in self:
            self.env['sale.price.history'].search([
                ('product_id', '=', line.product_id.id),
                ('order_id', '=', line.order_id.id),
            ]).unlink()

        return super(SaleOrderLine, self).unlink()

    def _create_sale_price_history(self):
        for line in self:
            if line.product_id and line.order_id:
                existing_history = self.env['sale.price.history'].search([
                    ('product_id', '=', line.product_id.id),
                    ('order_id', '=', line.order_id.id),
                ])
                existing_history.unlink()


                history = self.env['sale.price.history'].create({
                    'product_id': line.product_id.id,
                    'order_id': line.order_id.id,
                    'price': line.price_unit,
                    'state': line.order_id.state,
                })