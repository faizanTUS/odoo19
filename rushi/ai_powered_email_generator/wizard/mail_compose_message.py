# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import os
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json


class MailComposer(models.TransientModel):

    _inherit = 'mail.compose.message'

    fields_ids = fields.Many2many(
        'ir.model.fields',
        'name',
        domain="[('model','=',model),('ttype','in',['char', 'integer', 'float', 'many2one', 'datetime', 'date', 'text'])]"
    )

    llm_model_key = fields.Char(string='LLM Model Key')
    select_llm_model = fields.Selection([
        ('chat_gpt', 'Chat GPT'),
        ('gemini', 'Gemini')], string='Select LLM Model')

    @api.model
    def default_get(self, fields):
        res = super(MailComposer, self).default_get(fields)
        config = self.env['res.config.settings'].search([], order='id desc', limit=1)
        if config:
            res.update({'llm_model_key': config.llm_model_key,
                        'select_llm_model': config.select_llm_model})
        return res

    def action_get_field_data(self):

        llm_model_key = self.llm_model_key
        select_llm_model = self.select_llm_model
        email_prompt = PromptTemplate(
            input_variables=["type", "entities", "tone"],
            template="""
                    You are an AI assistant drafting professional email responses.

                    *Context:*
                    - *Type:* {type}
                    - *Details:* {entities}

                    *Response Guidelines:*
                    - Maintain a *{tone}* tone (options: Formal, Neutral, Friendly).
                    - Keep responses clear, concise, and aligned with the conversation.
                    - Avoid generic gratitude phrases like "Thank you for your prompt response."
                    - Focus on professionalism, relevance, and actionability.
                    -No need to add signature or name position company etc.

                    Your response should be professional, informative, and action-driven.
                    response in JSON Data like (Subject: "",Body:"")
                    """,
        )
        active_model = self._context.get('default_model')
        active_id = self._context.get('default_res_ids')

        if not llm_model_key or not select_llm_model:
            raise ValidationError("Please select both 'LLM Model' and 'LLM Model Key' in the General Settings before proceeding.")

        if not self.fields_ids:
            raise ValidationError("Please select at least one field before proceeding.")


        fields_date = {}
        technical_name = self.model
        model_description = self.env['ir.model'].search([('model', '=', technical_name)], limit=1).name
        fields_date['object'] = model_description
        data = {}

        if self.model and self.fields_ids:
            active_id = self._context.get('default_res_ids')

            if active_id:
                record = self.env[self.model].browse(active_id)
                if record.exists():
                    for field in self.fields_ids:
                        field_value = record[field.name]
                        if field.ttype == 'many2one' and field_value:
                            field_value = field_value.name
                        elif field.ttype in ['datetime', 'date'] and field_value:
                            field_value = field_value.strftime('%d/%m/%Y')
                        data[field.field_description] = field_value

        fields_date['data'] = data

        try:
            if select_llm_model== "chat_gpt":
                os.environ["OPENAI_API_KEY"] = llm_model_key
                llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            elif select_llm_model== "gemini":
                GEMINI_API_KEY = llm_model_key
                os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
                llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
            else:
                raise ValueError("Invalid selection! Choose either 'openai' or 'gemini'.")
        except Exception as e:
            raise
        email_chain = LLMChain(llm=llm, prompt=email_prompt)
        tone = "friendly"
        response = email_chain.run(type=str(fields_date["object"]), entities=str(fields_date["data"]), tone=tone)

        response = response.replace("```json", "").replace("```", "")
        response = json.loads(response)
        formatted_body = response['Body'].replace("\n", "<br>")
        self.body = formatted_body
        self.subject = response['Subject']

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': self.env.ref('mail.email_compose_message_wizard_form').id,
            'target': 'new',
            'context': {
                'default_model': active_model,
                'default_res_ids': active_id,
                'default_body': self.body,
                'default_subject': self.subject,
                'default_fields_ids':self.fields_ids.ids
            },
        }