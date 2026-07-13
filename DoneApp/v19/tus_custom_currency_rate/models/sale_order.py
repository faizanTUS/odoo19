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

    @api.depends("currency_id", "company_currency_id")
    def _compute_is_new_currency_rate_visible(self):
        """
        Compute for the boolean to get the new currency rate field visible
        @return: no return
        """
        self.is_new_currency_rate_visible = False
        for rec in self.filtered(lambda x: x.company_currency_id.id != x.currency_id.id):
            rec.is_new_currency_rate_visible = True

    @api.depends(
        "currency_id", "new_currency_rate", "company_id.currency_id", "amount_total"
    )
    def _compute_converted_currency_amount(self):
        """
        compute method to update converted currency amount based on currency set in the record
        @return: no return
        """
        self.converted_currency_amount = 0
        for so in self.filtered(
            lambda x: x.allow_custom_currency_rate
            and x.currency_id != x.company_id.currency_id
        ):
            so.converted_currency_amount = so.amount_total * so.new_currency_rate

    def action_confirm(self):
        """
        Passing currency rate context while confirm the Sale order
        @return: super call
        """
        if self.allow_custom_currency_rate:
            self = self.with_context(new_currency_rate=self.new_currency_rate)
        return super(SaleOrder, self).action_confirm()

    def write(self, vals):
        """
        raise validation if currency rate is not set in the record if the currency id of the order is not equals
        to the company currency.
        @param vals: values to update
        @return: super call result
        """
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.new_currency_rate)
            super(SaleOrder, rec).write(vals)
            if "state" in vals and vals["state"] == "cancel":
                continue
            elif (
                rec.company_id.allow_custom_currency_rate
                and rec.currency_id
                and rec.company_id.currency_id
                and rec.pricelist_id.currency_id != rec.company_id.currency_id
                and rec.new_currency_rate == 0
            ):
                raise ValidationError(_("Update new currency rate."))
        return True

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Passing currency rate context while creating a invoice from sale order
        @param grouped: bool if True, invoices are grouped by SO id. If False, invoices are grouped by keys
        returned by :meth:`_get_invoice_grouping_keys`
        @param final: bool if True, refunds will be generated if necessary
        @param date: unused parameter
        @return: super call
        """
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.new_currency_rate,is_custom_currency=True)
            super(SaleOrder, rec)._create_invoices(
                grouped=grouped, final=final, date=date
            )
        return self.invoice_ids

    @api.model_create_multi
    def create(self, vals_list):
        """
        raise validation if currency rate is not set in the record if the currency id of the order is not equals
        to the company currency.
        @param vals_list: records value to create
        @return: super call result
        """
        if all(self.mapped("allow_custom_currency_rate")):
            self = self.with_context(new_currency_rate=self.new_currency_rate)
        result = super(SaleOrder, self).create(vals_list)
        if (
            result
            and result.allow_custom_currency_rate
            and result.pricelist_id.currency_id
            and result.company_id.currency_id
            and result.pricelist_id.currency_id != result.company_id.currency_id
            and result.new_currency_rate == 0
        ):
            raise ValidationError(_("Update new currency rate."))
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
        """
        compute method to update converted subtotal based on new currency rate
        set in the record
        @return: no return
        """
        self.converted_subtotal = 0
        for line in self.filtered(lambda x: x.currency_id != x.company_id.currency_id):
            line.update({
                'converted_subtotal': line.price_subtotal * line.order_id.new_currency_rate,
            })

    @api.depends('product_id', 'product_uom_qty')
    def _compute_price_unit(self):
        """
        Passing currency rate context while computing price unit for a particular line
        @return: no return
        """
        for rec in self:
            if rec.order_id.allow_custom_currency_rate and rec.order_id.new_currency_rate:
                rec = rec.with_context(
                    new_currency_rate=1 / rec.order_id.new_currency_rate)
            super(SaleOrderLine, rec)._compute_price_unit()