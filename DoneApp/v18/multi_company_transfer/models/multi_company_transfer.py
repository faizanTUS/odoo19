# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MultiCompanyTransfer(models.Model):
    _name = 'multi.company.transfer'
    _description = 'Multi-Company Stock Transfer'
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    from_company_id = fields.Many2one(
        'res.company',
        string='From Company',
        required=True,
        ondelete='restrict',
    )
    to_company_id = fields.Many2one(
        'res.company',
        string='To Company',
        required=True,
        ondelete='restrict',
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
        domain="[('company_id', '=', from_company_id), ('usage', '=', 'internal')]",
    )
    destination_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        domain="[('company_id', '=', to_company_id), ('usage', '=', 'internal')]",
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('ready', 'Ready'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
    )
    stock_line_ids = fields.One2many(
        'multi.company.transfer.line',
        'transfer_id',
        string='Transfer Lines',
        copy=True,
    )
    outgoing_picking_id = fields.Many2one(
        'stock.picking',
        string='Outgoing Delivery Order',
        copy=False,
        readonly=True,
    )
    incoming_picking_id = fields.Many2one(
        'stock.picking',
        string='Incoming Delivery Order',
        copy=False,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'multi.company.transfer'
                ) or _('New')
        return super().create(vals_list)

    @api.constrains('from_company_id', 'to_company_id')
    def _check_companies_different(self):
        for rec in self:
            if rec.from_company_id and rec.to_company_id:
                if rec.from_company_id == rec.to_company_id:
                    raise ValidationError(
                        _('From Company and To Company must be different.')
                    )

    def _get_transit_location(self):
        """Get a transit location (shared or from source company)."""
        transit = self.env['stock.location'].search(
            [('usage', '=', 'transit')],
            limit=1,
            order='id',
        )
        if not transit:
            raise UserError(
                _('No transit location found. Please create a location with usage "Transit".')
            )
        return transit

    def _get_picking_type(self, company, code):
        picking_type = self.env['stock.picking.type'].search(
            [
                ('company_id', '=', company.id),
                ('code', '=', code),
            ],
            limit=1,
        )
        if not picking_type:
            raise UserError(
                _('No %s operation type found for company %s.')
                % (code, company.name)
            )
        return picking_type

    def action_check_availability(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft transfers can be checked.'))
        if not self.stock_line_ids:
            raise UserError(_('Add at least one line before checking availability.'))
        if self.from_company_id == self.to_company_id:
            raise UserError(_('From Company and To Company must be different.'))

        Quant = self.env['stock.quant']
        source = self.source_location_id
        for line in self.stock_line_ids:
            available = Quant._get_available_quantity(
                line.product_id,
                source,
            )
            if line.quantity > available:
                raise UserError(
                    _('Selected product "%(product)s" is not available in the source location. '
                      'Requested: %(qty)s, Available: %(avail)s.')
                    % {
                        'product': line.product_id.display_name,
                        'qty': line.quantity,
                        'avail': available,
                    }
                )
            line.available_qty = available
        self.state = 'ready'

    def action_create_transfer(self):
        self.ensure_one()
        if self.state != 'ready':
            raise UserError(_('Transfer must be in Ready state to create pickings.'))
        if not self.stock_line_ids:
            raise UserError(_('At least one stock line is required.'))
        if self.from_company_id == self.to_company_id:
            raise UserError(_('From Company and To Company must be different.'))

        transit = self._get_transit_location()
        out_type = self._get_picking_type(self.from_company_id, 'outgoing')
        in_type = self._get_picking_type(self.to_company_id, 'incoming')

        # Outgoing picking: source -> transit
        out_vals = {
            'picking_type_id': out_type.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': transit.id,
            'origin': self.name,
            'move_ids': [
                (0, 0, {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.source_location_id.id,
                    'location_dest_id': transit.id,
                })
                for line in self.stock_line_ids
            ],
        }
        outgoing = self.env['stock.picking'].with_company(
            self.from_company_id
        ).create(out_vals)
        outgoing.action_confirm()
        outgoing.action_assign()

        # Incoming picking: transit -> destination
        in_vals = {
            'picking_type_id': in_type.id,
            'location_id': transit.id,
            'location_dest_id': self.destination_location_id.id,
            'origin': self.name,
            'move_ids': [
                (0, 0, {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': transit.id,
                    'location_dest_id': self.destination_location_id.id,
                })
                for line in self.stock_line_ids
            ],
        }
        incoming = self.env['stock.picking'].with_company(
            self.to_company_id
        ).create(in_vals)
        incoming.action_confirm()
        incoming.action_assign()

        self.write({
            'outgoing_picking_id': outgoing.id,
            'incoming_picking_id': incoming.id,
        })

        return True

    def action_set_to_draft(self):
        self.ensure_one()
        if self.state != 'ready':
            raise UserError(_('Only Ready transfers can be reset to Draft.'))
        if self.outgoing_picking_id or self.incoming_picking_id:
            raise UserError(
                _('Cannot reset to draft when pickings have already been created. '
                  'Cancel the related pickings first.')
            )
        self.state = 'draft'
        self.stock_line_ids.write({'available_qty': 0})

    def action_view_outgoing_picking(self):
        self.ensure_one()
        if not self.outgoing_picking_id:
            return
        return self._action_view_picking(self.outgoing_picking_id)

    def action_view_incoming_picking(self):
        self.ensure_one()
        if not self.incoming_picking_id:
            return
        return self._action_view_picking(self.incoming_picking_id)

    def _action_view_picking(self, picking):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'stock.action_picking_tree_all'
        )
        action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
        action['res_id'] = picking.id
        action['context'] = self.env.context
        return action

    def _transfer_done(self):
        """Called when both pickings are done. Update done_qty and state."""
        self.ensure_one()
        if self.state == 'done':
            return
        if not self.outgoing_picking_id or self.outgoing_picking_id.state != 'done':
            return
        if not self.incoming_picking_id or self.incoming_picking_id.state != 'done':
            return
        # Update done quantities from incoming moves (actual received)
        for line in self.stock_line_ids:
            move = self.incoming_picking_id.move_ids.filtered(
                lambda m: m.product_id == line.product_id
            )
            line.done_qty = sum(move.mapped('quantity'))
        self.state = 'done'
