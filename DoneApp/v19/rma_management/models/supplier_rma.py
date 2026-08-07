# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupplierRma(models.Model):
    _name = 'supplier.rma'
    _description = 'Supplier RMA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='SRMA Reference', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'),
    )
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    partner_id = fields.Many2one(
        'res.partner', string='Vendor',
        related='purchase_order_id.partner_id', store=True, readonly=False,
    )
    receipt_email = fields.Char(string='Receipt Email')
    receipt_phone = fields.Char(string='Receipt Phone')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    deadline = fields.Datetime(string='Deadline')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    reject_reason = fields.Text(string='Reason for Rejection')
    bulk_reason_id = fields.Many2one(
        'rma.reason', string='Apply Reason to All Lines',
        help="Selecting a reason here applies it to every line at once.",
    )

    rma_line_ids = fields.One2many('supplier.rma.line', 'rma_id', string='RMA Lines')
    replacement_line_ids = fields.One2many(
        'supplier.rma.replacement.line', 'rma_id', string='Replacement Lines',
    )

    outgoing_picking_id = fields.Many2one('stock.picking', string='Outgoing Picking', readonly=True)
    incoming_picking_id = fields.Many2one('stock.picking', string='Incoming Picking', readonly=True)
    credit_note_id = fields.Many2one('account.move', string='Vendor Credit Note', readonly=True)

    total_refund = fields.Monetary(
        string='Total Refund', compute='_compute_total_refund', store=True,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='purchase_order_id.currency_id', store=True, readonly=True,
    )

    outgoing_picking_count = fields.Integer(compute='_compute_document_counts')
    incoming_picking_count = fields.Integer(compute='_compute_document_counts')
    credit_note_count = fields.Integer(compute='_compute_document_counts')

    @api.depends('outgoing_picking_id', 'incoming_picking_id', 'credit_note_id')
    def _compute_document_counts(self):
        for rma in self:
            rma.outgoing_picking_count = 1 if rma.outgoing_picking_id else 0
            rma.incoming_picking_count = 1 if rma.incoming_picking_id else 0
            rma.credit_note_count = 1 if rma.credit_note_id else 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('supplier.rma') or _('New')
        return super().create(vals_list)

    @api.depends('rma_line_ids.subtotal', 'rma_line_ids.action')
    def _compute_total_refund(self):
        for rma in self:
            rma.total_refund = sum(
                line.subtotal for line in rma.rma_line_ids
                if line.action == 'return_refund'
            )

    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        if not self.purchase_order_id:
            return
        self.partner_id = self.purchase_order_id.partner_id
        self.receipt_email = self.purchase_order_id.partner_id.email
        self.receipt_phone = self.purchase_order_id.partner_id.phone
        lines = []
        for po_line in self.purchase_order_id.order_line:
            lines.append((0, 0, {
                'product_id': po_line.product_id.id,
                'delivered_qty': po_line.qty_received,
                'return_qty': 0.0,
                'unit_price': po_line.price_unit,
                'tax_ids': [(6, 0, po_line.tax_ids.ids)],
            }))
        self.rma_line_ids = [(5, 0, 0)] + lines

    @api.onchange('bulk_reason_id')
    def _onchange_bulk_reason(self):
        if self.bulk_reason_id and self.rma_line_ids:
            mapping = {
                'return_refund': 'return_refund',
                'replacement': 'replacement',
                'only_return': 'return_refund',
                'no_action': 'return_refund',
                'contact_support': 'return_refund',
            }
            default_action = mapping.get(self.bulk_reason_id.action, 'return_refund')
            for line in self.rma_line_ids:
                line.reason_id = self.bulk_reason_id
                line.action = default_action

    def action_apply_bulk_reason(self):
        self.ensure_one()
        if not self.bulk_reason_id:
            raise UserError(_("Please select a reason to apply."))
        mapping = {
            'return_refund': 'return_refund',
            'replacement': 'replacement',
            'only_return': 'return_refund',
            'no_action': 'return_refund',
            'contact_support': 'return_refund',
        }
        default_action = mapping.get(self.bulk_reason_id.action, 'return_refund')
        self.rma_line_ids.write({
            'reason_id': self.bulk_reason_id.id,
            'action': default_action,
        })

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_reject(self):
        self.ensure_one()
        return {
            'name': _('Reject Supplier RMA'),
            'type': 'ir.actions.act_window',
            'res_model': 'rma.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_srma_id': self.id, 'default_model_name': 'supplier.rma'},
        }

    def _create_outgoing_picking(self):
        self.ensure_one()
        return_lines = self.rma_line_ids.filtered(lambda l: l.return_qty > 0)
        if not return_lines:
            return False
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id.company_id', '=', self.company_id.id),
        ], limit=1)
        if not picking_type:
            return False
        supplier_loc = self.env['stock.location'].search(
            [('usage', '=', 'supplier')], limit=1,
        )
        source_location = picking_type.default_location_src_id \
            or self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        moves = []
        for line in return_lines:
            moves.append((0, 0, {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.return_qty,
                'product_uom': line.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': supplier_loc.id,
            }))
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': source_location.id,
            'location_dest_id': supplier_loc.id,
            'origin': self.name,
            'move_ids_without_package': moves,
        })
        self.outgoing_picking_id = picking.id
        return picking

    def _create_incoming_picking(self):
        self.ensure_one()
        if not self.replacement_line_ids:
            return False
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.company_id.id),
        ], limit=1)
        if not picking_type:
            return False
        supplier_loc = self.env['stock.location'].search(
            [('usage', '=', 'supplier')], limit=1,
        )
        dest_location = picking_type.default_location_dest_id \
            or self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        moves = []
        for line in self.replacement_line_ids:
            moves.append((0, 0, {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'location_id': supplier_loc.id,
                'location_dest_id': dest_location.id,
            }))
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': supplier_loc.id,
            'location_dest_id': dest_location.id,
            'origin': self.name,
            'move_ids_without_package': moves,
        })
        self.incoming_picking_id = picking.id
        return picking

    def _create_vendor_credit_note(self):
        self.ensure_one()
        refund_lines = self.rma_line_ids.filtered(lambda l: l.action == 'return_refund')
        if not refund_lines:
            return False
        invoice_lines = []
        for line in refund_lines:
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.return_qty,
                'price_unit': line.unit_price,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }))
        move = self.env['account.move'].create({
            'move_type': 'in_refund',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
        })
        self.credit_note_id = move.id
        return move

    def action_approve(self):
        for rma in self:
            rma._create_outgoing_picking()
            rma._create_incoming_picking()
            rma._create_vendor_credit_note()
        self.write({'state': 'approved'})

    def action_process(self):
        self.write({'state': 'processing'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_view_outgoing_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Outgoing Picking'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.outgoing_picking_id.id,
        }

    def action_view_incoming_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Incoming Picking'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.incoming_picking_id.id,
        }

    def action_view_credit_note(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Credit Note'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.credit_note_id.id,
        }


