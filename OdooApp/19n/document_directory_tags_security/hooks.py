# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Backfill owner_id from create_uid for attachments created before this module."""
    env.cr.execute(
        """
        UPDATE ir_attachment
        SET owner_id = create_uid
        WHERE owner_id IS NULL AND create_uid IS NOT NULL
        """
    )
