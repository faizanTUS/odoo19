# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GlobalSearchController(http.Controller):

    @http.route("/global_search/search", type="jsonrpc", auth="user")
    def search(self, query, limit_per_model=10, max_models=50):
        query = (query or "").strip()
        if not query or len(query) < 2:
            return {"groups": []}

        user = request.env.user
        IrModel = request.env["ir.model"]

        if user.global_search_model_ids:
            # Use the user's personal selection
            model_recs = user.global_search_model_ids.sorted("name")[:max_models]
        else:
            # Fallback: all eligible models (same as before)
            IrModel = request.env["ir.model"].sudo()
            model_recs = IrModel.search([
                ("is_mail_thread", "=", True),
            ], order="name", limit=max_models)

            # Filter by actual access rights of the current user
            accessible_models = []
            for rec in model_recs:
                try:
                    Model = request.env[rec.model]
                    if Model._auto and request.env[rec.model].check_access_rights('read', raise_exception=False):
                        accessible_models.append(rec)
                except Exception:
                    continue

            model_recs = accessible_models[:max_models]

        # Search each model
        groups = []
        for rec in model_recs:
            model_name = rec.model
            try:
                Model = request.env[model_name]
            except KeyError:
                _logger.debug("global_search: model %s not in registry, skipping", model_name)
                continue

            if not Model._auto:
                continue

            try:
                name_search_result = Model.name_search(
                    query, domain=[], operator="ilike", limit=limit_per_model
                )
            except Exception as e:
                _logger.debug("global_search: name_search failed for %s — %s", model_name, e)
                continue

            if not name_search_result:
                continue

            ids = [pair[0] for pair in name_search_result]
            records = Model.browse(ids)

            has_image = "image_1920" in Model._fields
            fields_to_read = ["display_name", "id"]
            if has_image:
                fields_to_read.append("image_1920")

            try:
                rows = records.read(fields_to_read)
            except Exception as e:
                _logger.debug("global_search: read failed for %s — %s", model_name, e)
                continue

            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "display_name": row["display_name"] or "",
                    "has_image": bool(has_image and row.get("image_1920")),
                })

            groups.append({
                "model": model_name,
                "name": rec.name or model_name,
                "results": results,
            })

        return {"groups": groups}

    @http.route("/global_search/config", type="jsonrpc", auth="user")
    def get_config(self):
        user = request.env.user
        return {
            "configured": bool(user.global_search_model_ids),
            "model_count": len(user.global_search_model_ids),
        }