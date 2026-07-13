# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import ast
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def _literal_eval_domain(text):
    if not text or not text.strip():
        return []
    try:
        value = ast.literal_eval(text.strip())
    except (ValueError, SyntaxError) as e:
        raise ValidationError(_("Invalid domain literal: %s") % e) from e
    if not isinstance(value, (list, tuple)):
        raise ValidationError(_("Domain must evaluate to a list or tuple."))
    return list(value)


class AdvancedAccessPolicy(models.Model):
    _name = "advanced.access.policy"
    _description = "Advanced Access Control Policy"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    user_ids = fields.Many2many(
        "res.users",
        "advanced_access_policy_user_rel",
        "policy_id",
        "user_id",
        string="Users",
        help="Policies apply to these users in addition to any users in the selected groups.",
    )
    group_ids = fields.Many2many(
        "res.groups",
        "advanced_access_policy_group_rel",
        "policy_id",
        "group_id",
        string="Groups",
        help="All members of these groups receive this policy.",
    )
    global_readonly = fields.Boolean(
        string="Global read-only (UI + server)",
        help="Forms/lists open without create/edit; server blocks create, write, and unlink except on a built-in safe model list.",
    )
    hide_chatter = fields.Boolean(
        help="Hide mail chatter on form views for affected users.",
    )
    disable_debug = fields.Boolean(
        string="Disable developer / debug mode",
        help="Clears debug mode on each request and omits debug bundle hints for the session.",
    )
    enable_audit = fields.Boolean(
        string="Audit denials",
        help="Log rows when this policy denies an operation (model-level rules from this module).",
    )
    global_disable_import = fields.Boolean(
        string="Disable import",
        help="Hide the Import records menu on list/kanban for affected users (all models).",
    )
    global_disable_export = fields.Boolean(
        string="Disable export",
        help="Hide list export and block server export for affected users (all models). "
        "Per-model lines can still narrow further.",
    )
    global_disable_archive = fields.Boolean(
        string="Disable archive / unarchive",
        help="Hide Archive/Unarchive in the list action menu and block active toggles (all models).",
    )
    model_line_ids = fields.One2many(
        "advanced.access.policy.model.line", "policy_id", string="Model access"
    )
    field_line_ids = fields.One2many(
        "advanced.access.policy.field.line", "policy_id", string="Field access"
    )
    menu_line_ids = fields.One2many(
        "advanced.access.policy.menu.line", "policy_id", string="Hidden menus"
    )
    button_line_ids = fields.One2many(
        "advanced.access.policy.button.line", "policy_id", string="Hidden buttons"
    )
    tab_line_ids = fields.One2many(
        "advanced.access.policy.tab.line", "policy_id", string="Hidden notebook pages"
    )
    audit_log_ids = fields.One2many(
        "advanced.access.audit.log", "policy_id", string="Audit log"
    )

    @api.constrains("active", "user_ids", "group_ids")
    def _check_targets(self):
        for pol in self:
            if pol.active and not pol.user_ids and not pol.group_ids:
                raise ValidationError(
                    _("An active policy must include at least one user or one group.")
                )

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_all_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.env.registry.clear_all_caches()
        return recs

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_all_caches()
        return res


