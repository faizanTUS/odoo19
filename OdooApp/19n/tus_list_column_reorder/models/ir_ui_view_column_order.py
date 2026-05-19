# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import json
from odoo import api, fields, models

class IrUiViewColumnOrder(models.Model):
    _name = "ir.ui.view.column.order"
    _description = "User Column Order for List Views"

    user_id = fields.Many2one(
        "res.users", required=True, ondelete="cascade",
        default=lambda self: self.env.user
    )
    view_id = fields.Many2one(
        "ir.ui.view", ondelete="cascade",
        domain=[("type", "=", "tree")]
    )
    model = fields.Char(required=True)
    order_json = fields.Text()
    arch_hash = fields.Char()

    _sql_constraints = [
        (
            "unique_user_model_arch",
            "unique(user_id, model, arch_hash)",
            "One order per user/model/layout",
        ),
    ]

    @api.model
    def get_order(self, view_id, model, arch_hash=None):
        domain = [
            ("user_id", "=", self.env.user.id),
            ("model", "=", model),
        ]
        if arch_hash:
            domain.append(("arch_hash", "=", arch_hash))
        rec = self.search(domain, limit=1)
        if not rec:
            return []
        try:
            return json.loads(rec.order_json or "[]")
        except Exception:
            return []

    @api.model
    def set_order(self, view_id, model, order_list, arch_hash=None):
        if not isinstance(order_list, list):
            return False
        clean = [x for x in order_list if isinstance(x, str) and x]

        domain = [
            ("user_id", "=", self.env.user.id),
            ("model", "=", model),
        ]
        if arch_hash:
            domain.append(("arch_hash", "=", arch_hash))

        rec = self.search(domain, limit=1)
        vals = {
            "user_id": self.env.user.id,
            "view_id": view_id or False,
            "model": model,
            "order_json": json.dumps(clean),
            "arch_hash": arch_hash or False,
        }
        if rec:
            rec.write(vals)
        else:
            self.create(vals)
        return True
