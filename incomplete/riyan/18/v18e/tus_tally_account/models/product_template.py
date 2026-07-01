# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    def button_validate(self):
        return super(StockPicking, self.with_context(picking_type_id=self.picking_type_id)).button_validate()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_accounts(self):
        accounts = super(ProductTemplate, self)._get_product_accounts()
        res = self._get_asset_accounts()
        if self.env.company.anglo_saxon_accounting and self.env.company.anglo_saxon_accounting_according_to_tally:
            if 'create_bill' in self._context and self._context.get('create_bill') == True:
                accounts.update({
                    'stock_input': res['stock_input'] or self.categ_id.property_account_expense_categ_id,
                })
            if 'picking_type_id' in self._context and self._context.get('picking_type_id').code == 'outgoing':
                accounts.update({
                    'stock_output': res['stock_input'] or self.categ_id.property_stock_account_input_categ_id,
                })
        return accounts

class ResComapny(models.Model):
    _inherit = 'account.account'
    
    tally_wise_reporting = fields.Boolean(string='Tally wise Reporting')
    anglo_saxon_accounting_according_to_tally = fields.Boolean(string='Anglo-Saxon Accounting according to Tally')

class ResComapny(models.Model):
    _inherit = 'res.company'

    anglo_saxon_accounting_according_to_tally = fields.Boolean(string='Anglo-Saxon Accounting according to Tally')
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    use_anglo_saxen_according_to_tally = fields.Boolean(string='Anglo-Saxon Accounting according to Tally', related='company_id.anglo_saxon_accounting_according_to_tally', readonly=False)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        if self.env.company.anglo_saxon_accounting and self.env.company.anglo_saxon_accounting_according_to_tally:
            return []
        return super(AccountMove, self)._stock_account_prepare_anglo_saxon_out_lines_vals()