class AdvancedAccessPolicyModelLine(models.Model):
    _name = "advanced.access.policy.model.line"
    _description = "Policy model access line"

    policy_id = fields.Many2one(
        "advanced.access.policy", required=True, ondelete="cascade"
    )
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(related="model_id.model", store=True, readonly=True)
    allow_read = fields.Boolean(default=True)
    allow_create = fields.Boolean(default=True)
    allow_write = fields.Boolean(default=True)
    allow_unlink = fields.Boolean(
        default=True,
        help="When False, this module blocks unlink and hides delete in the UI. When True, unlink is still "
        "only possible if the user’s Odoo security groups already grant delete on the model "
        "(e.g. Salesperson has no unlink on sale.order; Sales Manager does).",
    )
    allow_export = fields.Boolean(
        default=True,
        help="When False, blocks export on the server and hides the list Export action (even if the user has "
        "“Access to export feature”).",
    )
    allow_duplicate = fields.Boolean(
        string="Allow duplicate",
        default=True,
        help="When False, blocks copy/duplicate and hides Duplicate in the Actions menu. Duplicate requires "
        "Allow Create: copying creates a new record, so if Create is unchecked here, duplicate is treated as off.",
    )
    allow_sidebar_cancel = fields.Boolean(
        string="Allow Cancel (Actions)",
        default=True,
        help="When False, hides sidebar Actions bound to this model whose title looks like a cancel wizard "
        "(e.g. “Cancel” on sales orders).",
    )
    allow_sidebar_send_email = fields.Boolean(
        string="Allow Send email (Actions)",
        default=True,
        help="When False, hides sidebar Actions bound to this model whose title suggests sending email "
        "(e.g. “Send an email” on sales orders).",
    )
    allow_import = fields.Boolean(
        default=True,
        help="When False, hides Import on list/kanban for this model (in addition to any global disable).",
    )
    allow_archive = fields.Boolean(
        default=True,
        help="When False, hides Archive/Unarchive and blocks changing active for matching records.",
    )
    hidden_report_ids = fields.Many2many(
        "ir.actions.report",
        string="Hidden reports",
        help="Reports removed from the Print menu for this model (pick a model first; only that model’s reports are offered).",
    )
    hidden_sidebar_action_ids_str = fields.Char(string="Hidden Actions (Store)", copy=False)
    hidden_sidebar_action_ids = fields.Many2many(
        "ir.actions.actions",
        string="Hidden sidebar actions",
        compute="_compute_hidden_sidebar_action_ids",
        inverse="_inverse_hidden_sidebar_action_ids",
        help="Actions bound to this model (Actions menu), e.g. Share or Send an email. Pick a model first. "
        "Links are stored per-model.",
    )

    @api.depends("hidden_sidebar_action_ids_str")
    def _compute_hidden_sidebar_action_ids(self):
        Action = self.env["ir.actions.actions"].sudo()
        for rec in self:
            ids = [
                int(i)
                for i in (rec.hidden_sidebar_action_ids_str or "").split(",")
                if i.strip()
            ]
            rec.hidden_sidebar_action_ids = Action.browse(ids).exists()

    def _inverse_hidden_sidebar_action_ids(self):
        for rec in self:
            rec.hidden_sidebar_action_ids_str = ",".join(
                str(i) for i in rec.hidden_sidebar_action_ids.ids
            )
    record_domain = fields.Char(
        help="Optional domain (Python literal list) restricting which records this line applies to. "
        "Empty means all records. Example: [('state', '=', 'draft')]"
    )

    @api.constrains("record_domain")
    def _check_record_domain(self):
        for line in self:
            if line.record_domain:
                _literal_eval_domain(line.record_domain)

    @api.onchange("model_id")
    def _onchange_aac_model_line_model(self):
        self.hidden_report_ids = False
        self.hidden_sidebar_action_ids = False

    @api.constrains("hidden_report_ids", "model_id")
    def _check_hidden_reports_model(self):
        for line in self:
            if not line.model_id:
                continue
            bad = line.hidden_report_ids.filtered(lambda r: r.model != line.model_name)
            if bad:
                raise ValidationError(
                    _("Hidden reports must belong to model %(model)s.")
                    % {"model": line.model_name}
                )

    @api.constrains("hidden_sidebar_action_ids", "model_id")
    def _check_hidden_sidebar_actions_model(self):
        for line in self:
            if not line.model_id:
                continue
            bad = line.hidden_sidebar_action_ids.filtered(
                lambda a: a.binding_model_id != line.model_id
            )
            if bad:
                raise ValidationError(
                    _("Hidden actions must be sidebar actions bound to model %(model)s.")
                    % {"model": line.model_name}
                )

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_all_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.env.registry.clear_all_caches()
        return recs

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_all_caches()
        return res


