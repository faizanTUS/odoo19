# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models


def _config_param_truthy(icp, key, default='False'):
    return str(icp.get_param(key, default) or default).lower() in ('1', 'true', 'yes')


class IrMailServer(models.Model):

    _inherit = "ir.mail_server"

    user_ids = fields.Many2many(
        'res.users',
        'ir_mail_server_user_rel',
        'mail_server_id',
        'user_id',
        string="User",
    )
    company_ids = fields.Many2many(
        'res.company',
        'ir_mail_server_rel',
        'mail_server_id',
        'company_id',
        string="Company",
    )
    is_smtp_by_company = fields.Boolean(string="Is SMTP by Company", default=False)
    is_smtp_by_user = fields.Boolean(string="Is SMTP by User", default=False)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        icp = self.env['ir.config_parameter'].sudo()
        updates = {}
        if 'is_smtp_by_company' in fields:
            updates['is_smtp_by_company'] = _config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_company')
        if 'is_smtp_by_user' in fields:
            updates['is_smtp_by_user'] = _config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_user')
        res.update(updates)
        return res
