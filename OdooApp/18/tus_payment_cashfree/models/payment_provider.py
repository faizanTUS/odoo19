# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models
from ..const import CASHFREE_URLS, DEFAULT_PAYMENT_METHOD_CODES


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('cashfree', 'Cashfree')], ondelete={'cashfree': 'set default'})
    cashfree_app_id = fields.Char(string='App id', required_if_provider='cashfree', groups='base.group_user')
    cashfree_secret_key = fields.Char(string='Secret Key', required_if_provider='cashfree', groups='base.group_user')

    def _get_cashfree_urls(self, environment):
        """Get Cashfree API URL based on environment"""
        return CASHFREE_URLS.get(environment, CASHFREE_URLS['test'])['api']

    def _get_cashfree_redirect_urls(self, environment):
        """Get Cashfree checkout URL based on environment"""
        return CASHFREE_URLS.get(environment, CASHFREE_URLS['test'])['checkout']

    def _get_default_payment_method_codes(self):
        """Override of `payment` to return the default payment method codes."""
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'cashfree':
            return default_codes
        return DEFAULT_PAYMENT_METHOD_CODES