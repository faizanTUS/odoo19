# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_requisition_id = fields.Many2one(
        'material.requisition',
        string='Material Requisition',
        index=True,
        copy=False,
    )
