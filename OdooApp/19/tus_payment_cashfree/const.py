# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Cashfree API Configuration
CASHFREE_URLS = {
    'test': {
        'api': 'https://sandbox.cashfree.com/pg',
        'checkout': 'https://sandbox.cashfree.com/pg/checkout',
    },
    'prod': {
        'api': 'https://api.cashfree.com/pg',
        'checkout': 'https://api.cashfree.com/pg/checkout',
    }
}

# Cashfree API Headers
def get_cashfree_headers(app_id, secret_key):
    """Get standard Cashfree API headers"""
    return {
        'x-client-id': app_id,
        'x-client-secret': secret_key,
        'x-api-version': '2022-09-01',
        'Content-Type': 'application/json',
    }


def sanitize_cashfree_order_id(order_id):
    """Sanitize order_id for Cashfree (alphanumeric with _ and - only, 3-45 characters)."""
    if order_id is None:
        order_id = ''
    order_id = str(order_id)
    sanitized = ''.join(c if c.isalnum() or c in '_-' else '_' for c in order_id)
    if len(sanitized) < 3:
        sanitized = sanitized + '_' * (3 - len(sanitized))
    elif len(sanitized) > 45:
        sanitized = sanitized[:45]
    return sanitized


# Default Payment Method Codes for Cashfree
DEFAULT_PAYMENT_METHOD_CODES = {
    'card',
    'netbanking', 
    'upi',
    'all',  # Shows all payment methods on Cashfree checkout
}

# Payment Method Codes Mapping (Odoo code -> Cashfree code)
# According to Cashfree API valid payment_methods: cc,dc,ppc,ccc,emi,paypal,upi,nb,app,paylater,applepay
# Note: 'wallet' is NOT a valid payment_methods value - wallets are handled differently
PAYMENT_METHODS_MAPPING = {
    'card': 'cc',  # Cashfree uses 'cc' for credit/debit cards (can also use 'cc,dc' for both)
    'netbanking': 'nb',  # Cashfree uses 'nb' for netbanking
    'upi': 'upi',  # UPI code is the same
    # 'wallet' and 'wallets_india' are not valid payment_methods values
    # Wallets are available on Cashfree checkout but cannot be restricted via payment_methods
}