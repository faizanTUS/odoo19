# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, models,fields
from odoo.addons.mail.tools.discuss import Store

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def im_search(self, name, limit=20, excluded_ids=None):
        if self.env.user.share:
            if excluded_ids is None:
                excluded_ids = []
            users = self.env['res.users'].sudo().search([
                ('id', '!=', self.env.user.id),
                ('name', 'ilike', name),
                ('active', '=', True),
                ('partner_id', 'not in', excluded_ids),
                '|',
                ('share', '=', True),
                ('can_message', '=', True),
            ], order='name, id', limit=limit)
            res = Store(users.partner_id).get_result()
            return res
        else:
            return super(Partner, self).im_search(name, limit, excluded_ids)

class ResUsers(models.Model):
    _inherit = 'res.users'

    can_message = fields.Boolean('Portal Can Message', default=False)