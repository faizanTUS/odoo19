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

    def _get_next_transfers(self):
        next_pickings = self.move_ids.move_dest_ids.picking_id
        return next_pickings.filtered(
            lambda p: not p.origin or self.name not in p.origin
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
        res = super(StockPicking, self).button_validate()

        if res is not True:
            return res

        for picking in self:
            if not (picking.is_pick_type and picking.sale_id):
                continue

            next_picking = picking._get_next_transfers()
            max_iterations = 10
            iteration = 0

            while next_picking and iteration < max_iterations:
                iteration += 1

                if not (
                    next_picking.picking_type_id.pack_auto_validate
                    or next_picking.picking_type_id.delivery_auto_validate
                ):
                    _logger.info("Skipping auto-validation for %s - not configured", next_picking.name)
                    break

                _logger.info(
                    "Auto-validating chained picking %s (%s)",
                    next_picking.name,
                    next_picking.picking_type_id.name,
                )

                company = next_picking.company_id
                if company.stock_move_sms_validation and not company.has_received_warning_stock_sms:
                    _logger.info("==> SMS Validation required for %s", next_picking.name)
                    try:
                        sms_wizard = self.env['confirm.stock.sms'].with_context(
                            active_model='stock.picking',
                            active_ids=[next_picking.id],
                            button_validate_picking_ids=[next_picking.id],
                        ).create({'pick_ids': [(6, 0, [next_picking.id])]})
                        sms_wizard.send_sms()
                        break
                    except Exception as e:
                        _logger.error("SMS validation failed for %s: %s", next_picking.name, str(e))
                        break

                try:
                    if next_picking.state in ('confirmed', 'waiting'):
                        next_picking.action_assign()

                    next_picking.action_set_quantities_to_reservation()
                    validation_res = next_picking.button_validate()

                    if validation_res is not True:
                        break

                    _logger.info("Successfully validated %s", next_picking.name)

                except Exception:
                    break

                next_picking = next_picking._get_next_transfers()

            if iteration >= max_iterations:
                _logger.warning("Auto-validation stopped after %d iterations", max_iterations)

        return res
