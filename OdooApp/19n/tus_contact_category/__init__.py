# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from . import models
from odoo import api, SUPERUSER_ID

def _post_install_default_category(env):
    """Give every partner the default category if they have none."""
    default = env.ref('tus_contact_category.contact_category_default')
    env['res.partner'].search([('contact_categ_id', '=', False)]).write({
        'contact_categ_id': default.id
    })