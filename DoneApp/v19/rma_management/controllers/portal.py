# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal


class RmaPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'rma_count' in counters:
            values['rma_count'] = request.env['customer.rma'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
            ]) if request.env.user.partner_id else 0
        return values

    @http.route(['/my/returns', '/my/returns/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_returns(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        CustomerRma = request.env['customer.rma']
        domain = [('partner_id', '=', request.env.user.partner_id.id)]

        rma_count = CustomerRma.search_count(domain)
        pager = request.website.pager(
            url='/my/returns',
            total=rma_count,
            page=page,
            step=self._items_per_page,
        )
        rmas = CustomerRma.search(
            domain, limit=self._items_per_page, offset=pager['offset'], order='id desc',
        )

        values.update({
            'rmas': rmas,
            'page_name': 'rma',
            'pager': pager,
            'default_url': '/my/returns',
        })
        return request.render('rma_management.portal_my_returns', values)

    @http.route(['/my/rma/<int:rma_id>'], type='http', auth='user', website=True)
    def portal_rma_detail(self, rma_id, **kw):
        try:
            rma_sudo = self._document_check_access('customer.rma', rma_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = {
            'rma': rma_sudo,
            'page_name': 'rma',
        }
        return request.render('rma_management.portal_rma_detail', values)

    @http.route(['/my/rma/create/<int:order_id>'], type='http', auth='user', website=True)
    def portal_rma_create(self, order_id, **kw):
        order = request.env['sale.order'].browse(order_id)
        if not order.exists() or order.partner_id != request.env.user.partner_id:
            return request.redirect('/my/orders')

        reasons = request.env['rma.reason'].search([('active', '=', True)])
        partner = request.env.user.partner_id
        addresses = partner | partner.child_ids
        values = {
            'order': order,
            'reasons': reasons,
            'addresses': addresses,
            'page_name': 'rma',
        }
        return request.render('rma_management.portal_rma_submission_form', values)

    @http.route(['/my/rma/submit'], type='http', auth='user',
                methods=['POST'], website=True, csrf=True)
    def portal_rma_submit(self, **post):
        try:
            order_id = int(post.get('order_id') or 0)
        except (TypeError, ValueError):
            return request.redirect('/my/orders')
        order = request.env['sale.order'].browse(order_id)
        if not order.exists() or order.partner_id != request.env.user.partner_id:
            return request.redirect('/my/orders')

        try:
            return_address_id = int(post.get('return_address_id') or 0) or order.partner_shipping_id.id
        except (TypeError, ValueError):
            return_address_id = order.partner_shipping_id.id

        line_vals = []
        for sol in order.order_line:
            if sol.display_type:
                continue
            if not post.get('select_%s' % sol.id):
                continue
            qty_raw = post.get('qty_%s' % sol.id) or '0'
            reason_raw = post.get('reason_%s' % sol.id) or False
            action_raw = post.get('action_%s' % sol.id) or 'return_refund'
            try:
                qty = float(qty_raw)
            except (TypeError, ValueError):
                qty = 0.0
            if qty <= 0:
                continue
            if qty > sol.qty_delivered:
                qty = sol.qty_delivered
            reason = request.env['rma.reason'].sudo().browse(
                int(reason_raw)
            ) if reason_raw else False
            if action_raw not in ('return_refund', 'replacement', 'no_action'):
                action_raw = 'return_refund'
            line_vals.append((0, 0, {
                'product_id': sol.product_id.id,
                'quantity': qty,
                'delivered_qty': sol.qty_delivered,
                'reason_id': reason.id if reason else False,
                'action': action_raw,
                'unit_price': sol.price_unit,
                'tax_ids': [(6, 0, sol.tax_id.ids)],
            }))

        if not line_vals:
            return request.redirect('/my/rma/create/%s' % order.id)

        rma = request.env['customer.rma'].sudo().create({
            'sale_order_id': order.id,
            'partner_id': order.partner_id.id,
            'return_address_id': return_address_id,
            'state': 'submitted',
            'rma_line_ids': line_vals,
        })
        template = request.env.ref(
            'rma_management.email_template_rma_submitted', raise_if_not_found=False,
        )
        if template:
            template.sudo().send_mail(rma.id, force_send=False)
        return request.redirect('/my/rma/%s' % rma.id)
