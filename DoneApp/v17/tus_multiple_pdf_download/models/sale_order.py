# See LICENSE file for full copyright and licensing details.
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)

        sale_order_action = self.env.ref('tus_multiple_pdf_download.action_sale_order_export')
        salequotation_action = self.env.ref('tus_multiple_pdf_download.action_sale_quotation_export')

        # sale order
        if res['views'].get('list') and res['views']['list']['id'] == self.env.ref('sale.view_order_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [salequotation_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)

        # sale quotation
        elif res['views'].get('list') and res['views']['list']['id'] == self.env.ref('sale.view_quotation_tree_with_onboarding').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [sale_order_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)
        return res