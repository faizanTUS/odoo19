# See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    custom_currency_rate = fields.Float(
        "Custom Currency Rate", default=0.0, digits=(16, 4)
    )
    allow_custom_currency_rate = fields.Boolean(
        related="company_id.allow_custom_currency_rate"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        updated new currency rate value while the currency rate is present in the context and raise validation
        if currency rate is not set in the order if the currency id of the record is not equals to the company currency.
        @param vals_list: creating record values
        @return: supper call result
        """
        if self._context.get("new_payment_currency_rate") and all(
            self.mapped("allow_custom_currency_rate")
        ):
            for vals in vals_list:
                vals["custom_currency_rate"] = self._context.get(
                    "new_payment_currency_rate"
                )
        custom_currency_rate = (
            vals_list[0].get("custom_currency_rate")
            if vals_list
            else (self._context.get("new_payment_currency_rate") or 0)
        )
        if all(self.mapped("allow_custom_currency_rate")):
            self = self.with_context(new_payment_currency_rate=custom_currency_rate)
        res = super(AccountPayment, self).create(vals_list)
        for payment in res:
            if (
                payment
                and payment.allow_custom_currency_rate
                and payment.currency_id != payment.company_currency_id
                and payment.custom_currency_rate == 0
            ):
                raise ValidationError(_("Update new currency rate."))
            payment._onchange_custom_currency_rate()
        return res

    @api.onchange("custom_currency_rate", "amount", "currency_id")
    def _onchange_custom_currency_rate(self):
        """
        update new currency rate base on changing the custom_currency_rate field
        @return: no return
        """
        for rec in self.filtered(lambda payment: payment.allow_custom_currency_rate):
            custom_currency_rate = rec.custom_currency_rate
            rec.move_id._origin.write({"new_currency_rate": custom_currency_rate})

    @api.onchange("partner_id")
    def _onchange_custom_partner_id(self):
        """
        When change the partner, updated custom currency rate to 0.
        @return: no return
        """
        for rec in self.filtered(lambda payment: payment.allow_custom_currency_rate):
            rec.custom_currency_rate = 0

    def write(self, vals):
        """
        Raise validation if currency rate is not set in the record if the currency id of the order is not equals
        to the company currency.
        @param vals: values to update
        @return: super call result
        """
        result = super(AccountPayment, self).write(vals)
        if (
            result
            and not self._context.get("new_currency_rate")
            and not self._context.get("new_currency_rate") == 0
        ):
            for rec in self:
                if (
                    rec.allow_custom_currency_rate
                    and rec.company_id.currency_id
                    and rec.currency_id != rec.company_id.currency_id
                    and rec.custom_currency_rate == 0
                ):
                    raise ValidationError(_("Update new currency rate."))
        return result

    def action_post(self):
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(
                    new_payment_currency_rate=rec.custom_currency_rate
                )
            super(AccountPayment, rec).action_post()
        return True
