# See LICENSE file for full copyright and licensing details.
from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        #invoice
        invoice_action = self.env.ref('tus_multiple_pdf_download.action_invoice_export')
        bill_action = self.env.ref('tus_multiple_pdf_download.action_vendor_bill_export')
        customer_credit_note_action = self.env.ref('tus_multiple_pdf_download.action_customer_credit_notes_export')
        vendor_credit_note_action = self.env.ref('tus_multiple_pdf_download.action_vendor_credit_notes_export')
        # vendor_payment_action = self.env.ref('tus_multiple_pdf_download.vendor_payment_action')
        customer_payment_action = self.env.ref('tus_multiple_pdf_download.customer_payment_action')

        # view_account_supplier_payment_tree
        #account.view_account_payment_tree
        if res['views'].get('list') and res['views']['list']['id'] == self.env.ref('account.view_out_invoice_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [customer_credit_note_action.id, bill_action.id,
                                            vendor_credit_note_action.id, customer_payment_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)

            # bill
        elif res['views'].get('list') and res['views']['list']['id'] == self.env.ref(
                'account.view_in_invoice_bill_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [customer_credit_note_action.id, invoice_action.id,
                                            vendor_credit_note_action.id, customer_payment_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)
            # customer credit Notes
        elif res['views'].get('list') and res['views']['list']['id'] == self.env.ref(
                'account.view_out_credit_note_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [invoice_action.id, bill_action.id, vendor_credit_note_action.id,
                                            customer_payment_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)
            # vendor credit Notes
        elif res['views'].get('list') and res['views']['list']['id'] == self.env.ref(
                'account.view_in_invoice_refund_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [invoice_action.id, bill_action.id, customer_credit_note_action.id,
                                            customer_payment_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)

            # customer payment
        elif res['views'].get('list') and res['views']['list']['id'] == self.env.ref(
                'account.view_account_payment_tree').id:
            if toolbar := res['views']['list'].get('toolbar'):
                actions_to_remove = []
                for action in toolbar.get('action', []):
                    if action.get('id') in [invoice_action.id, bill_action.id, customer_credit_note_action.id,
                                            vendor_credit_note_action.id]:
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    toolbar['action'].remove(action)

        return res
