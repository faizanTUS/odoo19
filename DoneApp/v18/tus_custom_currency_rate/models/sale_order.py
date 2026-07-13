# See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    is_new_currency_rate_visible = fields.Boolean(
        compute="_compute_is_new_currency_rate_visible"
    )

    @api.depends("pricelist_id.currency_id", "company_currency_id")
    def _compute_is_new_currency_rate_visible(self):
        self.is_new_currency_rate_visible = False
        for rec in self.filtered(
            lambda x: x.company_currency_id.id != x.pricelist_id.currency_id.id
        ):
            rec.is_new_currency_rate_visible = True

    @api.depends("pricelist_id.currency_id", "new_currency_rate", "amount_total")
    def _compute_converted_currency_amount(self):
        for so in self:
            if (
                so.allow_custom_currency_rate
                and so.pricelist_id.currency_id != so.company_id.currency_id
                and so.new_currency_rate > 0
            ):
                so.converted_currency_amount = so.amount_total * so.new_currency_rate
            else:
                so.converted_currency_amount = 0.0

    @api.constrains('new_currency_rate')
    def _check_new_currency_rate(self):
        for rec in self:
            if (
                rec.allow_custom_currency_rate
                and rec.pricelist_id.currency_id != rec.company_id.currency_id
                and rec.new_currency_rate <= 0
            ):
                raise ValidationError(_("Update new currency rate."))

    def action_confirm(self):
        if self.allow_custom_currency_rate:
            self = self.with_context(new_currency_rate=self.new_currency_rate)
        return super().action_confirm()

    def write(self, vals):
        res = super().write(vals)
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        for rec in self:
            if rec.allow_custom_currency_rate and rec.new_currency_rate:
                rec = rec.with_context(
                    new_currency_rate=rec.new_currency_rate,
                    is_custom_currency=True
                )
            super(SaleOrder, rec)._create_invoices(
                grouped=grouped, final=final, date=date
            )
        return self.invoice_ids

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
        for line in self:
            rate = line.order_id.new_currency_rate or 0.0
            if line.currency_id != line.company_id.currency_id:
                line.converted_subtotal = line.price_subtotal * rate
            else:
                line.converted_subtotal = 0.0

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for rec in self:
            if rec.order_id.allow_custom_currency_rate and rec.order_id.new_currency_rate:
                rec = rec.with_context(
                    new_currency_rate=1 / rec.order_id.new_currency_rate)
            super(SaleOrderLine, rec)._compute_price_unit()