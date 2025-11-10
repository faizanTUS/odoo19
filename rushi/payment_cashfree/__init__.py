# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from . import models
from . import controllers

from odoo.addons.payment import setup_provider, reset_payment_provider

def post_init_hook(env):
	setup_provider(env, 'cashfree')
	
	# Link payment methods to Cashfree provider and set primary payment method
	cashfree_provider = env.ref('payment_cashfree.payment_acquirer_cashfree', raise_if_not_found=False)
	if cashfree_provider:
		# Set default values only if they are empty (to preserve user-configured values)
		if not cashfree_provider.cashfree_app_id:
			cashfree_provider.cashfree_app_id = 'dummy'
		if not cashfree_provider.cashfree_secret_key:
			cashfree_provider.cashfree_secret_key = 'dummy'
		# Don't change state - let user configure it
		
		# Search for payment methods - includes 'all' instead of 'wallet'
		payment_methods = env['payment.method'].search([
			('code', 'in', ['card', 'netbanking', 'upi', 'all'])
		])
		# Also search by name as fallback
		if not payment_methods:
			payment_methods = env['payment.method'].search([
				('name', 'in', ['Card', 'Net Banking', 'UPI', 'All Payment Methods'])
			])
		if payment_methods:
			# Set primary payment method for each method (self-reference)
			for pm in payment_methods:
				pm.primary_payment_method_id = pm.id
			
			# Link payment methods to provider
			cashfree_provider.payment_method_ids = [(6, 0, payment_methods.ids)]

def uninstall_hook(env):
	reset_payment_provider(env, 'cashfree')