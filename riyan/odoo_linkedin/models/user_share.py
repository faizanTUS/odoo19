# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _



class ResUsersShareId(models.Model):
    _name = 'res.users.share.id'

    share_user_id = fields.Many2one('res.users',string='User')
    share_id = fields.Char(string='Sharing Post ID', readonly=True)
    job_id = fields.Many2one('hr.job',string="Job")