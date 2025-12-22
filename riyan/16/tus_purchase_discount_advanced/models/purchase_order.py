# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, _, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_open_discount_wizard(self):
        self.ensure_one()
        return {
            'name': _("Discount"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.discount',
            'view_mode': 'form',
            'target': 'new',
        }

    show_discount_feature = fields.Boolean(
        string="Show Discount Feature", compute="_compute_show_discount_feature", store=False
    )

    @api.depends()
    def _compute_show_discount_feature(self):
        param = self.env['ir.config_parameter'].sudo().get_param(
            'tus_purchase_discount_advanced.purchase_discount', default='False'
        )
        for rec in self:
            rec.show_discount_feature = param == 'True'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float()

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        res = super()._compute_amount()
        return res

    def _prepare_account_move_line(self, move=False):
        """Method for updating the discount amount in account move line"""
        res = super()._prepare_account_move_line(move=False)
        res.update({'discount': self.discount})
        return res

    def _get_discounted_price(self):
        """
        Compute the price per unit after applying the discount
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    def _convert_to_tax_base_line_dict(self):
        """The existing _convert_to_tax_base_line_dict method to
        compute the price_unit based on discount. Convert the current record
        to a dictionary in order to use the generic taxes computation method
        defined on account.tax.
        :return: A python dictionary.
        """
        self.ensure_one()
        res = super()._convert_to_tax_base_line_dict()
        price_unit = self._get_discounted_price()
        res.update({'price_unit': price_unit})
        return res
