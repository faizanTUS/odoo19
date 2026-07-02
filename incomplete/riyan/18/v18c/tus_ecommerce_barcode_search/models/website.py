# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        search_fields = result and result[0] and result[0].get('search_fields')
        model = result and result[0] and result[0] and result[0].get('model')
        if search_fields and model == 'product.template':
            # Append the 'barcode' field to the existing search fields
            search_fields.append('barcode')
        return result
