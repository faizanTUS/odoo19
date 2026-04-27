# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute(
        """
        UPDATE ir_attachment
        SET owner_id = create_uid
        WHERE owner_id IS NULL
          AND create_uid IS NOT NULL
        """
    )
