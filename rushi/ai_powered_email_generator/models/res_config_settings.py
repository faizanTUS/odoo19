# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    select_llm_model = fields.Selection([
        ('chat_gpt', 'Chat GPT'),
        ('gemini', 'Gemini')], string='Select LLM Model')
    llm_model_key = fields.Char(string='LLM Model Key')
    llm_model_key_label = fields.Char(
        string="Dynamic Label", compute="_compute_llm_model_key_label", store=False
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        llm_model_key = ICPSudo.get_param('mail.compose.message.llm_model_key', default="")
        select_llm_model = ICPSudo.get_param('mail.compose.message.select_llm_model', default="")
        res.update(select_llm_model=select_llm_model, llm_model_key=llm_model_key)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('mail.compose.message.llm_model_key', self.llm_model_key)
        ICPSudo.set_param('mail.compose.message.select_llm_model', self.select_llm_model)

    @api.depends('select_llm_model')
    def _compute_llm_model_key_label(self):
        for record in self:
            if record.select_llm_model == 'gemini':
                record.llm_model_key_label = "Gemini LLM Key"
            elif record.select_llm_model == 'chat_gpt':
                record.llm_model_key_label = "Chat GPT Key"
            else:
                record.llm_model_key_label = ""