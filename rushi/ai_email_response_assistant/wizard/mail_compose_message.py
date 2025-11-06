# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from bs4 import BeautifulSoup
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json
from odoo.exceptions import UserError, ValidationError


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    count = fields.Integer(string='Count', default=0)
    llm_model_key = fields.Char(string='LLM Model Key')
    select_llm_model = fields.Selection([
        ('chat_gpt', 'Chat GPT'),
        ('gemini', 'Gemini')
    ], string='Select LLM Model')

    @api.model
    def default_get(self, fields):
        res = super(MailComposer, self).default_get(fields)
        config = self.env['res.config.settings'].search([], order='id desc', limit=1)
        if config:
            res.update({
                'count': config.count,
                'llm_model_key': config.llm_model_key,
                'select_llm_model': config.select_llm_model
            })
        return res

    def action_generate_via_ai(self):
        count_value = self.count
        llm_model_key = self.llm_model_key
        select_llm_model = self.select_llm_model

        # ✅ Correct new way to define a ChatPromptTemplate
        email_prompt = ChatPromptTemplate.from_template("""
            You are an AI assistant drafting professional email responses. 
            Below is a last some mails for your context:
            {email_context}

            Now, generate a well-structured, relevant, and engaging response to the most recent email:
            {last_email}

            *Response Guidelines:*
            - Avoid generic gratitude phrases like "prompt"
            - Maintain a {tone} tone throughout.
            - Ensure the response is clear and aligned with the conversation.
            - Keep it direct and to the point, without unnecessary pleasantries.

            Your response should be professional, informative, and action-driven.
            Respond strictly in JSON format:
            {{
                "Subject": "...",
                "Body": "..."
            }}
        """)

        active_model = self._context.get('default_model')
        active_id = self._context.get('default_res_ids')

        mails = []
        if active_model and active_id:
            mails = self.env['mail.mail'].search([
                ('res_id', '=', active_id),
                ('model', '=', active_model)
            ], limit=count_value)

        mail_texts = []
        for index, mail in enumerate(mails, start=1):
            soup = BeautifulSoup(mail.body or "", 'html.parser')
            plain_text = soup.get_text(separator=" ").strip()
            mail_texts.append({
                f"Mail {index}": plain_text,
                "Sender": mail.email_from,
                "Receiver": mail.reply_to
            })

        if not mail_texts:
            raise UserError("No emails found to summarize. Please ensure there are previous emails to generate a response.")
        if not llm_model_key or not select_llm_model:
            raise ValidationError("Please select both 'LLM Model' and 'LLM Model Key' in the General Settings before proceeding.")

        try:
            if select_llm_model == "chat_gpt":
                os.environ["OPENAI_API_KEY"] = llm_model_key
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            elif select_llm_model == "gemini":
                os.environ["GOOGLE_API_KEY"] = llm_model_key
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
            else:
                raise ValueError("Invalid selection! Choose either 'chat_gpt' or 'gemini'.")
        except Exception as e:
            raise UserError(f"Error initializing LLM: {e}")

        # ✅ Combine prompt and model directly (instead of LLMChain)
        chain = email_prompt | llm

        tone = "friendly"
        response = chain.invoke({
            "email_context": str(mail_texts),
            "last_email": str(mail_texts[0]),
            "tone": tone
        })

        # ✅ Extract text output
        result_text = response.content.strip()
        result_text = result_text.replace("```json", "").replace("```", "")
        try:
            result_json = json.loads(result_text)
        except json.JSONDecodeError:
            raise UserError("AI response is not in valid JSON format. Please try again.")

        formatted_body = result_json.get("Body", "").replace("\n", "<br>")
        self.body = formatted_body
        self.subject = result_json.get("Subject", "AI Generated Reply")

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
            },
        }
