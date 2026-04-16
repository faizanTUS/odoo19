# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv.expression import OR, TRUE_DOMAIN

_logger = logging.getLogger(__name__)


def _model_can_read(Model):
    """Whether the current user may read this model (ir.model.access). Odoo 17+ compatible."""
    try:
        empty = Model.browse()
        if hasattr(empty, "has_access"):
            return bool(empty.has_access("read"))
        Model.check_access_rights("read")
    except AccessError:
        return False
    return True


def _record_can_read(record):
    """Whether the current user may read this record (access + record rules). Odoo 17+ compatible."""
    if not record:
        return False
    try:
        if hasattr(record, "has_access"):
            return bool(record.has_access("read"))
        record.check_access_rights("read")
        record.check_access_rule("read")
    except AccessError:
        return False
    return True


# Order groups in the popover: business records users expect first, then the rest A–Z.
_GROUP_MODEL_PRIORITY = (
    "res.partner",
    "sale.order",
    "purchase.order",
    "account.move",
    "crm.lead",
    "project.task",
    "stock.picking",
)


def _name_search_context(model_name):
    """Extra env context so name_search + display_name match what users type (e.g. customer name on SO)."""
    if model_name == "sale.order":
        # Search/refine by partner ("Customer") and show "S00042 - Partner Name" in results.
        return {"sale_show_partner_name": True}
    return {}


def _global_search_domain_for_model(Model, query):
    """Return a domain for global search across user-selected models.

    Odoo 18+ :meth:`~odoo.models.Model.name_search` filters on ``display_name`` only.
    Searching ``display_name`` normally delegates to :meth:`~odoo.models.Model._search_display_name`,
    which uses ``_rec_names_search`` / ``_rec_name`` — but many list views also search extra
    columns (``ref``, ``client_order_ref``, customer, …). We rebuild that behaviour for **any**
    model the user selected.

    Returns ``None`` when we should fall back to :meth:`~odoo.models.Model.name_search`
    (e.g. no ``_rec_name`` / domain would match everything).
    """
    try:
        base = Model._search_display_name("ilike", query)
    except Exception:  # pylint: disable=broad-except
        return None
    if not base or base == TRUE_DOMAIN:
        return None

    extras = []
    for fname in ("client_order_ref", "ref", "vat"):
        field = Model._fields.get(fname)
        if field and field.store and field.type in ("char", "text"):
            extras.append([(fname, "ilike", query)])

    partner = Model._fields.get("partner_id")
    if (
        partner
        and partner.type == "many2one"
        and partner.comodel_name == "res.partner"
    ):
        extras.append([("partner_id", "ilike", query)])

    if not extras:
        return base
    return OR([base] + extras)


# Server-side only: maps suggestion presets to safe domains (never trust arbitrary domains from the client).
_BROWSE_PRESET_DOMAINS = {
    ("account.move", "customer_invoices"): [("move_type", "in", ("out_invoice", "out_refund"))],
}

# Window actions used for "Open full list in new tab". Model-only URLs (/odoo/<model>) rely on
# sessionStorage and do not work in a fresh tab; real action ids load without that cache.
_PRESET_LIST_ACTION_XMLID = {
    ("account.move", "customer_invoices"): "account.action_move_out_invoice_type",
}
_DEFAULT_LIST_ACTION_XMLID = {
    "res.partner": "contacts.action_contacts",
    "sale.order": "sale.action_quotations",
    "purchase.order": "purchase.purchase_rfq",
    "product.product": "product.product_normal_action",
    "account.move": "account.action_move_out_invoice_type",
}

# When the user has not chosen any models in preferences, search these (if installed and readable).
_FALLBACK_GLOBAL_SEARCH_MODELS = (
    "res.partner",
    "sale.order",
    "purchase.order",
    "account.move",
    "product.product",
)


def _effective_global_search_models(env, user):
    """Models to search: explicit user selection, or safe defaults if empty."""
    selected = user.global_search_model_ids.sorted("name")
    if selected:
        return selected

    # Use a simple request-level cache to avoid redundant ir.model searches in the same request
    if hasattr(request, "tus_global_search_models"):
        return request.tus_global_search_models

    IrModel = env["ir.model"].sudo()
    out = env["ir.model"].browse()
    
    # Search all fallback models at once instead of in a loop
    ims = IrModel.search([("model", "in", _FALLBACK_GLOBAL_SEARCH_MODELS)])
    model_to_im = {m.model: m for m in ims}

    for name in _FALLBACK_GLOBAL_SEARCH_MODELS:
        im = model_to_im.get(name)
        if not im:
            continue
        try:
            Model = env[name]
        except KeyError:
            continue
        if not getattr(Model, "_auto", False) or not _model_can_read(Model):
            continue
        out |= im
    
    request.tus_global_search_models = out
    return out


