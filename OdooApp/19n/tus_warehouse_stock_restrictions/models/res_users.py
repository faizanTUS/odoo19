# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Locations')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id', 'location_id',
        string='Allowed Stock Locations'
    )

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type',
        'stock_picking_type_users_rel',
        'user_id', 'picking_type_id',
        string='Allowed Operations'
    )

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Allowed Warehouses'
    )

    limit_sale_order = fields.Integer(
        string='Sale Order List Limit',
        default=15
    )
