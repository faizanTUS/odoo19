# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


def _config_param_truthy(icp, key, default='False'):
    return str(icp.get_param(key, default) or default).lower() in ('1', 'true', 'yes')


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    smtp_by_company = fields.Boolean(string="SMTP BY COMPANY", default=False)
    smtp_by_user = fields.Boolean(string="SMTP BY USER", default=False)

    @api.constrains('smtp_by_company', 'smtp_by_user')
    def _check_smtp_by_company_and_user(self):
        for smtp in self:
            if smtp.smtp_by_company and smtp.smtp_by_user:
                raise ValidationError(
                    _('Outgoing Mail Configuration must be set by either the user or the company, but not both at the same time.')
                )

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env['ir.config_parameter'].sudo()
        res.update(
            smtp_by_company=_config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_company'),
            smtp_by_user=_config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_user'),
        )
        return res

    def set_values(self):
        super().set_values()
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('send_mail_company_wish_ext.smtp_by_company', self.smtp_by_company)
        icp.set_param('send_mail_company_wish_ext.smtp_by_user', self.smtp_by_user)
        mail_servers = self.env['ir.mail_server'].sudo().search([])
        if mail_servers:
            mail_servers.write({
                'is_smtp_by_company': self.smtp_by_company,
                'is_smtp_by_user': self.smtp_by_user,
            })
