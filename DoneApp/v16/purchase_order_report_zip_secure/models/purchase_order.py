# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api


class PurchaseOrderPdf(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)

        purchase_order_action = self.env.ref('purchase_order_report_zip_secure.action_purchase_order_export_zip_pdf')
        purchasequotation_action = self.env.ref('purchase_order_report_zip_secure.action_purchase_order_quotation_export_zip')

        # purchase order
        if res['views'].get('list') and res['views']['list']['id'] == self.env.ref('purchase.purchase_order_view_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [purchasequotation_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)

        # purchase quotation
        elif res['views'].get('list') and res['views']['list']['id'] == self.env.ref('purchase.purchase_order_kpis_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [purchase_order_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)
        return res