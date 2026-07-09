# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, content_disposition


class FontController(http.Controller):

    @http.route(['/web/content/font/<int:font_id>/<string:filename>'], type='http', auth='public', methods=['GET'], csrf=False)
    def get_font_file(self, font_id, filename, **kwargs):
        """Serve font files publicly for PDF generation"""
        font_file = request.env['custom.font.file'].sudo().browse(font_id)
        if not font_file.exists() or not font_file.active or not font_file.font_file:
            return request.not_found()
        
        # Get attachment
        attachment = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'custom.font.file'),
            ('res_id', '=', font_id),
        ], limit=1)
        
        if not attachment:
            return request.not_found()
        
        # Determine content type
        if filename.endswith('.woff'):
            content_type = 'font/woff'
        elif filename.endswith('.woff2'):
            content_type = 'font/woff2'
        elif filename.endswith('.otf'):
            content_type = 'font/opentype'
        elif filename.endswith('.eot'):
            content_type = 'application/vnd.ms-fontobject'
        else:
            content_type = 'font/truetype'
        
        # Get raw font data from attachment
        font_data = attachment.raw
        if not font_data:
            # Fallback to font_file field - decode base64 if needed
            font_data = font_file.font_file
            if isinstance(font_data, str):
                import base64
                try:
                    font_data = base64.b64decode(font_data)
                except Exception:
                    # If already decoded or not base64, use as is
                    if isinstance(font_data, str):
                        font_data = font_data.encode('latin-1')
        
        return request.make_response(
            font_data,
            headers=[
                ('Content-Type', content_type),
                ('Content-Disposition', content_disposition(filename)),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET'),
                ('Cache-Control', 'public, max-age=31536000'),
            ]
        )