class AdvancedAccessPolicyFieldLine(models.Model):
    _name = "advanced.access.policy.field.line"
    _description = "Policy field modifier line"

    policy_id = fields.Many2one(
        "advanced.access.policy", required=True, ondelete="cascade"
    )
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(string="Model Name", related="model_id.model", store=True, readonly=True)
    ir_field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        ondelete="set null",
        domain="[('model_id', '=', model_id)]",
        help="Pick a field on the selected model (easier than typing the technical name).",
    )
    field_name = fields.Char(
        help="Technical field name (filled automatically when you choose a field above).",
    )
    modifier = fields.Selection(
        [
            ("invisible", "Invisible"),
            ("readonly", "Read-only"),
            ("required", "Required"),
        ],
        required=True,
        default="readonly",
    )
    apply_condition = fields.Char(
        string="When (expression)",
        help="Optional expression evaluated in the web client (Python-like, same as view modifiers). "
        "If set, the modifier applies only when this expression is true. "
        "Example: state in ('sale', 'done'). Leave empty to always apply.",
    )

    @api.onchange("model_id")
    def _onchange_aac_field_line_model(self):
        self.ir_field_id = False
        self.field_name = False

    @api.onchange("ir_field_id")
    def _onchange_aac_field_line_ir_field_id(self):
        if self.ir_field_id:
            self.field_name = self.ir_field_id.name

    @api.model
    def _aac_sync_field_name_from_vals(self, vals):
        fid = vals.get("ir_field_id")
        if fid:
            mf = self.env["ir.model.fields"].browse(fid)
            vals["field_name"] = mf.name

    @api.constrains("field_name", "model_id", "ir_field_id")
    def _check_field_exists(self):
        IrModelFields = self.env["ir.model.fields"].sudo()
        for line in self:
            if not line.model_id:
                continue
            if not line.ir_field_id and not line.field_name:
                raise ValidationError(_("Please select a field for each line."))
            if line.ir_field_id:
                if line.ir_field_id.model_id != line.model_id:
                    raise ValidationError(
                        _("The selected field does not belong to model %(model)s.")
                        % {"model": line.model_id.model}
                    )
                if line.field_name and line.field_name != line.ir_field_id.name:
                    raise ValidationError(
                        _("Field name does not match the selected field.")
                    )
                continue
            f = IrModelFields.search(
                [
                    ("model_id", "=", line.model_id.id),
                    ("name", "=", line.field_name),
                ],
                limit=1,
            )
            if not f:
                raise ValidationError(
                    _("Field %(field)s does not exist on model %(model)s.")
                    % {"field": line.field_name, "model": line.model_id.model}
                )

    def write(self, vals):
        vals = dict(vals)
        if vals.get("ir_field_id") is False:
            vals.setdefault("field_name", False)
        elif vals.get("ir_field_id"):
            self._aac_sync_field_name_from_vals(vals)
        res = super().write(vals)
        self.env.registry.clear_all_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        rows = []
        for vals in vals_list:
            v = dict(vals)
            self._aac_sync_field_name_from_vals(v)
            rows.append(v)
        recs = super().create(rows)
        self.env.registry.clear_all_caches()
        return recs

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_all_caches()
        return res


