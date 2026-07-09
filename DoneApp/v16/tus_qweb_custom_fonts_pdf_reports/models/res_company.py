# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    custom_font_file_id = fields.Many2one('custom.font.file', string='Custom Font File',
                                          domain="[('company_id', '=', id), ('active', '=', True)]",
                                          help='Select a custom uploaded font file to use in reports')

    def write(self, values):
        """Update asset style when font changes"""
        res = super().write(values)
        if 'font' in values or 'custom_font_file_id' in values:
            # Trigger asset style update
            self._update_asset_style()
        return res

