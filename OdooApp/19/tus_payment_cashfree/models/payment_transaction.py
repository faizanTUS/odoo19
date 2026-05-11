# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import json
import logging

import requests

from odoo import _, models
from odoo.addons.payment.models.payment_provider import ValidationError

from ..const import PAYMENT_METHODS_MAPPING, get_cashfree_headers, sanitize_cashfree_order_id

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _process(self, provider_code, payment_data):
        """Override to ensure successful payments are processed even if validation fails.
        
        :param str provider_code: The code of the provider handling the transaction.
        :param dict payment_data: The payment data sent by the provider.
        :return: The updated transaction.
        :rtype: payment.transaction
        """
        if provider_code != 'cashfree':
            return super()._process(provider_code, payment_data)
        
        tx = self or self._search_by_reference(provider_code, payment_data)
        if tx:
            tx.ensure_one()
            
            # Check if payment is successful before validation
            order_status = payment_data.get('order_status')
            is_paid = order_status == 'PAID'
            
            # Validate amount (may set state to error if validation fails)
            tx._validate_amount(payment_data)
            
            # If validation failed but payment is successful, we still want to process it
            # So we always call _apply_updates() for successful payments
            if is_paid or tx.state != 'error':
                tx._apply_updates(payment_data)
                if tx.tokenize and tx.state in {'authorized', 'done'}:
                    tx._tokenize(payment_data)
            else:
                # Validation failed and payment is not successful - return early
                _logger.warning(
                    "Cashfree: Amount validation failed for transaction %s (order_status: %s). "
                    "Transaction set to error state.",
                    tx.reference,
                    order_status
                )
        return tx

    def _get_specific_processing_values(self, processing_values):
        """Override to create Cashfree order and get payment_session_id"""
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'cashfree':
            return res
        self.ensure_one()
        base_url = self.get_base_url()
        environment = 'prod' if self.provider_id.state == 'enabled' else 'test'
        cashfree_url = self.provider_id._get_cashfree_urls(environment) + '/orders'
        header = get_cashfree_headers(
            self.provider_id.cashfree_app_id,
            self.provider_id.cashfree_secret_key,
        )

        payment_method_id = processing_values.get('payment_method_id')
        if payment_method_id:
            payment_method = self.env['payment.method'].browse(payment_method_id)
            odoo_payment_method_code = payment_method.code if payment_method else None
            odoo_payment_method_name = payment_method.name if payment_method else None
        else:
            odoo_payment_method_code = self.payment_method_id.code if self.payment_method_id else None
            odoo_payment_method_name = self.payment_method_id.name if self.payment_method_id else None

        cashfree_payment_method = None
        if odoo_payment_method_code:
            if odoo_payment_method_code in ('all', 'wallet', 'wallets_india'):
                _logger.info(
                    "Cashfree: '%s' payment method selected ('%s'). "
                    "Showing all payment methods on Cashfree checkout.",
                    odoo_payment_method_name or 'All',
                    odoo_payment_method_code,
                )
                cashfree_payment_method = None
            elif odoo_payment_method_code in PAYMENT_METHODS_MAPPING:
                cashfree_payment_method = PAYMENT_METHODS_MAPPING[odoo_payment_method_code]
            else:
                _logger.warning(
                    "Cashfree: Payment method code '%s' (%s) not found in mapping. "
                    "Available mappings: %s. Not restricting payment methods.",
                    odoo_payment_method_code,
                    odoo_payment_method_name,
                    list(PAYMENT_METHODS_MAPPING.keys()),
                )

        currency = self.env['res.currency'].browse(processing_values.get('currency_id'))
        currency_code = currency.name if currency else 'INR'

        amount = processing_values.get('amount', 0)

        original_reference = processing_values.get('reference')
        sanitized_order_id = sanitize_cashfree_order_id(original_reference)

        customer_phone = self.partner_id.phone or ''
        sanitized_phone = ''.join(c for c in customer_phone if c.isdigit() or c == '+')

        order_meta = {
            'return_url': base_url + f'/cashfree/payment/validate?order_id={sanitized_order_id}',
            'notify_url': base_url + '/cashfree/payment/notify',
        }

        if cashfree_payment_method:
            order_meta['payment_methods'] = cashfree_payment_method
            _logger.info(
                "Cashfree: Restricting payment methods to '%s' (Odoo method: %s - %s)",
                cashfree_payment_method,
                odoo_payment_method_code,
                odoo_payment_method_name,
            )

        data = {
            'order_id': sanitized_order_id,
            'order_amount': amount,
            'order_currency': currency_code,
            'order_note': f'Payment for {original_reference}',
            'customer_details': {
                'customer_id': str(processing_values.get('partner_id', 1)),
                'customer_name': self.partner_id.name or 'Customer',
                'customer_email': self.partner_id.email or '',
                'customer_phone': sanitized_phone,
            },
            'order_meta': order_meta,
        }

        _logger.info(
            "Cashfree: Creating order with payment_methods='%s', order_id='%s', amount=%s",
            order_meta.get('payment_methods', 'all'),
            sanitized_order_id,
            amount,
        )

        response = requests.post(cashfree_url, headers=header, data=json.dumps(data))
        response_val = response.json()
        if response.status_code != 200:
            _logger.error(
                'Cashfree: Order creation failed. Status: %s, Response: %s, Request data: %s',
                response.status_code,
                response_val,
                json.dumps({k: v for k, v in data.items() if k != 'customer_details'}),
            )
            raise ValidationError(
                _('RESP %(status)s %(message)s')
                % {'status': response.status_code, 'message': response_val.get('message')}
            )

        extra = {'sanitized_order_id': sanitized_order_id}
        extra.update(response_val)
        extra['status'] = self.provider_id.state

        payment_session_id = response_val.get('payment_session_id')
        if payment_session_id:
            extra['payment_session_id'] = payment_session_id
            extra['redirect_url'] = None
            extra['cashfree_payment_session_id'] = payment_session_id
            extra['cashfree_mode'] = 'production' if environment == 'prod' else 'sandbox'
        else:
            redirect_base_url = self.provider_id._get_cashfree_redirect_urls(environment)
            extra['redirect_url'] = f'{redirect_base_url}/{sanitized_order_id}'

        return {**res, **extra}

    def _get_specific_rendering_values(self, processing_values):
        """Override to return rendering values for Cashfree redirect form"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cashfree':
            return res
        self.ensure_one()
        
        # Return the rendering values for the redirect form template
        # These values are already set in _get_specific_processing_values
        rendering_values = {
            'cashfree_payment_session_id': processing_values.get('cashfree_payment_session_id', ''),
            'cashfree_mode': processing_values.get('cashfree_mode', 'sandbox'),
        }
        res.update(rendering_values)
        return res

    def _extract_reference(self, provider_code, payment_data):
        """Extract the transaction reference from Cashfree payment data.
        
        :param str provider_code: The code of the provider handling the transaction.
        :param dict payment_data: The payment data sent by Cashfree.
        :return: The transaction reference.
        :rtype: str
        """
        if provider_code != 'cashfree':
            return super()._extract_reference(provider_code, payment_data)
        
        # Cashfree returns order_id in the payment data
        order_id = payment_data.get('order_id')
        if order_id:
            # Find transaction by matching sanitized reference with order_id
            tx_sudo = self.env['payment.transaction'].sudo().search([
                ('provider_code', '=', 'cashfree'),
                ('reference', '!=', False)
            ])
            
            for transaction in tx_sudo:
                sanitized_ref = sanitize_cashfree_order_id(transaction.reference)
                if sanitized_ref == order_id:
                    return transaction.reference
        
        # Fallback to default behavior
        return payment_data.get('reference') or payment_data.get('order_id')

    def _extract_amount_data(self, payment_data):
        """Extract the amount and currency from Cashfree payment data.
        
        :param dict payment_data: The payment data sent by Cashfree.
        :return: The amount data, in the {amount: float, currency_code: str} format, or None to skip validation.
        :rtype: dict|None
        """
        if self.provider_code != 'cashfree':
            return super()._extract_amount_data(payment_data)
        
        # Cashfree returns order_amount and order_currency in the order response
        # Amount and currency might not be present in all payment data (e.g., redirect responses)
        if 'order_amount' not in payment_data or 'order_currency' not in payment_data:
            return None  # Skip validation if amount/currency not present
        
        # Cashfree returns order_amount as a number (already in major currency units, e.g., rupees for INR)
        # No conversion needed - use the amount directly
        order_amount = payment_data['order_amount']
        
        # Ensure it's a float
        try:
            amount = float(order_amount)
        except (ValueError, TypeError):
            _logger.warning(
                "Cashfree: Invalid order_amount format: %s (type: %s). Skipping validation.",
                order_amount,
                type(order_amount)
            )
            return None  # Skip validation if amount format is invalid
        
        return {
            'amount': amount,
            'currency_code': payment_data['order_currency'],
        }

    def _apply_updates(self, payment_data):
        """Update the transaction based on Cashfree payment data.
        
        :param dict payment_data: The payment data sent by Cashfree.
        :return: None
        """
        if self.provider_code != 'cashfree':
            return super()._apply_updates(payment_data)
        
        # If payment is successful (PAID), always set to done, even if validation failed
        # This ensures successful payments are not stuck in error state
        order_status = payment_data.get('order_status')
        if order_status == 'PAID':
            # Payment was successful - set to done regardless of current state
            if self.state != 'done':
                self._set_done()
            # Still update provider reference if needed
            if payment_data.get('order_id') and not self.provider_reference:
                self.provider_reference = payment_data.get('order_id')
            return
        
        # For other statuses, only update if not already in a final state
        if self.state in ('done', 'error', 'canceled'):
            # Still update provider reference if needed
            if payment_data.get('order_id') and not self.provider_reference:
                self.provider_reference = payment_data.get('order_id')
            return
        
        # Update provider reference
        if payment_data.get('order_id'):
            self.provider_reference = payment_data.get('order_id')
        
        # Handle Cashfree payment status according to their API documentation
        # (PAID case is already handled above)
        if order_status == 'ACTIVE':
            self._set_pending()
        elif order_status == 'EXPIRED':
            self._set_canceled()
        elif order_status == 'CANCELLED':
            self._set_canceled()
        else:
            _logger.warning(
                'Cashfree: Unknown status %s for transaction %s',
                order_status,
                payment_data.get('order_id'),
            )
            msg = _(
                'Received unrecognized status for Cashfree Payment %(order)s, status: %(status)s'
            ) % {'order': payment_data.get('order_id'), 'status': order_status}
            self._set_error(msg)
