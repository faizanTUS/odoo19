# See LICENSE file for full copyright and licensing details.
from odoo import api, models


class Currency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        """
        update conversion rate based on the context present
        @param from_currency: conversion from currency
        @param to_currency: conversion to currency
        @param company: conversion company
        @param date: conversion date
        @return: rate of conversion (float)
        """
        result = super(Currency, self)._get_conversion_rate(
            from_currency, to_currency, company, date
        )
        if not company.allow_custom_currency_rate:
            return result
        if self._context.get("new_payment_currency_rate"):
            return self._context.get("new_payment_currency_rate") or result
        if self._context.get("new_currency_rate"):
            return self._context.get("new_currency_rate") or result
        if self._context.get("params"):
            params = self._context.get("params")
            if params.get("model") and params.get("id"):
                record_id = self.env[params.get("model")].search(
                    [("id", "=", params.get("id"))]
                )
                if hasattr(record_id, "new_currency_rate"):
                    result = record_id.new_currency_rate or result
        return result
