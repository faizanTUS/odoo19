# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models

class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"

    product_template_id = fields.Many2one(
        "product.template", compute="_compute_parent_values"
    )
    partner_id = fields.Many2one("res.partner", compute="_compute_parent_values")
    user_id = fields.Many2one("res.users", compute="_compute_parent_values")
    date_order = fields.Datetime(compute="_compute_parent_values")

    @api.depends("product_id")
    def _compute_parent_values(self):
        for record in self:
            record.partner_id = record.order_id.partner_id.id
            record.product_template_id = record.product_id.product_tmpl_id.id
            record.user_id = record.order_id.user_id.id
            record.date_order = record.order_id.date_order
