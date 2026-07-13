# See LICENSE file for full copyright and licensing details.
from contextlib import contextmanager

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.account.models.account_move_line import AccountMoveLine as AML


class AccountMove(models.Model):
    _inherit = "account.move"

    new_currency_rate = fields.Float(string="New Currency Rate", digits=(16, 4))

    allow_custom_currency_rate = fields.Boolean(
        related="company_id.allow_custom_currency_rate"
    )

    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        store=True,
    )

    converted_currency_amount = fields.Monetary(
        string="Converted Currency Amount",
        store=True,
        compute="_compute_converted_currency_amount",
        currency_field='company_currency_id',
        tracking=True,
    )

    currency_exchange_amount = fields.Monetary(
        string="Currency Exchange Amount",
        readonly=True,
        tracking=True,
        compute="_compute_exchange_amount",
        currency_field="company_currency_id",
    )

    is_new_currency_rate_visible = fields.Boolean(
        compute="_compute_is_new_currency_rate_visible"
    )

    @api.depends("currency_id", "company_currency_id")
    def _compute_is_new_currency_rate_visible(self):
        """
        Compute for the boolean to get the new currency rate field visible
        @return: no return
        """
        self.is_new_currency_rate_visible = False
        for rec in self.filtered(lambda x: x.company_currency_id.id != x.currency_id.id):
            rec.is_new_currency_rate_visible = True

    def _compute_exchange_amount(self):
        """
        Add total currency exchange rate difference on record
        @return: no return
        """
        self.currency_exchange_amount = 0.0
        for account_move in self.filtered(lambda x: x.allow_custom_currency_rate):
            if (
                account_move.currency_id == account_move.company_currency_id
                or not account_move.new_currency_rate
            ):
                continue
            payment_obj = self.env["account.payment"]
            invoice_payments_widget = account_move.invoice_payments_widget
            if invoice_payments_widget and invoice_payments_widget.get("content"):
                content = invoice_payments_widget.get("content")
                payment = 0
                currency_amount = 0
                for data in [content[-1]]:
                    amount = data.get("amount")
                    payment_id = data.get("account_payment_id")
                    if not payment_id or not amount:
                        continue
                    payment_id = payment_obj.search([("id", "=", payment_id)])
                    payment += amount * payment_id.custom_currency_rate
                    currency_amount += amount

                if account_move.move_type == "in_invoice":
                    account_move.currency_exchange_amount = (
                        currency_amount * account_move.new_currency_rate
                    ) - payment
                else:
                    account_move.currency_exchange_amount = payment - (
                        currency_amount * account_move.new_currency_rate
                    )

    @api.depends(
        "currency_id", "new_currency_rate", "company_id.currency_id", "amount_total"
    )
    def _compute_converted_currency_amount(self):
        """
        compute method to update converted currency amount based on currency set in the record
        @return: no return
        """
        self.converted_currency_amount = 0.0
        for so in self.filtered(lambda x: x.allow_custom_currency_rate):
            if so.currency_id != so.company_id.currency_id:
                so.converted_currency_amount = so.amount_total * so.new_currency_rate

    def write(self, vals):
        """
        raise validation if currency rate is not set in the record if the currency id of the order is not equals
        to the company currency.
        @param vals: values to update
        @return: True
        """
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.new_currency_rate)
            super(AccountMove, rec).write(vals)
            if (rec.allow_custom_currency_rate
                and rec.company_id.currency_id
                and rec.currency_id != rec.company_id.currency_id
                and rec.new_currency_rate == 0
            ):
                raise ValidationError(_("Update new currency rate."))
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """
        updated new currency rate value while the currency rate is present in the context
        @param vals_list: creating record values
        @return: super call result
        """
        if self._context.get("new_currency_rate") or self._context.get(
            "new_payment_currency_rate"
        ):
            if type(vals_list) == list:
                for val in vals_list:
                    val["new_currency_rate"] = (
                        self._context.get("new_currency_rate")
                        or self._context.get("new_payment_currency_rate")
                        or 0
                    )
            else:
                vals_list["new_currency_rate"] = (
                    self._context.get("new_currency_rate")
                    or self._context.get("new_payment_currency_rate")
                    or 0
                )
        result = super(AccountMove, self).create(vals_list)
        return result

    @api.depends(
        # "line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency",
        # "line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.balance",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        # "line_ids.payment_id.state",
        "line_ids.full_reconcile_id",
        "state",
    )
    def _compute_amount(self):
        """
        Passing currency rate context while Confirm the Purchase order
        @return: no return
        """
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.new_currency_rate)
            super(AccountMove, rec)._compute_amount()

    def action_register_payment(self):
        """Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        """
        if not len(self.currency_id) == 1 and all(
            self.mapped("allow_custom_currency_rate")
        ):
            raise ValidationError("Please Select Records with same Currency")
        return super(AccountMove, self).action_register_payment()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company Currency',
        store=True,
    )

    converted_subtotal = fields.Monetary(
        string="Converted Subtotal",
        compute='_compute_converted_subtotal',
        currency_field='company_currency_id',
    )

    def _compute_converted_subtotal(self):
        """
        compute method to update converted subtotal based on new currency rate
        set in the record
        @return: no return
        """
        self.converted_subtotal = 0
        for line in self.filtered(lambda x: x.currency_id != x.company_id.currency_id):
            line.update({
                'converted_subtotal': line.price_subtotal * line.move_id.new_currency_rate,
            })

    @api.depends('product_id', 'product_uom_id')
    def _compute_price_unit(self):
        """
        Passing currency rate context while computing price unit for a particular line
        @return: no return
        """
        for rec in self:
            if rec.move_id.allow_custom_currency_rate and rec.move_id.new_currency_rate:
                rec = rec.with_context(
                    new_currency_rate=1 / rec.move_id.new_currency_rate)
            super(AccountMoveLine, rec)._compute_price_unit()

    @api.depends("quantity", "discount", "price_unit", "tax_ids", "currency_id")
    def _compute_totals(self):
        """
        Passing currency rate context while Confirm the Purchase order
        @return: no return
        """
        for rec in self:
            if rec.move_id.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.move_id.new_currency_rate)
            super(AccountMoveLine, rec)._compute_totals()

    @api.depends(
        "debit",
        "credit",
        "amount_currency",
        "account_id",
        "currency_id",
        "company_id",
        "matched_debit_ids",
        "matched_credit_ids",
    )
    def _compute_amount_residual(self):
        """
        Passing currency rate context while Confirm the Purchase order
        @return: no return
        """
        for rec in self:
            if rec.move_id.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.move_id.new_currency_rate)
            super(AccountMoveLine, rec)._compute_amount_residual()

    @api.depends("currency_id", "company_id", "move_id.date")
    def _compute_currency_rate(self):
        """
        Passing currency rate context while Confirm the Purchase order
        @return: no return
        """
        for rec in self:
            if rec.move_id.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.move_id.new_currency_rate)
            super(AccountMoveLine, rec)._compute_currency_rate()

    @api.onchange("amount_currency", "currency_id")
    def _inverse_amount_currency(self):
        """
        update balance according to the new currency rate
        @return: no return
        """
        super(AccountMoveLine, self)._inverse_amount_currency()
        for line in self.filtered(lambda x: x.move_id.allow_custom_currency_rate):
            if (
                line.currency_id != line.company_id.currency_id
                and not line.move_id.is_invoice(True)
                and not line.env.is_protected(line._fields["balance"], line)
            ):
                line.balance = line.company_id.currency_id.round(
                    line.amount_currency * line.currency_rate
                )


