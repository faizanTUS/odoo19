# See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    new_currency_rate = fields.Float(string="New Currency Rate", digits=(16, 4))

    allow_custom_currency_rate = fields.Boolean(related="company_id.allow_custom_currency_rate")

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

    is_company_currency = fields.Boolean(
        string="Is Company Currency", compute="_compute_is_company_currency", store=True
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
        self.converted_currency_amount = 0.0
        for po in self.filtered(
            lambda x: x.allow_custom_currency_rate
            and x.currency_id != x.company_id.currency_id
        ):
            po.converted_currency_amount = po.amount_total * po.new_currency_rate

    @api.depends("currency_id")
    def _compute_is_company_currency(self):
        """
        compute method to update is_company_currency to True if the selected currency is equal to the company currency
        @return: no return
        """
        self.is_company_currency = False
        for rec in self.filtered(
            lambda x: x.allow_custom_currency_rate
            and x.currency_id.id != x.company_id.currency_id.id
        ):
            rec.is_company_currency = True

    def button_confirm(self):
        """
        Passing currency rate context while Confirm the Purchase order
        @return: super call
        """
        if self.allow_custom_currency_rate:
            self = self.with_context(new_currency_rate=self.new_currency_rate)
        return super(PurchaseOrder, self).button_confirm()

    def write(self, vals):
        """
        Passing currency rate context while saving the Purchase order &
        Checking if Company's currency and record's currency is same or not if not then
        user must set new_currency_rate value greater than zero.
        @param vals: update record values
        @return: super call result
        """
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.new_currency_rate)
            super(PurchaseOrder, rec).write(vals)
            if (
                rec.allow_custom_currency_rate
                and rec.company_id.currency_id
                and rec.currency_id != rec.company_id.currency_id
                and rec.new_currency_rate == 0
            ):
                raise ValidationError(_("Update new currency rate."))
        return True

    def action_create_invoice(self):
        """
        super called based on the picking new currency rate or order new currency rate
        @return: super call
        """
        for rec in self:
            currency_rate = rec.new_currency_rate
            new_rate_picking = rec.picking_ids.filtered(
                lambda e: e.new_currency_rate
            ).mapped("new_currency_rate")
            currency_rate = (
                len(new_rate_picking) and new_rate_picking[0] or currency_rate
            )
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=currency_rate, is_custom_currency=True)
            super(PurchaseOrder, rec).action_create_invoice()
        return self.action_view_invoice(self.invoice_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """
        raise validation if currency rate is not set in the record if the currency id of the order is not equals
        to the company currency.
        @param vals_list: record values to create
        @return: super call result
        """
        if all(self.mapped("allow_custom_currency_rate")):
            self = self.with_context(new_currency_rate=self.new_currency_rate)
        result = super(PurchaseOrder, self).create(vals_list)
        if (
            result
            and result.allow_custom_currency_rate
            and result.new_currency_rate == 0
            and result.currency_id != result.company_id.currency_id
        ):
            raise ValidationError(_("Update new currency rate."))
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

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

    @api.depends('product_qty', 'company_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        """
        Passing currency rate context while computing price unit for a particular line
        @return: no return
        """
        for rec in self:
            if rec.order_id.allow_custom_currency_rate and rec.order_id.new_currency_rate:
                rec = rec.with_context(
                    new_currency_rate=1 / rec.order_id.new_currency_rate)
            super(PurchaseOrderLine, rec)._compute_price_unit_and_date_planned_and_name()
