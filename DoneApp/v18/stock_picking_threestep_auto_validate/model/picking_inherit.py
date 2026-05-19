# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_pick_type = fields.Boolean(
        compute='_compute_is_pick_type',
        store=True,
    )

    @api.depends(
        'picking_type_id',
        'picking_type_id.warehouse_id',
        'picking_type_id.warehouse_id.pick_type_id',
    )
    def _compute_is_pick_type(self):
        for picking in self:
            ptype = picking.picking_type_id
            wh = ptype.warehouse_id
            picking.is_pick_type = bool(ptype and wh and wh.pick_type_id == ptype)

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if not picking.is_pick_type or not picking.sale_id:
                continue
            next_picking = picking._get_next_transfers()
            while next_picking:
                ptype = next_picking.picking_type_id
                if ptype.pack_auto_validate or ptype.delivery_auto_validate:
                    _logger.info(
                        "Auto-validating chained picking %s (type %s)",
                        next_picking.name,
                        ptype.id,
                    )
                    company = next_picking.company_id
                    if (
                        company.stock_move_sms_validation
                        and not company.has_received_warning_stock_sms
                    ):
                        _logger.info("==> SMS Validation required for %s", next_picking.name)
                        sms_wizard = self.env['confirm.stock.sms'].with_context(
                            active_model='stock.picking',
                            active_ids=[next_picking.id],
                            button_validate_picking_ids=[next_picking.id],
                        ).create({'pick_ids': [(6, 0, [next_picking.id])]})
                        sms_wizard.send_sms()
                    else:
                        next_picking.button_validate()

                    next_picking = next_picking._get_next_transfers()
                else:
                    next_picking = False
        return res
