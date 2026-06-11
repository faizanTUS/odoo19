# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        user = self.env.user

        if user.has_group('tus_warehouse_stock_restrictions.group_restrict_button'):
            arch = res.get('arch', '')

            if view_type == 'tree':
                arch = arch.replace('<tree', '<tree create="0" edit="0" delete="0"')

            elif view_type == 'form':
                arch = arch.replace('<form', '<form create="0" edit="0" delete="0"')

            res['arch'] = arch

        return res
