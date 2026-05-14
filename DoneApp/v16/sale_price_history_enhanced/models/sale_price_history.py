# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models


class SalePriceHistory(models.Model):
    _name = 'sale.price.history'
    _description = 'Sale Price History'
    _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    order_id = fields.Many2one('sale.order', string='Sales Order')
    price = fields.Float(string='Sale Price', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', string='Changed By',
        default=lambda self: self.env.user)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('sale', 'Confirmed'),
            ('done', 'Locked'),
        ],
        string='Order State', related='order_id.state', store=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_price_history_ids = fields.One2many(
        'sale.price.history',
        'product_id',
        string='Sales Price History',
        compute='_compute_sale_price_history',
    )

    @api.depends('product_variant_ids')
    def _compute_sale_price_history(self):
        params = self.env['ir.config_parameter'].sudo()
        limit = int(params.get_param('sale_price_history.item_limit', 10))
        state_filter = False
        if params.get_param('sale_price_history.filter_sent') == 'True':
            state_filter = 'sent'
        elif params.get_param('sale_price_history.filter_draft') == 'True':
            state_filter = 'draft'
        elif params.get_param('sale_price_history.filter_confirmed') == 'True':
            state_filter = 'sale'

        history_model = self.env['sale.price.history']
        for record in self:
            domain = [('product_id', 'in', record.product_variant_ids.ids)]
            if state_filter:
                domain.append(('state', '=', state_filter))
            record.sale_price_history_ids = history_model.search(
                domain, limit=limit)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._create_sale_price_history()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if {'price_unit', 'product_id'} & vals.keys():
            self._create_sale_price_history()
        return res

    def unlink(self):
        product_ids = self.product_id.ids
        order_ids = self.order_id.ids
        if product_ids and order_ids:
            pairs = {(line.product_id.id, line.order_id.id) for line in self}
            self.env['sale.price.history'].search([
                ('product_id', 'in', product_ids),
                ('order_id', 'in', order_ids),
            ]).filtered(
                lambda h: (h.product_id.id, h.order_id.id) in pairs
            ).unlink()
        return super().unlink()

    def _create_sale_price_history(self):
        pair_to_price = {}
        for line in self:
            if line.product_id and line.order_id:
                pair_to_price[(line.product_id.id, line.order_id.id)] = \
                    line.price_unit
        if not pair_to_price:
            return
        history_model = self.env['sale.price.history']
        history_model.search([
            ('product_id', 'in', [p for p, _ in pair_to_price]),
            ('order_id', 'in', [o for _, o in pair_to_price]),
        ]).filtered(
            lambda h: (h.product_id.id, h.order_id.id) in pair_to_price
        ).unlink()
        history_model.create([
            {
                'product_id': product_id,
                'order_id': order_id,
                'price': price,
            }
            for (product_id, order_id), price in pair_to_price.items()
        ])
