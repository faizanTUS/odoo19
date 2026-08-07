# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustomerRma(models.Model):
    _name = 'customer.rma'
    _description = 'Customer RMA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='RMA Reference', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'),
    )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        related='sale_order_id.partner_id', store=True, readonly=False,
    )
    return_address_id = fields.Many2one('res.partner', string='Return Address')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    rma_line_ids = fields.One2many('customer.rma.line', 'rma_id', string='RMA Lines')
    replacement_line_ids = fields.One2many(
        'customer.rma.replacement.line', 'rma_id', string='Replacement Lines',
    )

    reject_reason = fields.Text(string='Reason for Rejection')
    bulk_reason_id = fields.Many2one(
        'rma.reason', string='Apply Reason to All Lines',
        help="Selecting a reason here applies it (and its default action) to every line at once.",
    )
    priority = fields.Selection([
        ('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Very High'),
    ], string='Priority', default='1')
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company,
    )

    picking_id = fields.Many2one('stock.picking', string='Return Picking', readonly=True)
    replacement_order_id = fields.Many2one('sale.order', string='Replacement Order', readonly=True)
    credit_note_id = fields.Many2one('account.move', string='Credit Note', readonly=True)

    total_refund_amount = fields.Monetary(
        string='Total Refund Amount', compute='_compute_total_refund', store=True,
    )
    restocking_fee = fields.Monetary(
        string='Restocking Fee', compute='_compute_restocking_fee', store=True,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='sale_order_id.currency_id', store=True, readonly=True,
    )
    valid_product_ids = fields.Many2many(
        'product.product', compute='_compute_valid_products',
    )

    picking_count = fields.Integer(compute='_compute_document_counts')
    credit_note_count = fields.Integer(compute='_compute_document_counts')
    replacement_order_count = fields.Integer(compute='_compute_document_counts')

    @api.depends('picking_id', 'credit_note_id', 'replacement_order_id')
    def _compute_document_counts(self):
        for rma in self:
            rma.picking_count = 1 if rma.picking_id else 0
            rma.credit_note_count = 1 if rma.credit_note_id else 0
            rma.replacement_order_count = 1 if rma.replacement_order_id else 0

    @api.depends('sale_order_id')
    def _compute_valid_products(self):
        for rma in self:
            rma.valid_product_ids = rma.sale_order_id.order_line.mapped('product_id') \
                if rma.sale_order_id else self.env['product.product']

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.rma') or _('New')
        return super().create(vals_list)

    @api.depends('rma_line_ids.subtotal', 'rma_line_ids.action')
    def _compute_total_refund(self):
        for rma in self:
            rma.total_refund_amount = sum(
                line.subtotal for line in rma.rma_line_ids
                if line.action == 'return_refund'
            )

    @api.depends('rma_line_ids.subtotal', 'rma_line_ids.action')
    def _compute_restocking_fee(self):
        fee_config = self.env['rma.restock.fee'].search([('active', '=', True)], limit=1)
        for rma in self:
            fee = 0.0
            if fee_config:
                refund_lines = rma.rma_line_ids.filtered(lambda l: l.action == 'return_refund')
                if fee_config.fee_type == 'percentage':
                    fee = sum(l.subtotal * (fee_config.amount / 100.0) for l in refund_lines)
                elif refund_lines:
                    fee = fee_config.amount
            rma.restocking_fee = fee

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id
            self.return_address_id = self.sale_order_id.partner_shipping_id

    @api.constrains('rma_line_ids')
    def _check_return_quantity(self):
        for rma in self:
            for line in rma.rma_line_ids:
                if line.quantity <= 0:
                    raise UserError(_("Return quantity must be greater than zero."))
                if line.delivered_qty and line.quantity > line.delivered_qty:
                    raise UserError(_(
                        "Return quantity for product %(p)s cannot exceed delivered quantity (%(q)s).",
                        p=line.product_id.display_name, q=line.delivered_qty,
                    ))

    def _lines_require_pickup(self):
        """Return the RMA lines that need a pickup. Lines whose return qty is below
        the product's RMA threshold skip the pickup (cost-of-return optimization)."""
        self.ensure_one()
        to_pick = self.env['customer.rma.line']
        for line in self.rma_line_ids:
            threshold = line.product_id.product_tmpl_id.rma_threshold or 0.0
            if threshold and line.quantity < threshold:
                continue
            to_pick |= line
        return to_pick

    _REASON_TO_ACTION = {
        'return_refund': 'return_refund',
        'replacement': 'replacement',
        'only_return': 'no_action',
        'no_action': 'no_action',
        'contact_support': 'no_action',
    }

    @api.onchange('bulk_reason_id')
    def _onchange_bulk_reason(self):
        if self.bulk_reason_id and self.rma_line_ids:
            default_action = self._REASON_TO_ACTION.get(self.bulk_reason_id.action, 'return_refund')
            for line in self.rma_line_ids:
                line.reason_id = self.bulk_reason_id
                line.action = default_action

    def action_apply_bulk_reason(self):
        self.ensure_one()
        if not self.bulk_reason_id:
            raise UserError(_("Please select a reason to apply."))
        default_action = self._REASON_TO_ACTION.get(self.bulk_reason_id.action, 'return_refund')
        self.rma_line_ids.write({
            'reason_id': self.bulk_reason_id.id,
            'action': default_action,
        })

    def action_submit(self):
        self.write({'state': 'submitted'})
        template = self.env.ref('rma_management.email_template_rma_submitted', raise_if_not_found=False)
        if template:
            for rma in self:
                template.send_mail(rma.id, force_send=False)

    def _create_return_picking(self):
        self.ensure_one()
        pickup_lines = self._lines_require_pickup()
        if not pickup_lines:
            return False
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.company_id.id),
        ], limit=1)
        if not picking_type:
            return False
        customer_loc = self.env['stock.location'].search(
            [('usage', '=', 'customer')], limit=1,
        )
        dest_location = picking_type.default_location_dest_id \
            or self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        moves = []
        for line in pickup_lines:
            moves.append((0, 0, {
                'description_picking': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'location_id': customer_loc.id,
                'location_dest_id': dest_location.id,
            }))
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': customer_loc.id,
            'location_dest_id': dest_location.id,
            'origin': self.name,
            'move_ids': moves,
        })
        self.picking_id = picking.id
        return picking

    def _create_credit_note(self):
        self.ensure_one()
        refund_lines = self.rma_line_ids.filtered(lambda l: l.action == 'return_refund')
        if not refund_lines:
            return False
        invoice_lines = []
        for line in refund_lines:
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }))
        if self.restocking_fee > 0:
            invoice_lines.append((0, 0, {
                'name': _('Restocking Fee'),
                'quantity': 1,
                'price_unit': -self.restocking_fee,
            }))
        move = self.env['account.move'].create({
            'move_type': 'out_refund',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
        })
        self.credit_note_id = move.id
        return move

    def _create_replacement_order(self):
        self.ensure_one()
        replacement_lines_from_rma = self.rma_line_ids.filtered(lambda l: l.action == 'replacement')
        if not (self.replacement_line_ids or replacement_lines_from_rma):
            return False
        order_lines = []
        for line in self.replacement_line_ids:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.price,
            }))
        for line in replacement_lines_from_rma:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': 0.0,
            }))
        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'order_line': order_lines,
        })
        self.replacement_order_id = order.id
        return order

    def action_approve(self):
        for rma in self:
            rma._create_return_picking()
            rma._create_credit_note()
            rma._create_replacement_order()
        self.write({'state': 'approved'})
        template = self.env.ref('rma_management.email_template_rma_approved', raise_if_not_found=False)
        if template:
            for rma in self:
                template.send_mail(rma.id, force_send=False)

    def action_process(self):
        self.write({'state': 'processing'})

    def action_reject(self):
        self.ensure_one()
        return {
            'name': _('Reject RMA'),
            'type': 'ir.actions.act_window',
            'res_model': 'rma.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_rma_id': self.id, 'default_model_name': 'customer.rma'},
        }

    def action_view_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Return Picking'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
        }

    def action_view_credit_note(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Credit Note'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.credit_note_id.id,
        }

    def action_view_replacement_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Replacement Order'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.replacement_order_id.id,
        }

    def action_close(self):
        self.write({'state': 'closed'})
        template = self.env.ref('rma_management.email_template_rma_closed', raise_if_not_found=False)
        if template:
            for rma in self:
                template.send_mail(rma.id, force_send=False)

    def action_draft(self):
        self.write({'state': 'draft'})


