# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseQuickAddProduct(models.TransientModel):
    _name = 'purchase.quick.add.product'
    _description = 'Quick Add Multiple Products to Purchase Order'

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        required=True,
        ondelete='cascade',
    )

    product_line_ids = fields.One2many(
        'purchase.quick.add.product.line',
        'wizard_id',
        string='Products to Add',
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseQuickAddProduct, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['purchase_order_id'] = active_id
        return res

    def action_add_products(self):
        self.ensure_one()
        order = self.purchase_order_id

        if not order.partner_id:
            raise UserError(_("You must first select a Vendor for the Purchase Order."))

        for line in self.product_line_ids:
            if line.quantity <= 0:
                continue

            vals = {
                'order_id': order.id,
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'product_uom_id': line.product_id.uom_id.id,
                'price_unit': line.price_unit,
                'name': line.product_id.name,
                'date_planned': order.date_order or fields.Date.today(),
                'tax_ids': [(6, 0, line.product_id.supplier_taxes_id.filtered(
                    lambda t: t.company_id.id == order.company_id.id).ids)],
            }

            self.env['purchase.order.line'].create(vals)

        return {'type': 'ir.actions.act_window_close'}

    def action_open_multi_product_select(self):
        """Open multi-select product list to add many lines at once"""
        self.ensure_one()
        return {
            'name': _('Select Multiple Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'list',
            'views': [(self.env.ref('purchase_quick_add_products.view_product_tree_multi_select').id, 'list')],
            'domain': [('purchase_ok', '=', True)],
            'context': {
                'wizard_id': self.id,
                'create': False,
                'edit': False,
            },
            'target': 'new',
        }


class PurchaseQuickAddProductLine(models.TransientModel):
    _name = 'purchase.quick.add.product.line'
    _description = 'Quick Add Product Line'

    wizard_id = fields.Many2one(
        'purchase.quick.add.product',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )

    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )

    price_unit = fields.Float(
        string='Unit Price',
        compute='_compute_price_unit',
        store=True,
        readonly=False,
    )

    @api.depends('product_id', 'quantity', 'wizard_id.purchase_order_id.partner_id')
    def _compute_price_unit(self):
        for line in self:
            price = 0.0
            product = line.product_id
            order = line.wizard_id.purchase_order_id

            if product:
                if order.partner_id:
                    seller = product._select_seller(
                        partner_id=order.partner_id,
                        quantity=line.quantity,
                        date=order.date_order or fields.Date.today(),
                        uom_id=line.product_id.uom_id,
                    )
                    if seller:
                        price = seller.price
                        if seller.currency_id and seller.currency_id != order.currency_id:
                            price = seller.currency_id._convert(
                                price,
                                order.currency_id,
                                order.company_id,
                                order.date_order or fields.Date.today(),
                            )

                if not price:
                    price = product.standard_price or 0.0

            line.price_unit = price


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_add_selected_to_quick_wizard(self):
        """Called from multi-select list - add selected products as lines"""
        wizard_id = self.env.context.get('wizard_id')
        if not wizard_id:
            raise UserError(_("Wizard context missing."))

        wizard = self.env['purchase.quick.add.product'].browse(wizard_id)
        if not wizard.exists():
            raise UserError(_("Wizard record no longer exists."))

        order = wizard.purchase_order_id
        if not order.partner_id:
            raise UserError(_("Please select a vendor on the Purchase Order first."))

        today = fields.Date.context_today(self)

        # Collect existing lines from old wizard
        existing_lines = []
        for line in wizard.product_line_ids:
            existing_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
            }))

        # Add newly selected products
        existing_products = wizard.product_line_ids.mapped('product_id')
        for product in self:
            if product in existing_products:
                continue
            seller = product._select_seller(
                partner_id=order.partner_id,
                quantity=1.0,
                date=order.date_order or today,
                uom_id=product.uom_id,
            )
            price = seller.price if seller else product.standard_price or 0.0
            if seller and seller.currency_id != order.currency_id:
                price = seller.currency_id._convert(
                    price, order.currency_id, order.company_id,
                    order.date_order or today
                )
            existing_lines.append((0, 0, {
                'product_id': product.id,
                'quantity': 1.0,
                'price_unit': price,
            }))

        # Delete old wizard, open fresh one with all lines via default_
        # Fresh wizard via default_ context always opens in edit mode
        wizard.unlink()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.quick.add.product',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_purchase_order_id': order.id,
                'default_product_line_ids': existing_lines,
            },
        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_quick_add_product(self):
        self.ensure_one()
        return {
            'name': _('Quick Add Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.quick.add.product',
            'view_mode': 'form',
            'view_id': self.env.ref('purchase_quick_add_products.view_purchase_quick_add_product_form').id,
            'context': {'default_purchase_order_id': self.id},
            'target': 'new',
        }