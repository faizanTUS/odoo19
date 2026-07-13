# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    currency_rate = fields.Float(
        string="Currency Rate", store=True, digits=(16, 4), readonly=1
    )
    manual_currency_rate = fields.Float(string="Manual Currency Rate", digits=(16, 4))
    currency_amount_difference = fields.Float(
        string="Amount Difference", compute="_compute_currency_amount_difference"
    )
    allow_custom_currency_rate = fields.Boolean(
        related="company_id.allow_custom_currency_rate"
    )
    is_company_currency = fields.Boolean(compute="_compute_is_company_currency")
    is_not_company_invoice_currency = fields.Boolean(
        compute="_compute_is_not_company_invoice_currency"
    )
    invoice_ids = fields.Many2many("account.move")
    currency_rate_for_currency_to_invoice_currency = fields.Float(
        string="Currency Rate for Selected Currency to Invoice Currency",
        digits=(16, 4),
        default=1,
    )
    currency_rate_for_invoice_currency_to_company_currency = fields.Float(
        string="Currency Rate for Invoice Currency to Company Currency",
        digits=(16, 4),
        default=1,
    )
    custom_amount = fields.Monetary(
        currency_field="currency_id",
        store=True,
        readonly=False,
        compute="_compute_custom_amount",
    )
    is_multiple_record = fields.Boolean()
    currency_rate_for_multiple_records = fields.Float(
        string="Currency Rate", digits=(16, 4)
    )

    @api.depends(
        "is_not_company_invoice_currency",
        "currency_rate_for_currency_to_invoice_currency",
    )
    def _compute_custom_amount(self):
        """
        compute method to update the custom amount if the payment currency is neither equals to the payment record
        currency nor company currency.
        @return: no return
        """
        self.custom_amount = 0
        for rec in self.filtered(lambda x: x.allow_custom_currency_rate):
            if rec.is_not_company_invoice_currency:
                rec.custom_amount = rec.amount / (
                    rec.currency_rate_for_currency_to_invoice_currency
                    and rec.currency_rate_for_currency_to_invoice_currency
                    or 1
                )

    @api.depends(
        "company_currency_id", "currency_id", "invoice_ids", "invoice_ids.currency_id"
    )
    def _compute_is_not_company_invoice_currency(self):
        """
        compute method to find of if the payment currency is neither equals to the payment record currency nor
        company currency
        @return: no return
        """
        self.is_not_company_invoice_currency = False
        for rec in self.filtered(lambda x: x.allow_custom_currency_rate):
            if (
                rec.currency_id != rec.company_currency_id
                and rec.currency_id != rec.invoice_ids.currency_id
            ):
                rec.is_not_company_invoice_currency = True

    @api.depends("company_currency_id", "currency_id")
    def _compute_is_company_currency(self):
        """
        compute method to find out the payment currency is same as the company currency
        @return: no return
        """
        self.is_company_currency = False
        for rec in self.filtered(
            lambda x: x.allow_custom_currency_rate
            and x.company_currency_id == x.currency_id
        ):
            rec.is_company_currency = True

    @api.onchange("currency_id")
    def _onchange_currency_rate(self):
        """
        update currency rate and manual currency rate based on changing of currency
        @return: no return
        """
        for rec in self.filtered(lambda x: x.allow_custom_currency_rate):
            rec.currency_rate = rec.currency_id.inverse_rate or 0
            rec.manual_currency_rate = rec.currency_id.inverse_rate or 0
            if self._context.get("active_model") and self._context.get("active_ids"):
                record_id = self.env[self._context.get("active_model")].browse(
                    self._context.get("active_ids")
                )
                if len(record_id.move_id) == 1:
                    if (
                        hasattr(record_id.move_id, "company_id")
                        and hasattr(record_id.move_id, "currency_id")
                        and hasattr(record_id.move_id, "new_currency_rate")
                    ):
                        if record_id.company_id.currency_id != rec.currency_id:
                            rec.currency_rate = record_id.move_id.new_currency_rate
                            rec.manual_currency_rate = record_id.move_id.new_currency_rate

    @api.model
    def default_get(self, fields):
        """
        Use active_ids from the context to fetch the currency rate and payment record.
        @param fields: argument of the function
        @return: list of the values
        """
        vals = super(AccountPaymentRegister, self).default_get(fields)
        if self._context.get("active_model") and self._context.get("active_ids"):
            record_id = self.env[self._context.get("active_model")].browse(
                self._context.get("active_ids")
            )
            if len(record_id) == 1:
                vals["manual_currency_rate"] = record_id[:1].move_id.new_currency_rate
                vals["currency_rate"] = record_id[:1].move_id.new_currency_rate
                vals["currency_rate_for_invoice_currency_to_company_currency"] = record_id[:1].move_id.new_currency_rate
            vals["is_multiple_record"] = len(record_id.move_id) > 1 and True or False
            vals["currency_rate_for_multiple_records"] = record_id[:1].move_id.new_currency_rate
            vals["invoice_ids"] = [(6, 0, record_id.move_id.ids)]
        return vals

    @api.depends("manual_currency_rate", "amount", "currency_id")
    def _compute_currency_amount_difference(self):
        """
        compute method to find the value of currency_amount_difference between the payment amount with the
        payment record amount
        @return: no return
        """
        self.currency_amount_difference = 0
        for rec in self.filtered(lambda x: x.allow_custom_currency_rate):
            if (
                rec.currency_rate
                and rec.amount
                and rec.manual_currency_rate
                and not rec.is_not_company_invoice_currency
            ):
                total_rate = rec.currency_rate * rec.amount
                currency_total_rate = rec.manual_currency_rate * rec.amount
                currency_total_rate = currency_total_rate - total_rate
                rec.currency_amount_difference = currency_total_rate
            if (
                self._context.get("active_model")
                and self._context.get("active_ids")
                and not rec.is_not_company_invoice_currency
            ):
                record_id = self.env[self._context.get("active_model")].browse(
                    self._context.get("active_ids")
                )
                if len(record_id) == 1:
                    if (
                        hasattr(record_id, "company_id")
                        and hasattr(record_id, "currency_id")
                        and hasattr(record_id, "new_currency_rate")
                        and hasattr(record_id, "converted_currency_amount")
                    ):
                        currency_total_rate = rec.manual_currency_rate * rec.amount
                        currency_total_rate = (
                            currency_total_rate - record_id.converted_currency_amount
                        )
                        rec.currency_amount_difference = currency_total_rate
            if rec.is_not_company_invoice_currency:
                invoice_currency_rate = rec.amount
                currency_total_rate = (
                    invoice_currency_rate
                    * rec.currency_rate_for_invoice_currency_to_company_currency
                )
                rec.currency_amount_difference = currency_total_rate - rec.source_amount

    def action_create_payments(self):
        """
        update context related to company currency, payment record currency and payment currency and currency rate
        @return: supper call return
        """
        if (
            self.invoice_ids.company_id.currency_id == self.currency_id
            and self.allow_custom_currency_rate
        ):
            return super(
                AccountPaymentRegister, self.with_context(no_exchange_difference=True)
            ).action_create_payments()
        if self.is_not_company_invoice_currency and self.allow_custom_currency_rate:
            self.currency_id = self.source_currency_id.id
            currency_rate = self.currency_rate_for_invoice_currency_to_company_currency
        elif self.is_multiple_record and self.allow_custom_currency_rate:
            currency_rate = self.currency_rate_for_multiple_records
        else:
            currency_rate = self.manual_currency_rate
        if self.allow_custom_currency_rate:
            self = self.with_context(new_payment_currency_rate=currency_rate)
        return super(AccountPaymentRegister, self).action_create_payments()

    @api.depends(
        "can_edit_wizard",
        "source_amount",
        "source_amount_currency",
        "source_currency_id",
        "company_id",
        "currency_id",
        "payment_date",
        "currency_rate_for_invoice_currency_to_company_currency",
    )
    def _compute_amount(self):
        """
        update amount related to the currency of company, payment record and payment
        @return: no return
        """
        if not self.is_not_company_invoice_currency:
            if (
                self._context.get("active_model")
                and self._context.get("active_ids")
                and self.allow_custom_currency_rate
            ):
                record_id = self.env[self._context.get("active_model")].browse(
                    self._context.get("active_ids")
                )
                if len(record_id) == 1:
                    self_upd = self.with_context(
                        new_payment_currency_rate=record_id.new_currency_rate
                    )
                    return super(AccountPaymentRegister, self_upd)._compute_amount()
            return super(AccountPaymentRegister, self)._compute_amount()
        if self.allow_custom_currency_rate:
            self.amount = self.source_amount / (
                self.currency_rate and self.currency_rate or 1
            )

    @api.depends("journal_id")
    def _compute_currency_id(self):
        super(AccountPaymentRegister, self)._compute_currency_id()
        for rec in self.filtered(
            lambda x: x.allow_custom_currency_rate and x.is_multiple_record
        ):
            rec.currency_id = rec.invoice_ids.currency_id.id
