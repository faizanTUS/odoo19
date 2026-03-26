# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_out_of_stock_restriction_enabled = fields.Boolean(
        string='Enable Out of Stock Product Restriction',
        config_parameter='sale_out_of_stock_restriction.enabled',
        help='When enabled, confirming a sales order is blocked if a storable product line '
             'orders more than the available quantity (based on the option below).',
    )
    sale_out_of_stock_restriction_base = fields.Selection(
        selection=[
            ('on_hand', 'Quantity on Hand'),
            ('forecast', 'Forecast Quantity'),
        ],
        string='Restriction Based On',
        default='on_hand',
        help='Use physical on-hand quantity or forecasted quantity (including planned moves) '
             'when comparing to the ordered quantity.',
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env['ir.config_parameter'].sudo()
        base = icp.get_param('sale_out_of_stock_restriction.base', 'on_hand')
        if base not in ('on_hand', 'forecast'):
            base = 'on_hand'
        res['sale_out_of_stock_restriction_base'] = base
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_out_of_stock_restriction.base',
            self.sale_out_of_stock_restriction_base or 'on_hand',
        )
