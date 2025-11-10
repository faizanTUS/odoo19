/** @odoo-module */
import paymentForm from '@payment/js/payment_form';

paymentForm.include({
    /**
     * Redirect the customer to Cashfree hosted payment page.
     *
     * @override method from @payment/js/payment_form
     * @private
     * @param {string} providerCode - The code of the selected payment option's provider
     * @param {number} paymentOptionId - The id of the selected payment option
     * @param {string} paymentMethodCode - The code of the selected payment method, if any
     * @param {object} processingValues - The processing values of the transaction
     * @return {void}
     */
    _processRedirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'cashfree') {
            return this._super(...arguments);
        }
        
        // For Cashfree, use the JavaScript SDK to open checkout
        if (processingValues.payment_session_id) {
            // Determine environment based on status
            const mode = processingValues.status === 'enabled' ? 'production' : 'sandbox';
            
            // Initialize Cashfree SDK
            const cashfree = Cashfree({
                mode: mode
            });
            
            // Open the checkout page
            cashfree.checkout({
                paymentSessionId: processingValues.payment_session_id,
                redirectTarget: "_self"
            });
        } else {
            console.error('Cashfree: No payment_session_id received');
            alert('Payment redirect not available. Please try again.');
        }
    },
});
