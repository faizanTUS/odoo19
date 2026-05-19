# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class QuickChatterNote(models.Model):
    _name = 'quick.chatter.note'
    _description = 'Quick Chatter Notes'
    _order = 'sequence, id'

    name = fields.Char('Title', required=True)
    content = fields.Text('Note Content', required=True)

    global_note = fields.Boolean('Global Note', default=False)
    user_id = fields.Many2one('res.users', string='User')

    sequence = fields.Integer(default=10)