class AdvancedAccessPolicyMenuLine(models.Model):
    _name = "advanced.access.policy.menu.line"
    _description = "Policy hidden menu line"

    policy_id = fields.Many2one(
        "advanced.access.policy", required=True, ondelete="cascade"
    )
    model_id = fields.Many2one(
        "ir.model",
        ondelete="cascade",
        help="Menus offered include the full app subtree (e.g. all Sales menus) when that app has actions "
        "for this model—not only lines that open this model (e.g. Customers / res.partner appear for Sales Order).",
    )
    model_name = fields.Char(string="Model Name", related="model_id.model", store=True, readonly=True)
    aac_menu_candidate_ids = fields.Many2many(
        "ir.ui.menu",
        compute="_compute_aac_menu_candidate_ids",
        string="Menus for model",
    )
    menu_id = fields.Many2one("ir.ui.menu", required=True, ondelete="cascade")

    @api.depends("model_id")
    def _compute_aac_menu_candidate_ids(self):
        for line in self:
            if line.model_id:
                line.aac_menu_candidate_ids = line._aac_menus_for_model(
                    line.model_id.model
                )
            else:
                line.aac_menu_candidate_ids = False

    @api.model
    def _aac_menus_for_model(self, model_name):
        """Menus under the same app root(s) as actions for ``model_name``.

        We first find menus whose *own* action targets the model, walk each up to the top-level
        ``ir.ui.menu`` root, then return every menu ``child_of`` those roots (full Sales tree:
        Customers, Products, Reporting, etc.—not only Quotations/Orders).
        """
        Menu = self.env["ir.ui.menu"].sudo()
        if not model_name:
            return Menu.browse()
        IrModel = self.env["ir.model"].sudo()
        im = IrModel.search([("model", "=", model_name)], limit=1)
        refs = []
        ActWin = self.env["ir.actions.act_window"].sudo()
        for aw in ActWin.search([("res_model", "=", model_name)]):
            refs.append("ir.actions.act_window,%s" % aw.id)
        ActReport = self.env["ir.actions.report"].sudo()
        for ar in ActReport.search([("model", "=", model_name)]):
            refs.append("ir.actions.report,%s" % ar.id)
        if im:
            ActSrv = self.env["ir.actions.server"].sudo()
            for sv in ActSrv.search([("model_id", "=", im.id)]):
                refs.append("ir.actions.server,%s" % sv.id)
        if not refs:
            return Menu.browse()
        refs = list(dict.fromkeys(refs))
        direct = Menu.search([("action", "in", refs)])
        if not direct:
            return Menu.browse()

        roots = set()
        for d in direct:
            m = d
            while m.parent_id:
                m = m.parent_id
            roots.add(m.id)

        rid_list = sorted(roots)
        if len(rid_list) == 1:
            subtree = Menu.search([("id", "child_of", rid_list[0])])
        else:
            dom = []
            for i, rid in enumerate(rid_list):
                if i:
                    dom.insert(0, "|")
                dom.append(("id", "child_of", rid))
            subtree = Menu.search(dom)
        return subtree.sorted("complete_name")

    @api.onchange("model_id")
    def _onchange_aac_menu_line_model(self):
        self.menu_id = False

    @api.constrains("menu_id", "model_id")
    def _check_menu_matches_model(self):
        for line in self:
            if not line.model_id:
                raise ValidationError(
                    _("Each hidden-menu line needs a model: choose the model, then pick a menu to hide.")
                )
            if not line.menu_id:
                raise ValidationError(_("Choose a menu to hide on each line."))
            allowed = line._aac_menus_for_model(line.model_id.model)
            if line.menu_id.id not in allowed.ids:
                raise ValidationError(
                    _("Menu “%(menu)s” is not allowed for model %(model)s. "
                      "Pick the model first, then choose a menu from the filtered list.")
                    % {"menu": line.menu_id.display_name, "model": line.model_id.model}
                )

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_all_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.env.registry.clear_all_caches()
        return recs

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_all_caches()
        return res


class AdvancedAccessPolicyButtonLine(models.Model):
    _name = "advanced.access.policy.button.line"
    _description = "Policy hidden button line"

    policy_id = fields.Many2one(
        "advanced.access.policy", required=True, ondelete="cascade"
    )
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(string="Model Name", related="model_id.model", store=True, readonly=True)
    form_button_id = fields.Many2one(
        "advanced.access.form.button",
        string="Button",
        ondelete="set null",
        domain="[('model_id', '=', model_id)]",
        help="Pick a button from indexed form views for the selected model.",
    )
    button_name = fields.Char(
        help="XML name attribute (e.g. action_confirm); filled when you choose a button above.",
    )

    @api.onchange("model_id")
    def _onchange_aac_button_line_model(self):
        self.form_button_id = False
        self.button_name = False

    @api.onchange("form_button_id")
    def _onchange_aac_button_line_form_button(self):
        if self.form_button_id:
            self.button_name = self.form_button_id.xml_name

    @api.model
    def _aac_sync_button_name_from_vals(self, vals):
        bid = vals.get("form_button_id")
        if bid:
            row = self.env["advanced.access.form.button"].browse(bid)
            vals["button_name"] = row.xml_name

    @api.constrains("button_name", "model_id", "form_button_id")
    def _check_button_line(self):
        for line in self:
            if not line.model_id:
                continue
            if not line.form_button_id and not line.button_name:
                raise ValidationError(_("Please select a button or enter its XML name."))
            if line.form_button_id:
                if line.form_button_id.model_id != line.model_id:
                    raise ValidationError(
                        _("The selected button does not belong to model %(model)s.")
                        % {"model": line.model_id.model}
                    )
                if line.button_name and line.button_name != line.form_button_id.xml_name:
                    raise ValidationError(
                        _("Button name does not match the selected button.")
                    )

    def write(self, vals):
        vals = dict(vals)
        if vals.get("form_button_id") is False:
            vals.setdefault("button_name", False)
        elif vals.get("form_button_id"):
            self._aac_sync_button_name_from_vals(vals)
        res = super().write(vals)
        self.env.registry.clear_all_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        rows = []
        for vals in vals_list:
            v = dict(vals)
            self._aac_sync_button_name_from_vals(v)
            rows.append(v)
        recs = super().create(rows)
        self.env.registry.clear_all_caches()
        return recs

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_all_caches()
        return res


