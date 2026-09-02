# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)

TARGETS = [
    ("cancel", "Cancel"),
    ("reverse", "Reverse"),
    ("reset", "Reset to Draft"),
]

class TusCancelResetWizard(models.TransientModel):
    _name = "tus.cancel.reset.wizard"
    _description = "Cancel / Reverse / Reset Wizard"

    action = fields.Selection(TARGETS, required=True, default="cancel")
    include_dependencies = fields.Boolean(default=lambda s: s._get_param_bool("tus_reversal.auto_handle_dependencies"))
    require_reason = fields.Boolean(default=lambda s: s._get_param_bool("tus_reversal.require_reason"))
    reason = fields.Text()
    reverse_date = fields.Date(default=fields.Date.context_today)
    reverse_journal_id = fields.Many2one("account.journal", domain=[("type","=","purchase")])
    create_refund_bill = fields.Boolean(string="Create Refund Bill(s)", default=True)
    create_return_picking = fields.Boolean(string="Create Return Picking(s)", default=True)

    # Computed context opener
    def action_open_wizard(self):
        return {
            "name": _("Cancel / Reverse / Reset"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "target": "new",
        }

    # Helpers
    def _get_param_bool(self, key):
        return self.env["ir.config_parameter"].sudo().get_param(key, "False") in ("True", "1", True)

    # MAIN ENTRY
    def action_execute(self):
        self.ensure_one()
        if self.require_reason and not self.reason:
            raise UserError(_("Please provide a reason."))

        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])
        if not active_model or not active_ids:
            raise UserError(_("No records selected."))

        records = self.env[active_model].browse(active_ids).exists()
        if not records:
            return

        # permissions
        if not self.env.user.has_group("tus_po_reversal_advanced.group_reversal_user"):
            raise UserError(_("You don't have rights to perform this action."))

        # action routing
        if self.action == "cancel":
            self._do_cancel(records)
        elif self.action == "reverse":
            self._do_reverse(records)
        else:
            self._do_reset(records)

    # IMPLEMENTATIONS
    def _do_cancel(self, records):
        for rec in records:
            if rec._name == "purchase.order":
                self._cancel_po(rec)
            elif rec._name == "stock.picking":
                self._cancel_picking(rec)
            elif rec._name == "account.move":
                self._cancel_move(rec)
        return True

    def _do_reverse(self, records):
        for rec in records:
            if rec._name == "stock.picking" and self.create_return_picking:
                self._reverse_picking(rec)
            elif rec._name == "account.move" and self.create_refund_bill:
                self._reverse_move(rec)
        return True

    def _do_reset(self, records):
        allow = self._get_param_bool("tus_reversal.allow_after_validation")
        for rec in records:
            if rec._name == "purchase.order":
                if rec.state not in ("draft","sent","to approve","purchase") and not allow:
                    raise UserError(_("Reset not allowed after validation by policy."))
                rec.button_cancel() if rec.state not in ("cancel","done") else None
                rec.button_draft()
                rec._tus_log("reset", self.reason)
            elif rec._name == "stock.picking":
                if rec.state == "done" and not allow:
                    raise UserError(_("Reset not allowed after done by policy."))
                if rec.state not in ("cancel","draft"):
                    rec.action_cancel()
                rec.write({"state": "draft"})
                rec._tus_log("reset", self.reason)
            elif rec._name == "account.move":
                if rec.state == "posted" and not allow:
                    raise UserError(_("Reset not allowed for posted entries by policy."))
                rec.button_draft()
                rec._tus_log("reset", self.reason)

    # PO
    def _cancel_po(self, po):
        # optional dependency handling
        if self.include_dependencies:
            # Get all related bills
            all_bills = po.tus_get_related_bills()

            # 1. Handle bills that are not cancelled
            for bill in all_bills.filtered(lambda m: m.state != "cancel"):
                self._cancel_move(bill)

            # 2. After handling bills, check if any are still blocking
            # Posted bills that have been refunded should not block cancellation
            blocking_bills = all_bills.filtered(lambda m: m.state == "posted" and not m.reversed_entry_id)

            if blocking_bills and not self.create_refund_bill:
                raise UserError(_(
                    "Posted bills exist: %s. Enable 'Create Refund Bill' to handle them."
                ) % ', '.join(blocking_bills.mapped('name')))

            # 3. Handle pickings
            for picking in po.tus_get_related_pickings().filtered(lambda p: p.state not in ("cancel")):
                self._cancel_picking(picking)

        # 4. Cancel the PO - use with_context to skip invoice validation
        if po.state not in ("cancel", "done"):
            try:
                po.with_context(disable_cancel_warning=True).button_cancel()
            except UserError as e:
                # If standard cancel fails, write state directly
                # _logger.warning(f"Standard cancel failed for {po.name}, using direct state write: {e}")
                po.order_line.write({'state': 'cancel'})
                po.write({'state': 'cancel'})

        po._tus_log("cancel", self.reason)

    # Picking
    def _cancel_picking(self, picking):
        if picking.state == "done":
            # prefer reverse rather than direct cancel
            if self.create_return_picking:
                self._reverse_picking(picking)
        elif picking.state not in ("cancel",):
            picking.action_cancel()
            picking._tus_log("cancel", self.reason)

    def _reverse_picking(self, picking):

        if picking.state != "done":
            return

        ReturnWizard = self.env["stock.return.picking"].with_context(
            active_model="stock.picking",
            active_id=picking.id,
            active_ids=[picking.id],
        )

        vals = ReturnWizard.default_get(list(ReturnWizard._fields.keys()))

        if "picking_id" in ReturnWizard._fields:
            vals["picking_id"] = picking.id

        # Create wizard with lines
        wiz = ReturnWizard.create(vals)

        # Use Odoo API to auto-set quantities properly
        res = None
        if hasattr(wiz, "action_create_returns_all"):
            res = wiz.action_create_returns_all()
        else:
            # fallback safe method
            for line in wiz.product_return_moves:
                if not line.quantity:
                    m = line.move_id
                    if m:
                        qty = m.quantity - sum(m.move_dest_ids.filtered(
                            lambda mv: mv.origin_returned_move_id == m
                        ).mapped("quantity"))
                        qty = float_round(qty, precision_rounding=m.product_uom_id.rounding)
                        if qty > 0:
                            line.quantity = qty

            # find correct creator method
            for m in ("action_create_returns", "create_returns", "_create_returns", "_create_return"):
                if hasattr(wiz, m):
                    res = getattr(wiz, m)()
                    break

        # Extract created picking id
        created_id = None

        if isinstance(res, dict) and "res_id" in res:
            created_id = res["res_id"]
        elif isinstance(res, dict) and "domain" in res:
            dom = res.get("domain") or []
            ids = next((d[2] for d in dom if isinstance(d, (list, tuple)) and d[:2] == ["id", "in"]), [])
            created_id = ids and ids[0]
        elif isinstance(res, (tuple, list)) and res:
            created_id = res[0]

        # LOG CREATION
        picking._tus_log("reverse", self.reason, note=_("Created return picking: %s") % (created_id or _("unknown")))

        return res

    # Vendor Bills
    def _cancel_move(self, move):
        if move.state == "posted":
            if self.create_refund_bill:
                # This will create refund and keep original posted
                self._reverse_move(move)
            else:
                raise UserError(
                    _("Posted bill cannot be cancelled directly. Enable 'Create Refund Bill' to create a refund entry."))
        elif move.state != "cancel":
            if hasattr(move, "button_cancel"):
                move.button_cancel()
            else:
                move.write({"state": "cancel"})
            move._tus_log("cancel", self.reason)

    def _reverse_move(self, move):

        if move.move_type not in ("in_invoice", "in_refund"):
            return

        if move.state != "posted":
            return

        # Create reversal wizard
        reversal = self.env["account.move.reversal"].create({
            "move_ids": [(6, 0, [move.id])],
            "date": self.reverse_date,
            "journal_id": self.reverse_journal_id.id or move.journal_id.id,
            "reason": self.reason or _("Reversal"),
        })

        # Create refund move
        result = reversal.reverse_moves()

        refund_id = None

        if isinstance(result, dict) and result.get("res_id"):
            refund_id = result["res_id"]
            refund_move = self.env["account.move"].browse(refund_id).exists()

            if refund_move:

                # AUTO-POST REFUND
                try:
                    if refund_move.state == "draft":
                        refund_move.action_post()

                    move._tus_log("reverse", self.reason,
                                  note=_("Refund created and posted: %s") % refund_move.name)
                except Exception as e:
                    # _logger.warning("Refund created but not posted: %s", e)
                    move._tus_log("reverse", self.reason,
                                  note=_("Refund created but not posted."))

        return result
