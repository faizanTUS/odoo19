# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_pick_type = fields.Boolean(compute="compute_picking_type", store=True)

#       without sms config
    def button_validate(self):
        res = super(StockPicking, self.with_context(is_validate_write=True)).button_validate()
        for rec in self:
            if rec.is_pick_type and rec.sale_id:
                next_t = rec._get_next_transfers()
                # if next_t.picking_type_id.pack_auto_validate:
                while next_t:
                    # next_t.button_validate()
                    # if next_t._get_next_transfers().picking_type_id.delivery_auto_validate:
                    # if next_t.picking_type_id.pack_auto_validate or next_t._get_next_transfers().picking_type_id.delivery_auto_validate:
                    if next_t.picking_type_id.pack_auto_validate or next_t.picking_type_id.delivery_auto_validate:
                        _logger.info("==================Validating picking: %s (%s)", next_t.name, next_t.picking_type_id.id)

                        next_t.button_validate()
                        next_t = next_t._get_next_transfers()
                    else:
                        next_t = False
        return res

    # def button_validate(self):
    #     res = super(StockPicking, self.with_context(is_validate_write=True)).button_validate()
    #     for rec in self:
    #         if rec.is_pick_type and rec.sale_id:
    #             next_t = rec._get_next_transfers()
    #             while next_t:
    #                 if next_t.picking_type_id.pack_auto_validate or next_t.picking_type_id.delivery_auto_validate:
    #                     _logger.info("==================Auto-validating picking: %s (%s)", next_t.name,
    #                                  next_t.picking_type_id.id)
    #
    #                     company = next_t.company_id
    #                     # if company.stock_move_sms_validation and not company.has_received_warning_stock_sms:
    #                     if not company.has_received_warning_stock_sms:
    #                         _logger.info("==> SMS Validation required for %s", next_t.name)
    #
    #                         sms_wizard = self.env['confirm.stock.sms'].with_context(
    #                             active_model='stock.picking',
    #                             active_ids=[next_t.id],
    #                             button_validate_picking_ids=[next_t.id]
    #                         ).create({'pick_ids': [(6, 0, [next_t.id])]})
    #                         sms_wizard.send_sms()
    #                     else:
    #                         next_t.button_validate()
    #
    #                     next_t = next_t._get_next_transfers()
    #                 else:
    #                     next_t = False
    #     return res

    @api.depends('picking_type_id')
    def compute_picking_type(self):
        for record in self:
            is_pick_type = False
            if record.picking_type_id and record.picking_type_id.warehouse_id.pick_type_id == record.picking_type_id:
                is_pick_type = True
            record.is_pick_type = is_pick_type

