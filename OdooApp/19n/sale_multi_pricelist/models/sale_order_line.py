# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        help="When set, this pricelist is used for this line instead of the order's pricelist. "
             "Leave empty to use the order pricelist.",
        domain="[('active', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
    effective_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_effective_pricelist_id',
        store=True,
        help="Pricelist used for this line (line pricelist or order pricelist).",
    )

    @api.depends('pricelist_id', 'order_id.pricelist_id')
    def _compute_effective_pricelist_id(self):
        for line in self:
            line.effective_pricelist_id = line._get_pricelist_for_line()

    def _get_pricelist_for_line(self):
        """Return the pricelist to use for this line: line pricelist or order pricelist."""
        self.ensure_one()
        return self.pricelist_id or self.order_id.pricelist_id

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty', 'pricelist_id', 'order_id.pricelist_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            pricelist = line._get_pricelist_for_line()
            if not line.product_id or line.display_type or not pricelist:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = pricelist._get_product_rule(
                    line.product_id,
                    quantity=line.product_uom_qty or 1.0,
                    uom=line.product_uom_id,
                    date=line._get_order_date(),
                )

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty', 'pricelist_id')
    def _compute_price_unit(self):
        """Recompute price when line pricelist changes."""
        return super()._compute_price_unit()

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty', 'pricelist_id', 'order_id.pricelist_id')
    def _compute_discount(self):
        """Recompute discount when line pricelist changes; use effective pricelist for the check."""
        discount_enabled = self.env['product.pricelist.item']._is_discount_feature_enabled()
        for line in self:
            if not line.product_id or line.display_type:
                line.discount = 0.0

            effective_pricelist = line._get_pricelist_for_line()
            if not (effective_pricelist and discount_enabled):
                continue

            if line.combo_item_id:
                line.discount = line._get_linked_line().discount
                continue

            line.discount = 0.0

            if not line.pricelist_item_id._show_discount():
                continue

            line = line.with_company(line.company_id)
            pricelist_price = line._get_pricelist_price()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    line.discount = discount

    def action_open_multi_pricelist_wizard(self):
        """Open the Multi Pricelist comparison wizard for this line."""
        self.ensure_one()
        if not self.product_id or self.display_type:
            return
        return {
            'name': self.env.context.get('wizard_title', 'Multi Pricelist on Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.multi.pricelist.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_line_id': self.id,
                'default_product_id': self.product_id.id,
                'default_product_uom_qty': self.product_uom_qty,
                'default_product_uom_id': self.product_uom_id.id,
            },
        }


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_display_name(self):
        # In wizard context, show name only without currency
        if self.env.context.get('hide_currency_in_name'):
            for pl in self:
                pl.display_name = pl.name
        else:
            return super()._compute_display_name()