class AdvancedAccessPolicyTabLine(models.Model):
    _name = "advanced.access.policy.tab.line"
    _description = "Policy hidden notebook page line"

    policy_id = fields.Many2one(
        "advanced.access.policy", required=True, ondelete="cascade"
    )
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(string="Model Name", related="model_id.model", store=True, readonly=True)
    form_notebook_page_id = fields.Many2one(
        "advanced.access.form.notebook.page",
        string="Notebook page",
        ondelete="set null",
        domain="[('model_id', '=', model_id)]",
        help="Choose a tab from indexed form views for the selected model.",
    )
    page_string = fields.Char(
        help="Exact ``string`` on the form's <page> (case-sensitive). Filled when you pick a page above, "
        "or type manually if it is not listed.",
    )

    @api.onchange("model_id")
    def _onchange_aac_tab_line_model(self):
        self.form_notebook_page_id = False
        self.page_string = False

    @api.onchange("form_notebook_page_id")
    def _onchange_aac_tab_line_form_notebook_page(self):
        if self.form_notebook_page_id:
            self.page_string = self.form_notebook_page_id.page_string

    @api.model
    def _aac_sync_page_string_from_vals(self, vals):
        pid = vals.get("form_notebook_page_id")
        if pid:
            row = self.env["advanced.access.form.notebook.page"].browse(pid)
            vals["page_string"] = row.page_string

    @api.constrains("page_string", "model_id", "form_notebook_page_id")
    def _check_tab_line(self):
        for line in self:
            if not line.model_id:
                continue
            if not line.form_notebook_page_id and not (line.page_string or "").strip():
                raise ValidationError(
                    _("Please select a notebook page or enter the page title (string).")
                )
            if line.form_notebook_page_id:
                if line.form_notebook_page_id.model_id != line.model_id:
                    raise ValidationError(
                        _("The selected page does not belong to model %(model)s.")
                        % {"model": line.model_id.model}
                    )
                if (
                    line.page_string
                    and line.page_string != line.form_notebook_page_id.page_string
                ):
                    raise ValidationError(
                        _("Page title does not match the selected notebook page.")
                    )

    def write(self, vals):
        vals = dict(vals)
        if vals.get("form_notebook_page_id") is False:
            vals.setdefault("page_string", False)
        elif vals.get("form_notebook_page_id"):
            self._aac_sync_page_string_from_vals(vals)
        res = super().write(vals)
        self.env.registry.clear_all_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        rows = []
        for vals in vals_list:
            v = dict(vals)
            self._aac_sync_page_string_from_vals(v)
            rows.append(v)
        recs = super().create(rows)
        self.env.registry.clear_all_caches()
        return recs

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_all_caches()
        return res


class AdvancedAccessAuditLog(models.Model):
    _name = "advanced.access.audit.log"
    _description = "Advanced access denial audit"
    _order = "create_date desc"

    policy_id = fields.Many2one("advanced.access.policy", ondelete="set null")
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade")
    model_name = fields.Char(string="Model")
    operation = fields.Char()
    detail = fields.Text()
