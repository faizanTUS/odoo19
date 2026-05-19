# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import ast
from lxml import etree

ALLOWED_TYPES = {
    "char", "text","html", "json", "boolean",
    "integer", "float", "monetary",
    "date", "datetime", "selection",
    "many2one","binary"
}


class ExternalArchiveConfig(models.Model):
    _name = "external.archive.config"
    _description = "External Archive Configuration"
    _rec_name = "name"

    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(related="model_id.model", store=True, index=True)

    field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields to Offload",
        domain="""
                   [
                       ('model_id', '=', model_id),
                       ('store', '=', True),
                       ('required', '=', False),
                       ('ttype', 'not in', ('one2many', 'many2many'))
                   ]
               """,
        help="Required fields and relational fields (one2many, many2many) are not allowed."
    )

    offload_mode = fields.Selection(
        [("manual", "Manual"), ("scheduled", "Scheduled"), ("both", "Manual + Scheduled")],
        default="manual",
        required=True,
    )
    delete_mode = fields.Selection(
        [("manual", "Manual"), ("scheduled", "Scheduled"), ("both", "Manual + Scheduled")],
        default="scheduled",
        required=True,
    )

    # Offload rules
    offload_domain = fields.Char(
        string="Offload Domain",
        help="Optional domain in Python list syntax, e.g. [('state','=','done')]. Leave empty for all records.",
    )
    archive_age_days = fields.Integer(default=0)

    # Delete rules
    delete_age_days = fields.Integer(default=30)

    # Scheduled delete settings
    interval_number = fields.Integer(default=7)
    interval_type = fields.Selection(
        [("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        default="days",
        required=True,
    )
    batch_size = fields.Integer(default=500)
    last_run_at = fields.Datetime(readonly=True)
    next_run_at = fields.Datetime(readonly=True)

    # Scheduled offload settings
    offload_interval_number = fields.Integer(default=7)
    offload_interval_type = fields.Selection(
        [("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        default="days",
        required=True,
    )
    offload_batch_size = fields.Integer(default=200)
    last_offload_run_at = fields.Datetime(readonly=True)
    next_offload_run_at = fields.Datetime(readonly=True)

    active = fields.Boolean(default=True)
    injected_view_id = fields.Many2one("ir.ui.view", readonly=True)

    @api.constrains("interval_number")
    def _check_interval(self):
        for rec in self:
            if rec.interval_number <= 0:
                raise UserError(_("Delete interval number must be greater than 0."))

    @api.constrains("offload_interval_number")
    def _check_offload_interval(self):
        for rec in self:
            if rec.offload_interval_number <= 0:
                raise UserError(_("Offload interval number must be greater than 0."))

    @api.constrains("field_ids")
    def _check_fields_allowed(self):
        for rec in self:
            for f in rec.field_ids:
                if f.ttype not in ALLOWED_TYPES:
                    raise UserError(_("Field type not supported for offload in Phase 1: %s (%s)") % (f.name, f.ttype))
                if f.ttype in ("one2many", "many2many"):
                    raise UserError(_("x2many fields are not supported for offload in Phase 1: %s") % f.name)

    def _get_field_names_and_types(self):
        self.ensure_one()
        return [(f.name, f.ttype) for f in self.field_ids]

    def _compute_next_run(self):
        self.ensure_one()
        return fields.Datetime.add(fields.Datetime.now(), **{self.interval_type: self.interval_number})

    def _compute_next_offload_run(self):
        self.ensure_one()
        return fields.Datetime.add(fields.Datetime.now(), **{self.offload_interval_type: self.offload_interval_number})

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._ensure_injected_buttons()
            if not rec.next_run_at:
                rec.next_run_at = rec._compute_next_run()
            if not rec.next_offload_run_at:
                rec.next_offload_run_at = rec._compute_next_offload_run()
        return recs

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._ensure_injected_buttons()
            rec._ensure_server_actions()
            if any(k in vals for k in ("interval_number", "interval_type")):
                rec.next_run_at = rec._compute_next_run()
            if any(k in vals for k in ("offload_interval_number", "offload_interval_type")):
                rec.next_offload_run_at = rec._compute_next_offload_run()
        return res

    def _ensure_injected_buttons(self):
        self.ensure_one()

        if not self.model_name:
            return

        View = self.env["ir.ui.view"].sudo()

        base_form = View.search(
            [
                ("model", "=", self.model_name),
                ("type", "=", "form"),
                ("inherit_id", "=", False),
            ],
            order="priority asc, id asc",
            limit=1,
        )
        if not base_form:
            return

        try:
            arch_tree = etree.fromstring(base_form.arch_db.encode("utf-8"))
        except Exception:
            return

        has_header = bool(arch_tree.xpath("//form/header"))

        if has_header:
            arch = """
            <data>
                <xpath expr="//form/header" position="inside">
                    <button name="action_external_offload" type="object"
                            string="Offload" class="btn-primary"
                            groups="external_archive_manager.group_external_archive_manager"/>
                    <button name="action_external_retrieve" type="object"
                            string="Retrieve" class="btn-secondary"
                            groups="external_archive_manager.group_external_archive_manager"/>
                    <button name="action_external_delete" type="object"
                            string="Delete External" class="btn-danger"
                            confirm="This will permanently delete archived data from external DB. Continue?"
                            groups="external_archive_manager.group_external_archive_admin"/>
                </xpath>
            </data>
            """
        else:
            arch = """
            <data>
                <xpath expr="//sheet" position="before">
                    <header>
                        <button name="action_external_offload" type="object"
                                string="Offload" class="btn-primary"
                                groups="external_archive_manager.group_external_archive_manager"/>
                        <button name="action_external_retrieve" type="object"
                                string="Retrieve" class="btn-secondary"
                                groups="external_archive_manager.group_external_archive_manager"/>
                        <button name="action_external_delete" type="object"
                                string="Delete External" class="btn-danger"
                                confirm="This will permanently delete archived data from external DB. Continue?"
                                groups="external_archive_manager.group_external_archive_admin"/>
                    </header>
                </xpath>
            </data>
            """

        view_name = f"external_archive_buttons_{self.model_name}"

        injected_view = View.search(
            [
                ("name", "=", view_name),
                ("model", "=", self.model_name),
                ("inherit_id", "=", base_form.id),
            ],
            limit=1,
        )

        if injected_view:
            injected_view.write({
                "arch_base": arch,
                "active": True,
            })
        else:
            View.create({
                "name": view_name,
                "type": "form",
                "model": self.model_name,
                "inherit_id": base_form.id,
                "arch_base": arch,
                "active": True,
            })

    def _ensure_server_actions(self):
        """Ensure Actions menu entries exist for list (tree) view."""
        self.ensure_one()
        if not self.model_name:
            return

        Action = self.env["ir.actions.server"].sudo()
        IrModel = self.env["ir.model"].sudo()

        model = IrModel.search([("model", "=", self.model_name)], limit=1)
        if not model:
            return

        actions = [
            {
                "name": "External Offload",
                "code": "records.action_external_offload()",
                "groups": "external_archive_manager.group_external_archive_manager",
            },
            {
                "name": "External Retrieve",
                "code": "records.action_external_retrieve()",
                "groups": "external_archive_manager.group_external_archive_manager",
            },
            {
                "name": "External Delete",
                "code": "records.action_external_delete()",
                "groups": "external_archive_manager.group_external_archive_admin",
            },
        ]

        for act in actions:
            group = self.env.ref(act["groups"], raise_if_not_found=False)

            existing = Action.search([
                ("name", "=", act["name"]),
                ("model_id", "=", model.id),
                ("binding_model_id", "=", model.id),
                ("binding_type", "=", "action"),
            ], limit=1)

            vals = {
                "name": act["name"],
                "model_id": model.id,
                "binding_model_id": model.id,
                "binding_type": "action",
                "binding_view_types": "list",  # ✅ REQUIRED
                "state": "code",
                "code": act["code"],
                "groups_id": [(6, 0, [group.id])] if group else False,
            }

            if existing:
                existing.write(vals)
            else:
                Action.create(vals)

    def _parse_domain(self):
        self.ensure_one()
        if not self.offload_domain:
            return []
        try:
            dom = ast.literal_eval(self.offload_domain)
            if not isinstance(dom, list):
                raise ValueError("Domain must be a list")
            return dom
        except Exception:
            raise UserError(_("Invalid offload domain format. Please use valid Python domain list syntax."))

    def _run_scheduled_offload(self):
        self.ensure_one()
        if self.offload_mode not in ("scheduled", "both"):
            return 0

        Model = self.env[self.model_name].sudo()
        dom = self._parse_domain()

        age_days = int(self.archive_age_days or 0)
        if age_days > 0:
            cutoff = fields.Datetime.subtract(fields.Datetime.now(), days=age_days)
            if "write_date" in Model._fields:
                dom += [("write_date", "<=", cutoff)]
            elif "create_date" in Model._fields:
                dom += [("create_date", "<=", cutoff)]

        # OR: at least one configured field is not empty
        non_empty = []
        for f in self.field_ids:
            if f.ttype in ("char", "text", "html", "json", "many2one", "date", "datetime", "selection"):
                non_empty.append((f.name, "!=", False))
            elif f.ttype in ("integer", "float", "monetary"):
                non_empty.append((f.name, "!=", 0))
            elif f.ttype == "boolean":
                non_empty.append((f.name, "=", True))

        if non_empty:
            dom += ["|"] * (len(non_empty) - 1) + non_empty

        recs = Model.search(dom, limit=int(self.offload_batch_size or 200))
        count = 0
        for r in recs:
            r.action_external_offload()
            count += 1
        return count

    def _run_scheduled_delete(self):
        self.ensure_one()
        db = self.env["external.archive.db.config"].sudo().search([("active", "=", True)], limit=1)
        if not db:
            raise UserError(_("No active External Archive DB configuration found."))

        conn = db._get_conn()
        deleted_total = 0
        try:
            with conn.cursor() as cr:
                cr.execute(
                    """
                    DELETE FROM odoo_external_archive
                    WHERE odoo_db_uuid=%s
                      AND model=%s
                      AND archived_at < (NOW() - (%s || ' days')::interval)
                    """,
                    (self.env.cr.dbname, self.model_name, int(self.delete_age_days or 0)),
                )
                deleted_total = cr.rowcount
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return deleted_total

    @api.model
    def cron_master_scheduler(self):
        now = fields.Datetime.now()
        configs = self.sudo().search([("active", "=", True)])

        for cfg in configs:
            # Offload schedule
            if cfg.offload_mode in ("scheduled", "both"):
                if not cfg.next_offload_run_at or cfg.next_offload_run_at <= now:
                    cfg._run_scheduled_offload()
                    cfg.last_offload_run_at = now
                    cfg.next_offload_run_at = cfg._compute_next_offload_run()

            # Delete schedule
            if cfg.delete_mode in ("scheduled", "both"):
                if not cfg.next_run_at or cfg.next_run_at <= now:
                    cfg._run_scheduled_delete()
                    cfg.last_run_at = now
                    cfg.next_run_at = cfg._compute_next_run()