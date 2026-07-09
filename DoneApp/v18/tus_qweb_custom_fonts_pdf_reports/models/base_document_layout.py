# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    custom_font_file_id = fields.Many2one('custom.font.file', string='Custom Font File',
                                          domain="[('company_id', '=', company_id), ('active', '=', True)]",
                                          help='Select a custom uploaded font file to use in reports. If selected, this font will be used instead of the default font.')

    @api.model
    def default_get(self, fields_list):
        """Set default custom_font_file_id from company"""
        res = super().default_get(fields_list)
        # Always try to set custom_font_file_id if company has one
        company = self.env.company
        if company.custom_font_file_id:
            res['custom_font_file_id'] = company.custom_font_file_id.id
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Set custom_font_file_id when company changes"""
        super()._onchange_company_id()
        for wizard in self:
            wizard.custom_font_file_id = wizard.company_id.custom_font_file_id

    def document_layout_save(self):
        """Override to save custom_font_file_id to company"""
        # Save custom_font_file_id to company before calling super
        for wizard in self:
            # Get the current value from the wizard (might be a recordset or False)
            font_file_id = wizard.custom_font_file_id.id if wizard.custom_font_file_id else False
            
            # Explicitly write the custom_font_file_id to the company
            wizard.company_id.sudo().write({
                'custom_font_file_id': font_file_id
            })
        return super().document_layout_save()

