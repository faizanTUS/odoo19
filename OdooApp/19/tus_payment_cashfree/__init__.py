# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo.addons.payment import reset_payment_provider, setup_provider

from . import controllers
from . import models


def post_init_hook(env):
    setup_provider(env, 'cashfree')
    cashfree_provider = env.ref(
        'tus_payment_cashfree.payment_acquirer_cashfree',
        raise_if_not_found=False,
    )
    if not cashfree_provider:
        return
    if not cashfree_provider.cashfree_app_id:
        cashfree_provider.cashfree_app_id = 'dummy'
    if not cashfree_provider.cashfree_secret_key:
        cashfree_provider.cashfree_secret_key = 'dummy'
    if cashfree_provider.state == 'disabled':
        cashfree_provider.state = 'test'
    if not cashfree_provider.is_published:
        cashfree_provider.is_published = True
    cashfree_provider.available_country_ids = [(5, 0, 0)]
    cashfree_provider.available_currency_ids = [(5, 0, 0)]


def uninstall_hook(env):
    reset_payment_provider(env, 'cashfree')
