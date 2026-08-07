from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rma_product_type_id = fields.Many2one('rma.product.type', string='RMA Product Type')
    rma_threshold = fields.Float(
        string='RMA Return Qty Threshold',
        help="Minimum return qty that still requires a pickup. If the requested "
             "return qty is below this threshold, the customer is refunded/replaced "
             "without scheduling a pickup.",
    )
    rma_reason_id = fields.Many2one(
        'rma.reason', string='Default RMA Reason',
        help="Suggested default reason when this product is added to an RMA.",
    )
