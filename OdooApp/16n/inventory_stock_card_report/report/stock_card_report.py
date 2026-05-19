# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)


class StockCardReportPDF(models.AbstractModel):
    _name = "report.inventory_stock_card_report.stock_card_template"
    _description = "Stock Card PDF Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.warning("STOCK CARD REPORT _get_report_values CALLED")

        if not data or not data.get("wizard_id"):
            return {
                "data": {
                    "header": {
                        "warehouse": "",
                        "location": "",
                        "date_from": "",
                        "date_to": "",
                        "generated_by": "",
                    },
                    "groups": [],
                }
            }

        wizard = self.env["stock.card.wizard"].browse(data["wizard_id"]).ensure_one()

        engine = self.env["inventory.stock.card.engine"]
        payload = engine.get_report_data(wizard)

        return {
            "doc_ids": wizard.ids,
            "doc_model": "stock.card.wizard",
            "wizard": wizard,
            "data": payload,
        }