class CustomerRmaLine(models.Model):
    _name = 'customer.rma.line'
    _description = 'Customer RMA Line'

    rma_id = fields.Many2one('customer.rma', string='RMA Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Return Qty', required=True, default=1.0)
    delivered_qty = fields.Float(string='Delivered Qty', readonly=True)
    reason_id = fields.Many2one('rma.reason', string='Reason')
    action = fields.Selection([
        ('return_refund', 'Return & Refund'),
        ('replacement', 'Replacement'),
        ('no_action', 'No Action'),
    ], string='Action')
    unit_price = fields.Float(string='Unit Price')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    subtotal = fields.Float(string='Total', compute='_compute_subtotal', store=True)
    pickup_required = fields.Boolean(
        string='Pickup Required', compute='_compute_pickup_required', store=True,
    )

    @api.depends('quantity', 'product_id.rma_threshold')
    def _compute_pickup_required(self):
        for line in self:
            threshold = line.product_id.product_tmpl_id.rma_threshold or 0.0
            line.pickup_required = not (threshold and line.quantity < threshold)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.rma_id.sale_order_id:
            order_line = self.rma_id.sale_order_id.order_line.filtered(
                lambda l: l.product_id == self.product_id,
            )
            if order_line:
                self.delivered_qty = sum(order_line.mapped('qty_delivered'))
                self.unit_price = order_line[0].price_unit
                self.tax_ids = order_line[0].tax_ids
                self.quantity = self.delivered_qty or 1.0
            if self.product_id.product_tmpl_id.rma_reason_id and not self.reason_id:
                self.reason_id = self.product_id.product_tmpl_id.rma_reason_id
            if self.reason_id and not self.action:
                reason_action = self.reason_id.action
                if reason_action == 'return_refund':
                    self.action = 'return_refund'
                elif reason_action == 'replacement':
                    self.action = 'replacement'
                else:
                    self.action = 'no_action'

    @api.onchange('reason_id')
    def _onchange_reason_id(self):
        if self.reason_id:
            mapping = {
                'return_refund': 'return_refund',
                'replacement': 'replacement',
                'only_return': 'no_action',
                'no_action': 'no_action',
                'contact_support': 'no_action',
            }
            self.action = mapping.get(self.reason_id.action, 'no_action')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price


class CustomerRmaReplacementLine(models.Model):
    _name = 'customer.rma.replacement.line'
    _description = 'Customer RMA Replacement Line'

    rma_id = fields.Many2one('customer.rma', string='RMA Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price = fields.Float(string='Price')
