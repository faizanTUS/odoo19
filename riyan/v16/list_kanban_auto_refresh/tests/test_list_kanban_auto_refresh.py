# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Odoo tests for list_kanban_auto_refresh (Odoo 16).

Run (adjust ``-c``, ``-d``, ``--data-dir``, ``--http-port`` to your environment)::

    /usr/bin/python3.10 /home/tus/workspace/odoo16/odoo/odoo-bin \\
        -c /path/to/your.conf \\
        -d YOUR_DATABASE \\
        -u list_kanban_auto_refresh --test-enable --stop-after-init \\
        --test-tags=/list_kanban_auto_refresh \\
        --data-dir=/tmp/odoo_session_test --http-port=18089

``HttpCase`` needs a writable ``--data-dir`` (sessions). ``TransactionCase`` does not.
"""

import json
from uuid import uuid4

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests import common


def _icp_truthy(param_value):
    """Match ir.http logic: enabled when param is 1/true/yes (string or bool)."""
    if isinstance(param_value, bool):
        return param_value
    return str(param_value or "").lower() in ("1", "true", "yes")


@tagged("post_install", "-at_install")
class TestListKanbanAutoRefreshConfig(common.TransactionCase):
    """res.config.settings and ir.config_parameter behaviour for auto-refresh."""

    def setUp(self):
        super().setUp()
        self.icp = self.env["ir.config_parameter"].sudo()

    def test_settings_execute_persists_parameters(self):
        self.icp.set_param("list_kanban_auto_refresh.enabled", "False")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "10000")
        settings = self.env["res.config.settings"].create(
            {
                "list_kanban_auto_refresh_enabled": True,
                "list_kanban_auto_refresh_interval_ms": 15000,
            }
        )
        settings.execute()
        self.assertTrue(_icp_truthy(self.icp.get_param("list_kanban_auto_refresh.enabled")))
        self.assertEqual(
            str(self.icp.get_param("list_kanban_auto_refresh.interval_ms")), "15000"
        )

    def test_settings_execute_can_disable_globally(self):
        self.icp.set_param("list_kanban_auto_refresh.enabled", "True")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "5000")
        settings = self.env["res.config.settings"].create(
            {
                "list_kanban_auto_refresh_enabled": False,
                "list_kanban_auto_refresh_interval_ms": 8000,
            }
        )
        settings.execute()
        self.assertFalse(_icp_truthy(self.icp.get_param("list_kanban_auto_refresh.enabled")))
        self.assertEqual(
            str(self.icp.get_param("list_kanban_auto_refresh.interval_ms")), "8000"
        )

    def test_minimum_interval_ms_is_accepted(self):
        settings = self.env["res.config.settings"].create(
            {"list_kanban_auto_refresh_interval_ms": 1000}
        )
        self.assertEqual(settings.list_kanban_auto_refresh_interval_ms, 1000)

    def test_interval_below_minimum_raises_validation(self):
        with self.assertRaises(ValidationError):
            self.env["res.config.settings"].create(
                {"list_kanban_auto_refresh_interval_ms": 500}
            )


@tagged("post_install", "-at_install")
class TestListKanbanAutoRefreshSessionInfo(common.HttpCase):
    """ir.http.session_info exposes list_kanban_auto_refresh for logged-in users."""

    def setUp(self):
        super().setUp()
        self.payload = json.dumps({"jsonrpc": "2.0", "method": "call", "id": str(uuid4())})
        self.headers = {"Content-Type": "application/json"}

    def _get_session_info_result(self):
        response = self.url_open(
            "/web/session/get_session_info", data=self.payload, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["result"]

    def test_session_info_includes_defaults_when_logged_in(self):
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("list_kanban_auto_refresh.enabled", "False")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "10000")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        result = self._get_session_info_result()

        self.assertIn("list_kanban_auto_refresh", result)
        cfg = result["list_kanban_auto_refresh"]
        self.assertFalse(cfg["global_enabled"])
        self.assertEqual(cfg["interval_ms"], 10000)

    def test_session_info_reflects_system_parameters(self):
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("list_kanban_auto_refresh.enabled", "true")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "2500")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        cfg = self._get_session_info_result()["list_kanban_auto_refresh"]

        self.assertTrue(cfg["global_enabled"])
        self.assertEqual(cfg["interval_ms"], 2500)

    def test_session_info_treats_yes_as_enabled(self):
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("list_kanban_auto_refresh.enabled", "yes")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "3000")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        cfg = self._get_session_info_result()["list_kanban_auto_refresh"]

        self.assertTrue(cfg["global_enabled"])
        self.assertEqual(cfg["interval_ms"], 3000)

    def test_session_info_preserves_large_interval(self):
        """Values above the minimum are passed through unchanged (no upper cap)."""
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("list_kanban_auto_refresh.enabled", "1")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "120000")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        cfg = self._get_session_info_result()["list_kanban_auto_refresh"]

        self.assertEqual(cfg["interval_ms"], 120000)

    def test_session_info_clamps_interval_minimum(self):
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("list_kanban_auto_refresh.enabled", "1")
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "100")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        cfg = self._get_session_info_result()["list_kanban_auto_refresh"]

        self.assertEqual(cfg["interval_ms"], 1000)

    def test_session_info_invalid_interval_falls_back(self):
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("list_kanban_auto_refresh.interval_ms", "not_a_number")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        cfg = self._get_session_info_result()["list_kanban_auto_refresh"]

        self.assertEqual(cfg["interval_ms"], 10000)
