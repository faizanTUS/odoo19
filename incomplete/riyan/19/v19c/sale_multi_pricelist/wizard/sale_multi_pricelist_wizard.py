# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SaleMultiPricelistWizardLine(models.TransientModel):
    _name = 'sale.multi.pricelist.wizard.line'
    _description = 'Multi Pricelist Wizard Line'

    wizard_id = fields.Many2one(
        comodel_name='sale.multi.pricelist.wizard',
        required=True,
        ondelete='cascade',
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        required=True,
        readonly=True,
    )
    price = fields.Float(
        string="Price",
        digits='Product Price',
        readonly=True,
    )

    min_qty = fields.Float(
        string="Min. Quantity",
        readonly=True,
    )

    discount_pr = fields.Char(
        string="Discount",
        readonly=True,
    )

    discount_amount = fields.Float(
        string="Discount Amount",
        digits='Product Price',
        readonly=True,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='wizard_id.currency_id',
        readonly=True,
    )


class SaleMultiPricelistWizard(models.TransientModel):
    _name = 'sale.multi.pricelist.wizard'
    _description = 'Multi Pricelist on Order'

    order_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string="Order Line",
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        related='order_line_id.product_id',
        readonly=True,
    )
    product_uom_qty = fields.Float(
        related='order_line_id.product_uom_qty',
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        related='order_line_id.product_uom_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='order_line_id.currency_id',
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name='sale.multi.pricelist.wizard.line',
        inverse_name='wizard_id',
        string="Pricelist Prices",
        readonly=True,
    )
    available_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        compute='_compute_available_pricelist_ids',
        string="Available Pricelists",
        help="Pricelists shown in the comparison table.",
    )
    selected_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Apply Pricelist",
        help="Select the pricelist to apply to this order line.",
        domain="[('id', 'in', available_pricelist_ids)]",
    )

    @api.depends('line_ids.pricelist_id')
    def _compute_available_pricelist_ids(self):
        for wiz in self:
            wiz.available_pricelist_ids = wiz.line_ids.pricelist_id

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_line_id = res.get('order_line_id') or self.env.context.get('default_order_line_id')
        if not order_line_id:
            return res
        order_line = self.env['sale.order.line'].browse(order_line_id)
        if not order_line.exists() or not order_line.product_id or order_line.display_type:
            return res

        # Get base sales price and convert to order currency if needed
        sales_price = order_line.product_id.lst_price
        if order_line.currency_id != order_line.product_id.currency_id:
            sales_price = order_line.product_id.currency_id._convert(
                sales_price,
                order_line.currency_id,
                order_line.company_id,
                order_line._get_order_date(),
            )

        # Build pricelist lines with computed prices
        pricelists = self.env['product.pricelist'].search([
            ('active', '=', True),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', order_line.company_id.id),
        ])
        lines_vals = []
        for pricelist in pricelists:
            try:
                price = pricelist._get_product_price(
                    order_line.product_id,
                    order_line.product_uom_qty or 1.0,
                    currency=order_line.currency_id,
                    uom=order_line.product_uom_id,
                    date=order_line._get_order_date(),
                )
            except Exception:
                price = 0.0
            # Search priority: product-specific > product template > category > global
            item = (
                # 1. Exact product match
                self.env['product.pricelist.item'].search([
                        ('pricelist_id', '=', pricelist.id),
                        ('applied_on', '=', '0_product_variant'),
                        ('product_id', '=', order_line.product_id.id),
                ], limit=1, order='min_quantity desc')
                 # 2. Product template match
                or self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist.id),
                    ('applied_on', '=', '1_product'),
                    ('product_tmpl_id', '=', order_line.product_id.product_tmpl_id.id),
                ], limit=1, order='min_quantity desc')
                # 3. Category match
                or self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist.id),
                    ('applied_on', '=', '2_product_category'),
                    ('categ_id', 'in', order_line.product_id.categ_id.search([
                    ('id', 'parent_of', order_line.product_id.categ_id.id)
                ]).ids),
                ], limit=1, order='min_quantity desc')
                # 4. Global fallback
                or self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist.id),
                    ('applied_on', '=', '3_global'),
                ], limit=1, order='min_quantity desc')
            )

            min_qty = item.min_quantity if item else 0.0
            discount = item.price if item else ''
            discount_amount = sales_price - price

            lines_vals.append((0, 0, {
                'pricelist_id': pricelist.id,
                'price': price,
                'min_qty': min_qty,
                'discount_pr': discount,
                'discount_amount': discount_amount,
            }))
        res['line_ids'] = lines_vals

        # Pre-select current line pricelist or order pricelist
        effective = order_line._get_pricelist_for_line()
        if effective and effective in pricelists:
            res['selected_pricelist_id'] = effective.id
        return res

    def action_apply(self):
        """Apply the selected pricelist to the order line and close the wizard."""
        self.ensure_one()
        if not self.order_line_id.exists():
            raise UserError(_("The order line no longer exists."))
        if self.order_line_id.qty_invoiced > 0:
            raise UserError(_("You cannot change the pricelist on a line that has already been invoiced."))
        self.order_line_id.pricelist_id = self.selected_pricelist_id

        # Force price recomputation so unit price and discount update immediately
        self.order_line_id.with_context(force_price_recomputation=True)._compute_price_unit()
        self.order_line_id._compute_discount()
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