def _browse_domain(model_name, browse_preset):
    """Return a safe search domain for browse mode."""
    if browse_preset:
        key = (model_name, browse_preset)
        if key in _BROWSE_PRESET_DOMAINS:
            return list(_BROWSE_PRESET_DOMAINS[key])
    return []


def _resolve_list_action_ref(env, model_name, browse_preset):
    """Return ir.actions.act_window record or empty recordset for full-list navigation."""
    Act = env["ir.actions.act_window"]
    xmlid = _PRESET_LIST_ACTION_XMLID.get((model_name, browse_preset))
    if not xmlid:
        xmlid = _DEFAULT_LIST_ACTION_XMLID.get(model_name)
    if xmlid:
        try:
            act = env.ref(xmlid, raise_if_not_found=False)
        except Exception:  # pylint: disable=broad-except
            act = Act.browse()
        if act and act._name == "ir.actions.act_window" and act.exists() and _record_can_read(act):
            return act
    try:
        found = Act.search([("res_model", "=", model_name)], order="id asc", limit=1)
    except Exception:  # pylint: disable=broad-except
        return Act.browse()
    if found and _record_can_read(found):
        return found
    return Act.browse()


def _user_may_browse_model(env, user, model_name):
    """Respect per-user whitelist; empty selection uses built-in defaults (same as text search)."""
    model_name = (model_name or "").strip()
    if not model_name:
        return False
    allowed = set(_effective_global_search_models(env, user).mapped("model"))
    return model_name in allowed


def _search_order(Model):
    if "write_date" in Model._fields:
        return "write_date desc, id desc"
    return "id desc"


