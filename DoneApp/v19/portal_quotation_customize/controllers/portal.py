# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.addons.portal.controllers.portal import CustomerPortal


class SalePortalQty(CustomerPortal):

    @http.route(
        ['/my/orders/<int:order_id>/update_line_qty'],
        type='jsonrpc',
        auth='public',
        website=True,
    )
    def portal_update_line_qty(self, order_id, line_id, quantity,
                               access_token=None, **kwargs):
        """Update SO line quantity from portal.

        Security:
        - Access checked via _document_check_access with access_token.
        - Ensures line belongs to that order.
        """
        try:
            order_sudo = self._document_check_access(
                'sale.order', order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            # generic error for portal
            return {'success': False, 'error': _("Access denied.")}

        line = request.env['sale.order.line'].sudo().browse(int(line_id))
        if not line or line.order_id.id != order_sudo.id:
            return {'success': False, 'error': _("Invalid order line.")}

        try:
            line.portal_update_qty(quantity)
        except UserError as e:
            return {'success': False, 'error': e}

        # After successful update, send back portal URL so JS can refresh
        return {
            'success': True,
            'redirect_url': order_sudo.get_portal_url(),
        }

    @http.route(
        ['/my/orders/<int:order_id>/delete_line'],
        type='jsonrpc',
        auth='public',
        website=True,
    )
    def portal_delete_line(self, order_id, line_id,
                           access_token=None, **kwargs):
        """Delete SO line from portal."""
        try:
            order_sudo = self._document_check_access(
                'sale.order', order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return {'success': False, 'error': _("Access denied.")}

        line = request.env['sale.order.line'].sudo().browse(int(line_id))
        if not line or line.order_id.id != order_sudo.id:
            return {'success': False, 'error': _("Invalid order line.")}

        try:
            line.portal_delete_line()
        except UserError as e:
            return {'success': False, 'error': e}

        return {
            'success': True,
            'redirect_url': order_sudo.get_portal_url(),
        }
