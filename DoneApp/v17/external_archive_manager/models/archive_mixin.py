# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _
from odoo.exceptions import UserError
import json
import psycopg2.extras
import base64


class ExternalArchiveMixin(models.AbstractModel):
    _name = "external.archive.mixin"
    _description = "External Archive Mixin"

    def _archive_config_for_model(self):
        return self.env["external.archive.config"].sudo().search(
            [("active", "=", True), ("model_name", "=", self._name)],
            limit=1,
        )

    def _active_db_config(self):
        db = self.env["external.archive.db.config"].sudo().search([("active", "=", True)], limit=1)
        if not db:
            raise UserError(_("No active External Archive DB configuration found."))
        return db

    def _odoo_db_uuid(self):
        # Phase 1: use dbname; for production store a generated UUID in ir.config_parameter
        return self.env.cr.dbname

    def action_external_offload(self):
        self = self.sudo()
        for rec in self:
            rec._external_offload_one()

    def action_external_retrieve(self):
        self = self.sudo()
        for rec in self:
            rec._external_retrieve_one()

    def action_external_delete(self):
        self = self.sudo()
        for rec in self:
            rec._external_delete_one()

    def _external_offload_one(self):
        self.ensure_one()
        cfg = self._archive_config_for_model()
        if not cfg:
            raise UserError(_("No archive configuration found for model %s") % self._name)

        db = self._active_db_config()
        fields_to_archive = cfg._get_field_names_and_types()

        payload_rows = []
        for fname, ftype in fields_to_archive:
            val = self[fname]
            if ftype == "many2one":
                val = val.id if val else None
            elif ftype == "binary":
                val = base64.b64encode(val).decode("utf-8") if val else None
            elif ftype in ("one2many", "many2many"):
                raise UserError(_("Relational fields (x2many) are not supported for offload in Phase 1: %s") % fname)

            payload_rows.append(
                (
                    self._odoo_db_uuid(),
                    self._name,
                    self.id,
                    fname,
                    ftype,
                    json.dumps(val, default=str),
                    self.env.user.id,
                )
            )

        conn = db._get_conn()
        try:
            with conn.cursor() as cr:
                psycopg2.extras.register_default_jsonb(cr)
                cr.executemany(
                    """
                    INSERT INTO odoo_external_archive
                        (odoo_db_uuid, model, res_id, field_name, field_type, field_value, archived_at, archived_by)
                    VALUES
                        (%s, %s, %s, %s, %s, %s::jsonb, NOW(), %s)
                    ON CONFLICT (odoo_db_uuid, model, res_id, field_name)
                    DO UPDATE SET field_value=EXCLUDED.field_value, archived_at=NOW(), archived_by=EXCLUDED.archived_by
                    """,
                    payload_rows,
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise UserError(_("Offload failed: %s") % str(e))
        finally:
            conn.close()

        # Clear values only after external write succeeded
        write_vals = {}
        for fname, ftype in fields_to_archive:
            # Skip clearing required fields to avoid ValidationError
            if self._fields[fname].required:
                continue

            if ftype in ("char", "text", "html"):
                write_vals[fname] = False
            elif ftype in ("integer", "float", "monetary"):
                write_vals[fname] = 0
            else:
                write_vals[fname] = False
        self.write(write_vals)

        return True

    def _external_retrieve_one(self):
        self.ensure_one()
        db = self._active_db_config()

        conn = db._get_conn()
        try:
            with conn.cursor() as cr:
                cr.execute(
                    """
                    SELECT field_name, field_type, field_value
                    FROM odoo_external_archive
                    WHERE odoo_db_uuid=%s AND model=%s AND res_id=%s
                    """,
                    (self._odoo_db_uuid(), self._name, self.id),
                )
                rows = cr.fetchall()
        except Exception as e:
            raise UserError(_("Retrieve failed: %s") % str(e))
        finally:
            conn.close()

        if not rows:
            raise UserError(_("No archived data found for this record."))

        write_vals = {}
        for fname, ftype, fvalue in rows:
            val = fvalue
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            if ftype == "many2one":
                write_vals[fname] = val or False
            elif ftype == "binary":
                write_vals[fname] = base64.b64decode(val) if val else False
            else:
                write_vals[fname] = val

        self.write(write_vals)

        return True

    def _external_delete_one(self):
        self.ensure_one()
        db = self._active_db_config()

        conn = db._get_conn()
        try:
            with conn.cursor() as cr:
                cr.execute(
                    """
                    DELETE FROM odoo_external_archive
                    WHERE odoo_db_uuid=%s AND model=%s AND res_id=%s
                    """,
                    (self._odoo_db_uuid(), self._name, self.id),
                )
                deleted = cr.rowcount
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise UserError(_("External delete failed: %s") % str(e))
        finally:
            conn.close()

        return True