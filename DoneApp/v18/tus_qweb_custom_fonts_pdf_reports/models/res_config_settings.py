# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_open_custom_font_files(self):
        """Open custom font files action with proper company context"""
        self.ensure_one()
        action = self.env.ref('tus_qweb_custom_fonts_pdf_reports.action_custom_font_file').read()[0]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'search_default_company_id': self.company_id.id,
            'search_default_active': 1,
        }
        action['domain'] = [('company_id', '=', self.company_id.id)]
        return action

