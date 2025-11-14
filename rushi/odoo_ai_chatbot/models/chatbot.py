# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import os
import warnings
import logging
from odoo import models, sql_db, tools, _
from odoo.http import request
from odoo.exceptions import UserError

from sqlalchemy.exc import SAWarning
warnings.filterwarnings(
    "ignore", category=SAWarning, message=".*unresolvable cycles between tables.*"
)

from . import Sql_agenT_chatbot, gemini_exp

_logger = logging.getLogger(__name__)

class ChatBot(models.Model):
    _name = "chatbot"
    _description = "Chatbot"

    def get_response(self, input_data, chatbot_session_id, partner_id=None):
        database_name = (
            tools.config["db_name"] if tools.config["db_name"] else request.session.db
        )
        # conn_info = sql_db.connection_info_for(db_or_uri=database_name)[1]
        connection_info = sql_db.connection_info_for(db_or_uri=database_name)
        if isinstance(connection_info, tuple):
            conn_info = connection_info[1]
        elif isinstance(connection_info, dict):
            conn_info = connection_info
        else:
            raise UserError(_("Unexpected database connection info format: %s") % type(connection_info))

        db_user = os.environ.get("PGUSER")
        db_password = os.environ.get("PGPASSWORD")

        if db_user and db_password and not db_user == None and not db_password == None:
            connection_str = f"postgresql://{db_user}:{db_password}@{conn_info.get('host') if conn_info.get('host') else 'localhost'}:{conn_info.get('port') if conn_info.get('port') else '5432'}/{conn_info.get('database')}"
        elif len(conn_info) == 7:
            connection_str = f"postgresql://{conn_info.get('user')}:{conn_info.get('password')}@{conn_info.get('host') if conn_info.get('host') else 'localhost' }:{conn_info.get('port') if conn_info.get('port') else '5432'}/{conn_info.get('database')}"
        elif (
            all(tools.config[key] == False for key in ["db_host", "db_port", "db_user"])
            and db_user == None
            and db_password == None
            and not len(conn_info) == 7
        ):
            raise UserError(
                _(
                    "Please define Username, Password, Port, Host and DB name in the Odoo configuration file to establish a database connection."
                )
            )

        MEMORY_FILE = "sql_agent_memory.json"
        is_open_ai = (
            self.env["ir.config_parameter"].sudo().get_param("chatbot.is_open_ai")
        )
        is_gemini = (
            self.env["ir.config_parameter"].sudo().get_param("chatbot.is_gemini")
        )
        if is_open_ai:
            api_key = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("chatbot.open_ai_api_key")
            )
            response_handler = Sql_agenT_chatbot.Response(
                api_key=api_key, connection_str=connection_str
            )
        elif is_gemini:
            api_key = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("chatbot.gemini_api_key")
            )
            response_handler = gemini_exp.Response(
                api_key=api_key, connection_str=connection_str
            )
        else:
            raise UserError(_("Please enter a valid API key for OpenAI or Gemini."))

        if input_data.lower() == "exit":
            Sql_agenT_chatbot.save_memory_to_json(response_handler.memory, MEMORY_FILE)
        if len(Sql_agenT_chatbot.memory.chat_memory.messages) > 10:
            Sql_agenT_chatbot.memory.chat_memory.messages = Sql_agenT_chatbot.memory.chat_memory.messages[-5:]
        result = response_handler.process_user_input(input_data)

        history = self.env["chat.history"].create(
            {
                "user_input": input_data,
                "bot_response_json": result,
            }
        )
        session = self.env["chatbot.session"].browse(chatbot_session_id)
        if not session.exists():
            session = self.env["chatbot.session"].create({
                "partner_id": partner_id or self.env.user.partner_id.id,
                "name": "New Chat Session",
            })
        history.write({
            "chatbot_session_id": session.id
        })

        # Optional: update partner
        session.partner_id = partner_id or self.env.user.partner_id.id
        return result
