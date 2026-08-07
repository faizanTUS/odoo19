# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class RmaReason(models.Model):
    _name = 'rma.reason'
    _description = 'RMA Reason'

    name = fields.Char(string='Reason', required=True)
    action = fields.Selection([
        ('return_refund', 'Return & Refund'),
        ('replacement', 'Replacement'),
        ('only_return', 'Only Return'),
        ('no_action', 'NO ACTION'),
        ('contact_support', 'Contact Support'),
    ], string='Action', default='return_refund', required=True)
    description = fields.Text(string='Description')
    service_charge = fields.Float(string='Service Charge')
    active = fields.Boolean(default=True)
