# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import logging
from odoo import http
from odoo.http import request
import requests
from ..const import get_cashfree_headers

_logger = logging.getLogger(__name__)


class CashfreeController(http.Controller):

    _return_url = '/cashfree/payment/validate'
    _notify_url = '/cashfree/payment/notify'

    @staticmethod
    def _sanitize_order_id(order_id):
        """Sanitize order_id for Cashfree (alphanumeric with _ and - only, 3-45 characters)"""
        sanitized = ''.join(c if c.isalnum() or c in '_-' else '_' for c in order_id)
        if len(sanitized) < 3:
            sanitized = sanitized + '_' * (3 - len(sanitized))
        elif len(sanitized) > 45:
            sanitized = sanitized[:45]
        return sanitized

    def _find_transaction_by_order_id(self, order_id):
        """Find transaction by matching sanitized reference with Cashfree order_id"""
        tx_sudo = request.env['payment.transaction'].sudo().search([
            ('provider_code', '=', 'cashfree'),
            ('reference', '!=', False)
        ])
        
        for tx in tx_sudo:
            sanitized_ref = self._sanitize_order_id(tx.reference)
            if sanitized_ref == order_id:
                return tx
        return None

    @http.route('/cashfree/payment/validate', type='http', auth="public", methods=['POST','GET'], csrf=False)
    def cashfree_validate(self, **post):
        """Handle return from Cashfree payment page"""
        provider_id = request.env.ref('payment_cashfree.payment_acquirer_cashfree').sudo()
        
        if provider_id and post.get('order_id'):
            try:
                header = get_cashfree_headers(
                    provider_id.cashfree_app_id,
                    provider_id.cashfree_secret_key
                )
                environment = 'prod' if provider_id.state == 'enabled' else 'test'
                url = provider_id._get_cashfree_urls(environment)
                order_url = url + '/orders/' + post.get('order_id')
                
                # Get order details from Cashfree
                response = requests.get(order_url, headers=header)
                
                if response.status_code == 200:
                    response_val = response.json()
                    sanitized_order_id = response_val.get('order_id')
                    order_status = response_val.get('order_status')
                    
                    # Find transaction by matching sanitized reference with order_id
                    matching_tx = self._find_transaction_by_order_id(sanitized_order_id)
                    
                    if matching_tx:
                        # Process the payment status using Odoo 19's _process method
                        matching_tx._process('cashfree', response_val)
                        
                        # Monitor the transaction for post-processing (required for Odoo 19)
                        from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
                        PaymentPostProcessing.monitor_transaction(matching_tx)
                        
                        # Check payment status based on Cashfree order_status
                        # The transaction state is already updated by _process() -> _apply_updates()
                        if order_status == 'PAID':
                            # Payment was successful - redirect to payment status page
                            # The payment status page will handle post-processing and redirect to landing_route
                            _logger.info(
                                "Cashfree: Payment successful for transaction %s (order_status: %s, tx_state: %s), redirecting to status page",
                                matching_tx.reference,
                                order_status,
                                matching_tx.state
                            )
                            return request.redirect('/payment/status')
                        elif order_status == 'ACTIVE':
                            # User came back without completing payment (clicked back button)
                            # Check transaction state to determine appropriate redirect
                            if matching_tx.state == 'pending':
                                # Transaction is still pending - user clicked back, cancel it
                                matching_tx._set_canceled()
                                _logger.info("Cashfree: User returned without completing payment, transaction %s canceled", matching_tx.reference)
                            
                            # Always redirect to payment status page so user can see the transaction status
                            # The payment status page will show the canceled/failed status
                            _logger.info(
                                "Cashfree: User returned from Cashfree, transaction %s state is '%s' (order_status: ACTIVE), redirecting to status page",
                                matching_tx.reference,
                                matching_tx.state
                            )
                            return request.redirect('/payment/status')
                        elif order_status in ('EXPIRED', 'CANCELLED'):
                            # Payment expired or was cancelled
                            if matching_tx.state not in ('done', 'error'):
                                matching_tx._set_canceled()
                            _logger.info(
                                "Cashfree: Payment %s for transaction %s (tx_state: %s), redirecting to status page",
                                order_status.lower(),
                                matching_tx.reference,
                                matching_tx.state
                            )
                            return request.redirect('/payment/status')
                        else:
                            # Unknown status - redirect to payment status page
                            _logger.warning(
                                "Cashfree: Unknown payment status '%s' for transaction %s (tx_state: %s), redirecting to status page",
                                order_status,
                                matching_tx.reference,
                                matching_tx.state
                            )
                            return request.redirect('/payment/status')
                    else:
                        _logger.warning("Cashfree: No transaction found for order_id %s", sanitized_order_id)
                        return request.redirect('/')
                else:
                    _logger.error("Cashfree: Failed to get order details. Status: %s", response.status_code)
                    
            except Exception as e:
                _logger.error("Cashfree: Error in validation: %s", str(e))
        
        # Fallback redirect if no order_id or error occurred
        return request.redirect('/')

    @http.route(_notify_url, type='http', auth="public", methods=['POST'], csrf=False)
    def cashfree_notify(self, **post):
        """Handle Cashfree webhook notifications"""
        provider_id = request.env.ref('payment_cashfree.payment_acquirer_cashfree').sudo()
        
        if provider_id and post.get('order_id'):
            try:
                header = get_cashfree_headers(
                    provider_id.cashfree_app_id,
                    provider_id.cashfree_secret_key
                )
                environment = 'prod' if provider_id.state == 'enabled' else 'test'
                url = provider_id._get_cashfree_urls(environment)
                order_url = url + '/orders/' + post.get('order_id')
                
                # Get order details from Cashfree
                response = requests.get(order_url, headers=header)
                
                if response.status_code == 200:
                    response_val = response.json()
                    sanitized_order_id = response_val.get('order_id')
                    
                    # Find transaction by matching sanitized reference with order_id
                    matching_tx = self._find_transaction_by_order_id(sanitized_order_id)
                    
                    if matching_tx:
                        matching_tx._process('cashfree', response_val)
                        _logger.info("Cashfree: Webhook processed for transaction %s", matching_tx.reference)
                    else:
                        _logger.warning("Cashfree: No transaction found for webhook order_id %s", sanitized_order_id)
                else:
                    _logger.error("Cashfree: Failed to get order details in webhook. Status: %s", response.status_code)
                    
            except Exception as e:
                _logger.error("Cashfree: Error in webhook processing: %s", str(e))
        
        return 'OK'  # Return simple OK response for webhook