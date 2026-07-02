# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    combo_display = fields.Selection(
        [
            ('list', 'List View'),
            ('grid', 'Grid View'),
        ],
        string='Combo Display',
        default='list',
        help='Default display for combo product selection popup in POS (list or grid).',
    )
