# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    material_requisition_officer = fields.Boolean(
        string='Requisition Officer',
        help='Allow this user to approve/reject material requisitions and generate pickings/POs.',
    )
    material_requisition_stock_location_id = fields.Many2one(
        'stock.location',
        string='User Stock Location',
        help='Default stock location for material requisitions created by this user when not selected on the requisition form.',
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
