# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Repair ACLs and group inheritance if CSV/XML did not apply cleanly."""

import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def _aac_fix_all(env):
    """Idempotent: safe to run on install, upgrade, or after bad data."""
    _aac_ensure_system_implies_manager(env)
    _aac_ensure_model_access(env)
    env.registry.clear_caches()


def _aac_rebuild_form_button_catalog(env):
    try:
        env["advanced.access.form.button"].rebuild_index()
    except Exception:
        _logger.exception("AAC form button catalog rebuild failed")


def _aac_rebuild_form_notebook_page_catalog(env):
    try:
        env["advanced.access.form.notebook.page"].rebuild_index()
    except Exception:
        _logger.exception("AAC form notebook page catalog rebuild failed")


def _aac_rebuild_catalogs(env):
    _aac_rebuild_form_button_catalog(env)
    _aac_rebuild_form_notebook_page_catalog(env)


def post_init_hook(cr, registry):
    """Odoo 16 passes cr and registry. Create env from cr."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _aac_fix_all(env)
    _aac_rebuild_catalogs(env)


def _aac_ensure_system_implies_manager(env):
    try:
        mgr = env.ref("advanced_access_control.group_advanced_access_manager")
        sysg = env.ref("base.group_system")
    except ValueError:
        return
    if mgr not in sysg.implied_ids:
        sysg.write({"implied_ids": [(4, mgr.id)]})


def _aac_ensure_model_access(env):
    try:
        mgr = env.ref("advanced_access_control.group_advanced_access_manager")
        sysg = env.ref("base.group_system")
    except ValueError:
        return
    IMA = env["ir.model.access"].sudo()
    IrModel = env["ir.model"].sudo()
    models = (
        "advanced.access.policy",
        "advanced.access.policy.model.line",
        "advanced.access.policy.field.line",
        "advanced.access.policy.menu.line",
        "advanced.access.policy.button.line",
        "advanced.access.policy.tab.line",
        "advanced.access.audit.log",
    )
    for model_name in models:
        model = IrModel.search([("model", "=", model_name)], limit=1)
        if not model:
            continue
        for group in (sysg, mgr):
            if IMA.search(
                [("model_id", "=", model.id), ("group_id", "=", group.id)], limit=1
            ):
                continue
            IMA.create(
                {
                    "name": "AAC fix %s %s" % (model_name, group.name),
                    "model_id": model.id,
                    "group_id": group.id,
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                    "perm_unlink": True,
                }
            )
