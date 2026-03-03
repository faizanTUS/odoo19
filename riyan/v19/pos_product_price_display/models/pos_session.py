# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    # def _update_session_info(self, session_info):
    #     session_info = super()._update_session_info(session_info)
    #     # Inject the POS backend menu_id so the JS can navigate directly to
    #     # /odoo?menu_id=<id> on session close, avoiding the reload-loop blink.
    #     try:
    #         menu = self.env.ref("point_of_sale.menu_point_root", raise_if_not_found=True)
    #         session_info["pos_backend_menu_id"] = menu.id
    #     except Exception:
    #         _logger.warning(
    #             "pos_product_price_display: Could not find point_of_sale.menu_point_root. "
    #             "Blink-fix redirect will fall back to /odoo."
    #         )
    #     return session_info
