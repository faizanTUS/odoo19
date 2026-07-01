# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Confirmed payslip states for report domains (Odoo 19 uses validated/paid; legacy DBs may use done)."""


def payslip_confirmed_states(env):
    """Return selection codes for payslips that should appear in registers (non-draft, non-cancel)."""
    field = env["hr.payslip"]._fields.get("state")
    if not field:
        return ["validated", "paid"]
    sel = field.selection
    if callable(sel):
        try:
            sel = sel(env["hr.payslip"])
        except TypeError:
            sel = sel()
    if not sel:
        return ["validated", "paid"]
    codes = {row[0] for row in sel}
    preferred = [s for s in ("validated", "paid", "done") if s in codes]
    if preferred:
        return preferred
    return [c for c in sorted(codes) if c not in ("draft", "cancel")]
