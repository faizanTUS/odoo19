# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_partner import _lang_get
import logging

_logger = logging.getLogger(__name__)


class MaterialRequisition(models.Model):
    _name = 'material.requisition'
    _description = 'Material Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _check_company_auto = True

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        index='trigram',
    )
    description = fields.Char(string='Description')
    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one(
        'res.users',
        string='Requested By',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        compute='_compute_employee_id',
        store=True,
        readonly=False,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
    requisition_type = fields.Selection(
        [
            ('purchase', 'Purchase'),
            ('internal', 'Internal'),
            ('both', 'Both'),
        ],
        string='Requisition Type',
        default='both',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved_manager', 'Approved by Department Manager'),
            ('approved_officer', 'Approved by Requisition Officer'),
            ('dispatch', 'Dispatch'),
            ('received', 'Received'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
    )
    line_ids = fields.One2many(
        'material.requisition.line',
        'requisition_id',
        string='Requisition Lines',
        copy=True,
    )
    approved_manager_id = fields.Many2one(
        'res.users',
        string='Approved by Manager',
        readonly=True,
        copy=False,
    )
    approved_manager_date = fields.Datetime(string='Manager Approval Date', readonly=True, copy=False)
    approved_officer_id = fields.Many2one(
        'res.users',
        string='Approved by Requisition Officer',
        readonly=True,
        copy=False,
    )
    approved_officer_date = fields.Datetime(string='Officer Approval Date', readonly=True, copy=False)
    rejected_by_id = fields.Many2one('res.users', string='Rejected By', readonly=True, copy=False)
    rejected_date = fields.Datetime(string='Rejection Date', readonly=True, copy=False)
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True, copy=False)

    picking_ids = fields.One2many(
        'stock.picking',
        'material_requisition_id',
        string='Pickings',
        readonly=True,
        copy=False,
    )
    picking_count = fields.Integer(compute='_compute_picking_count')
    # purchase_order_ids = fields.Many2many(
    #     'purchase.order',
    #     string='Purchase Orders',
    #     compute='_compute_purchase_order_ids',
    #     readonly=True,
    # )
    # purchase_order_count = fields.Integer(compute='_compute_purchase_order_count')

    @api.depends('requested_by_id')
    def _compute_employee_id(self):
        for req in self:
            if req.requested_by_id:
                emp = self.env['hr.employee'].search(
                    [('user_id', '=', req.requested_by_id.id), ('company_id', '=', req.company_id.id)],
                    limit=1,
                )
                req.employee_id = emp
                if emp and not req.department_id:
                    req.department_id = emp.department_id
            else:
                req.employee_id = False

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Purchase Orders',
        compute='_compute_purchase_orders',
        readonly=True,
    )
    purchase_order_count = fields.Integer(compute='_compute_purchase_orders')

    @api.depends('line_ids.picking_id')
    def _compute_picking_count(self):
        for req in self:
            req.picking_count = len(req.line_ids.mapped('picking_id'))

    @api.depends('line_ids.purchase_order_line_id.order_id')
    def _compute_purchase_orders(self):
        for req in self:
            orders = req.line_ids.mapped('purchase_order_line_id.order_id')
            req.purchase_order_ids = orders
            req.purchase_order_count = len(orders)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('material.requisition') or _('New')
        req = super().create(vals)
        if req.requested_by_id and not req.department_id and req.employee_id:
            req.department_id = req.employee_id.department_id
        if not req.dest_location_id and req.requested_by_id:
            loc = req.requested_by_id.material_requisition_stock_location_id
            if loc:
                req.dest_location_id = loc
        return req

    @api.constrains('line_ids', 'state')
    def _check_lines(self):
        for req in self:
            if req.state != 'draft' and not req.line_ids:
                raise ValidationError(_('At least one requisition line is required.'))

    def _get_config(self):
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'email_notification': ICP.get_param('material_requisition_advanced.set_email_notification', 'True') == 'True',
            'dept_manager_approval': ICP.get_param('material_requisition_advanced.set_department_manager_approval', 'True') == 'True',
            'officer_approval': ICP.get_param('material_requisition_advanced.set_requisition_officer_approval', 'True') == 'True',
        }

    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Please add at least one product line.'))
        if self.requisition_type == 'internal':
            wrong = self.line_ids.filtered(lambda l: l.requisition_action != 'internal')
            if wrong:
                raise UserError(_('All lines must be set to Internal Picking for this requisition type.'))
        elif self.requisition_type == 'purchase':
            wrong = self.line_ids.filtered(lambda l: l.requisition_action != 'purchase')
            if wrong:
                raise UserError(_('All lines must be set to Purchase Order for this requisition type.'))

        config = self._get_config()
        if config['dept_manager_approval'] and self.department_id and self.department_id.manager_id and self.department_id.manager_id.user_id:
            self.state = 'confirmed'
            if config['email_notification']:
                self._send_dept_manager_email()
        elif config['officer_approval']:
            self.state = 'confirmed'
            if config['email_notification']:
                self._send_requisition_officer_email()
        else:
            self.state = 'approved_officer'
            self.approved_officer_id = self.env.user
            self.approved_officer_date = fields.Datetime.now()
        return True

    def _send_dept_manager_email(self):
        template = self.env.ref(
            'material_requisition_advanced.mail_template_material_requisition_dept_manager',
            raise_if_not_found=False,
        )
        if not template:
            return
        for req in self:
            manager = req.department_id and req.department_id.manager_id and req.department_id.manager_id.user_id
            if manager and manager.partner_id:
                template.with_context(lang=manager.lang or manager.partner_id.lang).send_mail(
                    req.id,
                    force_send=False,
                    email_values={'email_to': manager.partner_id.email},
                )

    def _send_requisition_officer_email(self):
        template = self.env.ref(
            'material_requisition_advanced.mail_template_material_requisition_requisition_user',
            raise_if_not_found=False,
        )
        if not template:
            return
        officers = self.env['res.users'].search([('material_requisition_officer', '=', True)])
        for req in self:
            for officer in officers:
                if officer.partner_id and officer.partner_id.email:
                    template.with_context(lang=officer.lang or officer.partner_id.lang).send_mail(
                        req.id,
                        force_send=False,
                        email_values={'email_to': officer.partner_id.email},
                    )

    def action_approve_manager(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Only confirmed requisitions can be approved by the department manager.'))
        config = self._get_config()
        if config['officer_approval']:
            self.state = 'approved_manager'
            self.approved_manager_id = self.env.user
            self.approved_manager_date = fields.Datetime.now()
            if config['email_notification']:
                self._send_requisition_officer_email()
        else:
            self.state = 'approved_officer'
            self.approved_manager_id = self.env.user
            self.approved_manager_date = fields.Datetime.now()
            self.approved_officer_id = self.env.user
            self.approved_officer_date = fields.Datetime.now()
        return True

    def action_reject_manager(self):
        return self._reject('department manager')

    def action_approve_officer(self):
        self.ensure_one()
        if self.state not in ('confirmed', 'approved_manager'):
            raise UserError(_('Requisition must be in Confirmed or Approved by Manager state.'))
        self.state = 'approved_officer'
        if not self.approved_manager_id and self.state == 'approved_manager':
            self.approved_manager_id = self.env.user
            self.approved_manager_date = fields.Datetime.now()
        self.approved_officer_id = self.env.user
        self.approved_officer_date = fields.Datetime.now()
        return True

    def action_reject_officer(self):
        return self._reject('requisition officer')

    def _reject(self, by_who):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Material Requisition'),
            'res_model': 'material.requisition.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_requisition_id': self.id,
                'default_rejected_by': by_who,
            },
        }

    def action_received(self):
        self.ensure_one()
        if self.state != 'dispatch':
            raise UserError(_('Only requisitions in Dispatch state can be marked as Received.'))
        self.state = 'received'
        return True

    def action_reset_draft(self):
        self.ensure_one()
        if self.state not in ('draft', 'rejected'):
            raise UserError(_('Only draft or rejected requisitions can be reset.'))
        self.write({
            'state': 'draft',
            'approved_manager_id': False,
            'approved_manager_date': False,
            'approved_officer_id': False,
            'approved_officer_date': False,
            'rejected_by_id': False,
            'rejected_date': False,
            'rejection_reason': False,
        })
        return True

    def _check_and_set_dispatch(self):
        """Move to dispatch only when all lines have been processed."""
        internal_lines = self.line_ids.filtered(lambda l: l.requisition_action == 'internal')
        purchase_lines = self.line_ids.filtered(lambda l: l.requisition_action == 'purchase')

        internal_done = all(l.picking_id for l in internal_lines) if internal_lines else True
        purchase_done = all(l.purchase_order_line_id for l in purchase_lines) if purchase_lines else True

        if internal_done and purchase_done:
            self.state = 'dispatch'

    def action_create_picking(self):
        self.ensure_one()
        if self.state != 'approved_officer':
            raise UserError(_('Requisition must be approved by the requisition officer first.'))
        internal_lines = self.line_ids.filtered(lambda l: l.requisition_action == 'internal' and not l.picking_id)
        if not internal_lines:
            raise UserError(_('No lines with Internal Picking action to create picking.'))
        StockPicking = self.env['stock.picking']
        for line in internal_lines:
            picking_type = line.picking_type_id
            if not picking_type:
                raise UserError(
                    _('Picking Type is required for product "%s". Please set it on the requisition line.')
                    % line.product_id.display_name
                )
            source = line.requisition_id.source_location_id or picking_type.default_location_src_id
            dest = line.requisition_id.dest_location_id or picking_type.default_location_dest_id
            if not source or not dest:
                raise UserError(_('Source and Destination locations must be set for internal picking.'))
            vals = {
                'picking_type_id': picking_type.id,
                'location_id': source.id,
                'location_dest_id': dest.id,
                'origin': self.name,
                'material_requisition_id': self.id,
                'partner_id': False,
                'move_ids': [(0, 0, {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.required_qty,
                    'product_uom': line.product_uom_id.id,
                    'location_id': source.id,
                    'location_dest_id': dest.id,
                })],
            }
            picking = StockPicking.create(vals)
            line.picking_id = picking
        self._check_and_set_dispatch()
        return self.action_view_pickings()

    def action_create_purchase_order(self):
        self.ensure_one()
        if self.state != 'approved_officer':
            raise UserError(_('Requisition must be approved by the requisition officer first.'))
        purchase_lines = self.line_ids.filtered(
            lambda l: l.requisition_action == 'purchase' and not l.purchase_order_line_id
        )
        if not purchase_lines:
            raise UserError(_('No lines with Purchase Order action to create RFQ.'))
        missing = purchase_lines.filtered(lambda l: not l.vendor_id)
        if missing:
            raise UserError(
                _('Vendor is required for: %s') % ', '.join(missing.mapped('product_id.name'))
            )
        PurchaseOrder = self.env['purchase.order']
        by_vendor = {}
        for line in purchase_lines:
            key = line.vendor_id.id
            if key not in by_vendor:
                by_vendor[key] = []
            by_vendor[key].append(line)
        for vendor_id, lines in by_vendor.items():
            vendor = self.env['res.partner'].browse(vendor_id)
            order_vals = {
                'partner_id': vendor.id,
                'origin': self.name,
                'company_id': self.company_id.id,
                'order_line': [],
            }
            for line in lines:
                order_vals['order_line'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.required_qty,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.purchase_price or 0.0,
                    'name': line.description or line.product_id.display_name,
                }))
            po = PurchaseOrder.create(order_vals)
            for line in lines:
                pol = po.order_line.filtered(lambda l: l.product_id == line.product_id and l.product_qty == line.required_qty)
                if pol:
                    line.purchase_order_line_id = pol[:1]
        # if self.state == 'approved_officer':
        #     self.state = 'dispatch'
        self._check_and_set_dispatch()
        return self.action_view_purchase_orders()

    def action_view_pickings(self):
        self.ensure_one()
        pickings = self.line_ids.mapped('picking_id')
        if not pickings:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pickings'),
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', pickings.ids)],
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        orders = self.line_ids.mapped('purchase_order_line_id.order_id')
        if not orders:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Orders'),
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', orders.ids)],
        }
