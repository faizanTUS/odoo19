# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models


class ExportProductDataWizard(models.TransientModel):
    _name = 'export.product.data.wizard'
    _description = 'Export Product Data Wizard'

    def export_products_image(self):
        selected_products = self.env['product.template'].browse(self._context.get('active_ids'))
        return selected_products.action_export_products_image()

    def export_products_data(self):
        selected_products = self.env['product.template'].browse(self._context.get('active_ids'))
        return selected_products.action_export_products()