class GlobalSearchController(http.Controller):

    @http.route("/tus_smart_global_search/browse", type="json", auth="user")
    def browse(self, model, browse_preset=None, limit=80):
        """Load recent records for a single model (suggestion chips: show all contacts, orders, etc.)."""
        try:
            model = (model or "").strip()
            if not model:
                return {"groups": []}

            user = request.env.user
            if not _user_may_browse_model(request.env, user, model):
                return {"groups": []}

            try:
                Model = request.env[model]
            except KeyError:
                _logger.debug("tus_smart_global_search browse: model %s not in registry", model)
                return {"groups": []}

            if not getattr(Model, "_auto", False) or not _model_can_read(Model):
                return {"groups": []}

            domain = _browse_domain(model, browse_preset)
            ctx = _name_search_context(model)
            Model = Model.with_context(**ctx)

            try:
                records = Model.search(domain, limit=min(int(limit or 80), 200), order=_search_order(Model))
            except Exception as e:
                _logger.debug("tus_smart_global_search browse search failed for %s — %s", model, e)
                return {"groups": []}

            if not records:
                return {"groups": []}

            # Optimization: Never read binary fields (image_1920) in search results.
            # It's an order of magnitude faster to let the browser load them as needed.
            has_image_field = "image_128" in Model._fields or "image_1920" in Model._fields
            fields_to_read = ["display_name"]

            try:
                rows = records.read(fields_to_read)
            except Exception as e:
                _logger.debug("tus_smart_global_search browse read failed for %s — %s", model, e)
                return {"groups": []}

            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "display_name": row["display_name"] or "",
                    "has_image": bool(has_image_field),
                })

            ir_rec = request.env["ir.model"].sudo().search([("model", "=", model)], limit=1)
            group_name = ir_rec.name if ir_rec else model

            return {
                "groups": [{
                    "model": model,
                    "name": group_name,
                    "results": results,
                }],
            }
        except Exception:
            _logger.exception("tus_smart_global_search: browse endpoint failed")
            return {"groups": []}

    @http.route("/tus_smart_global_search/browse_action", type="json", auth="user")
    def browse_action(self, model, browse_preset=None):
        """Return a window action to open the full list view (pagination, filters) for browse chips."""
        model = (model or "").strip()
        if not model:
            return {}

        user = request.env.user
        if not _user_may_browse_model(request.env, user, model):
            return {}

        try:
            Model = request.env[model]
        except KeyError:
            return {}

        if not getattr(Model, "_auto", False) or not _model_can_read(Model):
            return {}

        domain = _browse_domain(model, browse_preset)
        ir_rec = request.env["ir.model"].sudo().search([("model", "=", model)], limit=1)
        name = ir_rec.name if ir_rec else model

        # Web client requires `views` (not only view_mode); otherwise action_service
        # crashes in _preprocessAction when mapping action.views.
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "res_model": model,
            "views": [[False, "list"], [False, "form"]],
            "domain": domain,
            "target": "current",
        }

    @http.route("/tus_smart_global_search/browse_list_nav", type="json", auth="user")
    def browse_list_nav(self, model, browse_preset=None):
        """Resolve a real window action id for URLs that open the full list in a new tab."""
        model = (model or "").strip()
        if not model:
            return {}

        user = request.env.user
        if not _user_may_browse_model(request.env, user, model):
            return {}

        try:
            request.env[model]
        except KeyError:
            return {}

        act = _resolve_list_action_ref(request.env, model, browse_preset)
        if not act:
            return {}
        return {"action": act.id}

    @http.route("/tus_smart_global_search/open_record_action", type="json", auth="user")
    def open_record_action(self, model, res_id):
        """Return a valid act_window for opening a record (same as get_formview_action, JSON-safe)."""
        model = (model or "").strip()
        if not model:
            return {}
        try:
            res_id = int(res_id)
        except (TypeError, ValueError):
            return {}
        try:
            record = request.env[model].browse(res_id)
        except KeyError:
            return {}
        if not record.exists() or not _record_can_read(record):
            return {}
        action = record.get_formview_action()
        # Ensure views are lists for JSON (tuples → list)
        if action.get("views"):
            action["views"] = [list(v) if isinstance(v, tuple) else v for v in action["views"]]
        return request.env["ir.actions.act_window"]._sanitize_act_window_dict_for_web_client(action)

    @http.route("/tus_smart_global_search/search", type="json", auth="user")
    def search(self, query, limit_per_model=40, max_models=50):
        """Return matching record groups; never raises (JSON-RPC must stay success for the client)."""
        try:
            query = (query or "").strip()
            if not query or len(query) < 2:
                return {"groups": []}

            user = request.env.user
            model_recs = _effective_global_search_models(request.env, user)[:max_models]
            if not model_recs:
                return {"groups": []}

            # Search each model
            groups = []
            for rec in model_recs:
                model_name = rec.model
                try:
                    Model = request.env[model_name]
                except KeyError:
                    _logger.debug("tus_smart_global_search: model %s not in registry, skipping", model_name)
                    continue

                if not Model._auto:
                    continue

                ctx = _name_search_context(model_name)
                Model = Model.with_context(**ctx)

                domain = _global_search_domain_for_model(Model, query)
                if domain is not None:
                    try:
                        records = Model.search(
                            domain,
                            limit=limit_per_model,
                            order=_search_order(Model),
                        )
                    except Exception as e:
                        _logger.debug(
                            "tus_smart_global_search: domain search failed for %s — %s",
                            model_name,
                            e,
                        )
                        continue
                else:
                    try:
                        name_search_result = Model.name_search(
                            query, args=[], operator="ilike", limit=limit_per_model
                        )
                    except Exception as e:
                        _logger.debug(
                            "tus_smart_global_search: name_search failed for %s — %s",
                            model_name,
                            e,
                        )
                        continue

                    if not name_search_result:
                        continue

                    ids = [pair[0] for pair in name_search_result]
                    records = Model.browse(ids)

                if not records:
                    continue

                # Optimization: Never read binary fields (image_1920) in search results.
                # It's an order of magnitude faster to let the browser load them as needed.
                has_image_field = "image_128" in Model._fields or "image_1920" in Model._fields
                fields_to_read = ["display_name"]

                try:
                    rows = records.read(fields_to_read)
                except Exception as e:
                    _logger.debug("tus_smart_global_search: read failed for %s — %s", model_name, e)
                    continue

                results = []
                for row in rows:
                    results.append({
                        "id": row["id"],
                        "display_name": row["display_name"] or "",
                        "has_image": bool(has_image_field),
                    })

                groups.append({
                    "model": model_name,
                    "name": rec.name or model_name,
                    "results": results,
                })

            priority = {m: i for i, m in enumerate(_GROUP_MODEL_PRIORITY)}

            def _group_sort_key(g):
                m = g["model"]
                return (priority.get(m, len(priority)), (g["name"] or "").lower(), m)

            groups.sort(key=_group_sort_key)

            return {"groups": groups}
        except Exception:
            _logger.exception("tus_smart_global_search: search endpoint failed")
            return {"groups": []}

    @http.route("/tus_smart_global_search/config", type="json", auth="user")
    def get_config(self):
        try:
            user = request.env.user
            effective = _effective_global_search_models(request.env, user)
            allowed_models = list(effective.mapped("model"))
            return {
                "configured": bool(user.global_search_model_ids),
                "model_count": len(effective),
                "allowed_models": allowed_models,
            }
        except Exception:
            _logger.exception("tus_smart_global_search: get_config failed")
            return {
                "configured": False,
                "model_count": 0,
                "allowed_models": [],
            }