@contextmanager
def _sync_invoice(self, container):
    """
    monkey patch base _sync_invoice method to update the journal entries according to the new currency rate
    @param self: current object
    @return: no return
    """
    if container["records"].env.context.get("skip_invoice_line_sync"):
        yield
        return  # avoid infinite recursion

    def existing():
        return {
            line: {
                "amount_currency": line.currency_id.round(line.amount_currency),
                "balance": line.company_id.currency_id.round(line.balance),
                "currency_rate": line.currency_rate,
                "price_subtotal": line.currency_id.round(line.price_subtotal),
                "move_type": line.move_id.move_type,
            }
            for line in container["records"]
            .with_context(
                skip_invoice_line_sync=True,
            )
            .filtered(lambda l: l.move_id.is_invoice(True))
        }

    def changed(fname):
        return line not in before or before[line][fname] != after[line][fname]

    before = existing()
    yield
    after = existing()
    for line in after:
        if line.display_type == "product" and (
            not changed("amount_currency") or line not in before
        ):
            amount_currency = line.move_id.direction_sign * line.currency_id.round(
                line.price_subtotal
            )
            if line.amount_currency != amount_currency or line not in before:
                line.amount_currency = amount_currency
            if line.currency_id == line.company_id.currency_id:
                line.balance = amount_currency

    after = existing()
    for line in after:
        if (
            changed("amount_currency")
            or changed("currency_rate")
            or changed("move_type")
        ) and (not changed("balance") or (line not in before and not line.balance)):
            balance = line.company_id.currency_id.round(
                line.amount_currency / line.currency_rate
            )
            if line.move_id.allow_custom_currency_rate:
                balance = line.company_id.currency_id.round(
                    line.amount_currency * line.currency_rate
                )
            line.balance = balance
    # Since this method is called during the sync, inside of `create`/`write`, these fields
    # already have been computed and marked as so. But this method should re-trigger it since
    # it changes the dependencies.
    self.env.add_to_compute(self._fields["debit"], container["records"])
    self.env.add_to_compute(self._fields["credit"], container["records"])


AML._sync_invoice = _sync_invoice
