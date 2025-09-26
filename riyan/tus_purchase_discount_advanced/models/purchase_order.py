# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, _


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
