/** @odoo-module */
/* global Cashfree */
import paymentForm from '@payment/js/payment_form';
import { loadJS } from '@web/core/assets';

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
    async _processRedirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        // Handle Cashfree SDK redirect before base method tries to use redirect_form_html
        if (providerCode === 'cashfree' && processingValues.payment_session_id) {
            try {
                // Load Cashfree SDK dynamically if not already loaded
                if (typeof Cashfree === 'undefined') {
                    await this.waitFor(loadJS('https://sdk.cashfree.com/js/v3/cashfree.js'));
                }
                
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
            } catch (error) {
                console.error('Cashfree: Error initializing checkout', error);
                alert('Payment redirect failed. Please try again.');
            }
            return;
        }
        
        // For non-Cashfree providers or if payment_session_id is missing, use base method
        return this._super(...arguments);
    },
});