class SupplierRmaLine(models.Model):
    _name = 'supplier.rma.line'
    _description = 'Supplier RMA Line'

    rma_id = fields.Many2one('supplier.rma', string='SRMA Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    action = fields.Selection([
        ('return_refund', 'Return & Refund'),
        ('replacement', 'Replacement'),
    ], string='Action', default='return_refund')
    reason_id = fields.Many2one('rma.reason', string='Reason')
    delivered_qty = fields.Float(string='Delivered Qty')
    return_qty = fields.Float(string='Return Qty', default=1.0)
    replace_qty = fields.Float(string='Replace Qty')
    unit_price = fields.Float(string='Unit Price')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    subtotal = fields.Float(string='Total', compute='_compute_subtotal', store=True)

    @api.depends('return_qty', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.return_qty * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.rma_id.purchase_order_id:
            po_line = self.rma_id.purchase_order_id.order_line.filtered(
                lambda l: l.product_id == self.product_id,
            )
            if po_line:
                self.delivered_qty = sum(po_line.mapped('qty_received'))
                self.unit_price = po_line[0].price_unit
                self.tax_ids = po_line[0].tax_ids


class SupplierRmaReplacementLine(models.Model):
    _name = 'supplier.rma.replacement.line'
    _description = 'Supplier RMA Replacement Line'

    rma_id = fields.Many2one('supplier.rma', string='SRMA Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price = fields.Float(string='Price')
