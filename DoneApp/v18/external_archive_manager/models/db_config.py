# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import psycopg2


ARCHIVE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS odoo_external_archive (
    id BIGSERIAL PRIMARY KEY,
    odoo_db_uuid TEXT NOT NULL,
    model TEXT NOT NULL,
    res_id BIGINT NOT NULL,
    field_name TEXT NOT NULL,
    field_type TEXT NOT NULL,
    field_value JSONB,
    archived_at TIMESTAMP,
    archived_by BIGINT,
    checksum TEXT,
    UNIQUE (odoo_db_uuid, model, res_id, field_name)
);
CREATE INDEX IF NOT EXISTS idx_odoo_external_archive_model_res_id
    ON odoo_external_archive(model, res_id);
CREATE INDEX IF NOT EXISTS idx_odoo_external_archive_archived_at
    ON odoo_external_archive(archived_at);
"""


class ExternalArchiveDbConfig(models.Model):
    _name = "external.archive.db.config"
    _description = "External Archive DB Configuration"
    _rec_name = "name"

    name = fields.Char(required=True, default="External Archive DB")
    host = fields.Char(required=True)
    port = fields.Integer(required=True, default=5432)
    database = fields.Char(required=True)
    user = fields.Char(required=True)
    password = fields.Char(required=True)  # For production: store/encrypt in ir.config_parameter
    ssl_mode = fields.Selection(
        [("disable", "disable"), ("require", "require"), ("verify-ca", "verify-ca"), ("verify-full", "verify-full")],
        default="disable",
        required=True,
    )
    active = fields.Boolean(default=True)
    last_tested_at = fields.Datetime(readonly=True)

    @api.constrains("active")
    def _check_single_active(self):
        for rec in self:
            if rec.active:
                others = self.search([("active", "=", True), ("id", "!=", rec.id)], limit=1)
                if others:
                    raise UserError(_("Only one active External Archive DB configuration is allowed."))

    def _get_conn(self):
        self.ensure_one()
        try:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.database,
                user=self.user,
                password=self.password,
                sslmode=self.ssl_mode,
            )
        except Exception as e:
            raise UserError(_("External DB connection failed: %s") % str(e))

    def action_test_connection(self):
        self.ensure_one()
        conn = self._get_conn()
        try:
            with conn.cursor() as cr:
                cr.execute(ARCHIVE_TABLE_SQL)
            conn.commit()
            self.last_tested_at = fields.Datetime.now()
        except Exception as e:
            conn.rollback()
            raise UserError(_("External DB test/schema setup failed: %s") % str(e))
        finally:
            conn.close()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('Test connection successful'),
                'type': 'rainbow_man',
            }
        }

