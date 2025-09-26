# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    invoice_ids = fields.One2many('account.move', 'picking_id', string='Invoices', readonly=True)


    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for picking in self:
            picking.invoice_count = len(picking.invoice_ids)

    def action_create_invoice(self):
        self.ensure_one()
        invoice = self._create_invoice()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'views': [(self.env.ref('account.view_move_form').id, 'form')],
            'target': 'current',
        }

    def _create_invoice(self):
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'picking_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.product_uom_qty,
                'price_unit': line.product_id.lst_price,

            }) for line in self.move_ids],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_ids = [(4, invoice.id)]
        return invoice

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        if len(self.invoice_ids) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.invoice_ids.id
        return action

    # def action_view_invoices(self):
    #     self.ensure_one()
    #     invoices = self.env['account.move'].search([('invoice_origin', '=', self.name)])
    #     action = self.env.ref('account.action_move_out_invoice_type').read()[0]
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif invoices:
    #         action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
    #         action['res_id'] = invoices.id
    #     return action
    #
    # def action_create_invoice(self):
    #     self.ensure_one()
    #     invoice_vals = {
    #         'move_type': 'out_invoice',
    #         'partner_id': self.partner_id.id,
    #         'invoice_origin': self.name,
    #         'invoice_line_ids': [],
    #     }
    #     for move_line in self.move_line_ids:
    #         product = move_line.product_id
    #         invoice_line_vals = {
    #             'product_id': product.id,
    #             'quantity': move_line.quantity,
    #             'price_unit': product.lst_price,
    #             'name': product.display_name,
    #         }
    #         invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
    #     invoice = self.env['account.move'].create(invoice_vals)
    #     return {
    #         'name': 'Invoice',
    #         'view_mode': 'form',
    #         'res_model': 'account.move',
    #         'res_id': invoice.id,
    #         'view_id': self.env.ref('account.view_move_form').id,
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #     }
