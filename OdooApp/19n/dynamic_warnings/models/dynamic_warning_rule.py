# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import ast
import logging
import re
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class DynamicWarningRule(models.Model):
    _name = "dynamic.warning.rule"
    _description = "Dynamic Warning Rule"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    model_id = fields.Many2one("ir.model", string="Target Model", required=True, ondelete="cascade")
    model_name = fields.Char(related="model_id.model", store=True, readonly=True)
    domain = fields.Text(
        string="Conditions",
        default="[]",
        help="Odoo domain: list of conditions, e.g. [('qty_available', '<', 10)] or [('phone', '=', False)]",
    )
    message = fields.Text(
        string="Warning Message",
        required=True,
        translate=True,
        help="Use {field_name} to insert record values, e.g. 'Stock is {qty_available} units'",
    )
    warning_type = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        string="Alert Style",
        default="warning",
        required=True,
    )
    group_ids = fields.Many2many(
        "res.groups",
        "dynamic_warning_rule_group_rel",
        "rule_id",
        "group_id",
        string="Restrict to User Groups",
        help="Leave empty to show to all users. Otherwise only users in at least one of these groups see this alert.",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", string="Company")
    date_start = fields.Date(string="Valid From")
    date_end = fields.Date(string="Valid To")

    @api.constrains("domain")
    def _check_domain(self):
        for rule in self:
            if not rule.domain or rule.domain.strip() == "":
                continue
            try:
                parsed = ast.literal_eval(rule.domain.strip())
                if not isinstance(parsed, list):
                    raise ValidationError(
                        _("Conditions must be a list (domain), e.g. [('field', '=', value)]")
                    )
            except (ValueError, SyntaxError) as e:
                raise ValidationError(
                    _("Invalid domain: %s. Use a valid Python list, e.g. [('qty_available', '<', 10)]")
                    % str(e)
                ) from e

    def _get_domain(self):
        """Return parsed domain list. Empty list if invalid or empty."""
        self.ensure_one()
        if not self.domain or not self.domain.strip():
            return []
        try:
            return ast.literal_eval(self.domain.strip())
        except (ValueError, SyntaxError):
            return []

    def _get_domain_field_names(self, domain):
        """Extract field names from a domain list (for pre-loading computed fields)."""
        names = set()
        for item in domain:
            if isinstance(item, (list, tuple)) and len(item) >= 1:
                if isinstance(item[0], str) and item[0] not in ("|", "&", "!"):
                    names.add(item[0])
        return list(names)

    def _replace_placeholders(self, message, record):
        """Replace {field_name} in message with record values."""




        if not message or not record:
            return message
        result = message
        # Match {field_name} but not doubled braces
        for match in re.finditer(r"\{(\w+)\}", result):
            field_name = match.group(1)
            if field_name in record._fields:
                try:
                    value = record[field_name]
                    if value is False or value is None:
                        value = ""
                    result = result.replace(match.group(0), str(value))
                except Exception:
                    pass
        return result

    def _rule_applies_for_user(self, rule):
        """Check if the current user is in one of the rule's groups (or no groups = all users)."""
        if not rule.group_ids:
            return True
        return bool(rule.group_ids & self.env.user.group_ids)

    def _rule_valid_dates(self, rule):
        """Check validity date range."""
        today = date.today()
        if rule.date_start and today < rule.date_start:
            return False
        if rule.date_end and today > rule.date_end:
            return False
        return True

    @api.model
    def get_warnings_for_record(self, model_name, res_id):
        _logger.warning("[DW] START model=%s res_id=%s", model_name, res_id)

        if not model_name or not res_id:
            _logger.warning("[DW] EXIT missing model/res_id")
            return []

        record = self.env[model_name].browse(res_id)
        if not record.exists():
            _logger.warning("[DW] EXIT record not found")
            return []

        rules = self.search([("model_id.model", "=", model_name), ("active", "=", True)])
        _logger.warning("[DW] rules_count=%s", len(rules))

        warnings = []
        for rule in rules:
            if rule.company_id and rule.company_id != self.env.company:
                continue

            if not self._rule_applies_for_user(rule):
                continue

            if not self._rule_valid_dates(rule):
                continue

            _logger.warning("[DW] rule=%s domain=%s", rule.id, rule.domain)

            domain = safe_eval(rule.domain or "[]")
            domain.append(("id", "=", res_id))

            matched = self.env[model_name].search(domain, limit=1)
            _logger.warning("[DW] rule=%s matched=%s", rule.id, bool(matched))

            if matched:
                msg = rule.message or "Warning triggered"
                typ = getattr(rule, "alert_type", None) or getattr(rule, "warning_type", None) or "warning"

                payload = {"message": msg, "type": typ}
                warnings.append(payload)
                _logger.warning("[DW] rule=%s APPEND %s", rule.id, payload)

        _logger.warning("[DW] RETURN %s", warnings)
        return warnings