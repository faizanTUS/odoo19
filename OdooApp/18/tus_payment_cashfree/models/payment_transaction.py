# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import models, _
from odoo.addons.payment.models.payment_provider import ValidationError

from ..const import (
    PAYMENT_METHODS_MAPPING,
    get_cashfree_headers,
    sanitize_cashfree_order_id,
)

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_processing_values(self, processing_values):
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
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cashfree':
            return res
        self.ensure_one()
        res.update({
            'cashfree_payment_session_id': processing_values.get('cashfree_payment_session_id', ''),
            'cashfree_mode': processing_values.get('cashfree_mode', 'sandbox'),
        })
        return res

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'cashfree':
            return

        order_status = notification_data.get('order_status')

        if order_status == 'PAID':
            self._set_done()
        elif order_status == 'ACTIVE':
            self._set_pending()
        elif order_status == 'EXPIRED':
            self._set_canceled()
        elif order_status == 'CANCELLED':
            self._set_canceled()
        else:
            _logger.warning(
                'Cashfree: Unknown status %s for transaction %s',
                order_status,
                notification_data.get('order_id'),
            )
            msg = _(
                'Received unrecognized status for Cashfree Payment %(order)s, status: %(status)s'
            ) % {
                'order': notification_data.get('order_id'),
                'status': order_status,
            }
            self._set_error(msg)
