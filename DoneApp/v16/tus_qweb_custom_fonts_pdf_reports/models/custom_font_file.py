# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import base64
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CustomFontFile(models.Model):
    _name = 'custom.font.file'
    _description = 'Custom Font File'
    _order = 'name'

    name = fields.Char(string='Font Name', required=True, help='Name of the font (e.g., Custom-font)')
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                 default=lambda self: self.env.company, 
                                 ondelete='cascade')
    font_file = fields.Binary(string='Font File', required=True, 
                             help='Upload font file (.ttf, .otf, etc.)')
    font_filename = fields.Char(string='Font Filename', compute='_compute_font_filename', store=True)
    font_family_name = fields.Char(string='Font Family Name', compute='_compute_font_family_name', 
                                   store=True, help='Name used in CSS font-family property')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('name')
    def _compute_font_family_name(self):
        """Generate a CSS-safe font family name from the font name"""
        for record in self:
            if record.name:
                # Replace spaces and special characters with underscores
                font_family = re.sub(r'[^a-zA-Z0-9_-]', '_', record.name)
                # Remove multiple consecutive underscores
                font_family = re.sub(r'_+', '_', font_family)
                # Remove leading/trailing underscores
                font_family = font_family.strip('_')
                record.font_family_name = font_family or 'CustomFont'
            else:
                record.font_family_name = 'CustomFont'

    @api.depends('font_file', 'font_family_name')
    def _compute_font_filename(self):
        """Extract filename from attachment if available"""
        for record in self:
            if record.font_file:
                # Try to get filename from attachment
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'custom.font.file'),
                    ('res_id', '=', record.id),
                ], limit=1)
                if attachment:
                    record.font_filename = attachment.name
                else:
                    # Default filename based on name - try to detect extension from name
                    if record.name and '.' in record.name:
                        ext = record.name.rsplit('.', 1)[1].lower()
                        if ext in ['ttf', 'otf', 'woff', 'woff2', 'eot']:
                            record.font_filename = f"{record.font_family_name}.{ext}"
                        else:
                            record.font_filename = f"{record.font_family_name}.ttf"
                    else:
                        record.font_filename = f"{record.font_family_name}.ttf"
            else:
                record.font_filename = False

    @api.constrains('font_file')
    def _check_font_file(self):
        """Validate that the uploaded file is a font file"""
        for record in self:
            if record.font_file:
                # Check if there's an attachment with valid extension
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'custom.font.file'),
                    ('res_id', '=', record.id),
                ], limit=1)
                if attachment:
                    valid_extensions = ['.ttf', '.otf', '.woff', '.woff2', '.eot']
                    if not any(attachment.name.lower().endswith(ext) for ext in valid_extensions):
                        raise ValidationError(_('Please upload a valid font file (.ttf, .otf, .woff, .woff2, .eot)'))

    @api.model_create_multi
    def create(self, vals_list):
        """Create attachment when font file is uploaded"""
        records = super().create(vals_list)
        for record in records:
            if record.font_file:
                record._create_font_attachment()
        return records

    def write(self, values):
        """Update attachment when font file is changed"""
        res = super().write(values)
        if 'font_file' in values:
            for record in self:
                if record.font_file:
                    record._create_font_attachment()
        return res

    def _create_font_attachment(self):
        """Create or update attachment for font file"""
        self.ensure_one()
        if not self.font_file:
            return
        
        # Find existing attachment
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'custom.font.file'),
            ('res_id', '=', self.id),
        ], limit=1)
        
        filename = self.font_filename or f"{self.font_family_name}.ttf"
        
        if attachment:
            # Update existing attachment
            attachment.write({
                'name': filename,
                'datas': self.font_file,
                'public': True,
                'access_token': False,  # Remove access token for public access
            })
        else:
            # Create new attachment
            self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': self.font_file,
                'res_model': 'custom.font.file',
                'res_id': self.id,
                'public': True,  # Make it accessible for reports
                'access_token': False,  # No access token needed for public files
            })

    def get_font_url(self, for_pdf=False):
        """Get the URL to access the font file"""
        self.ensure_one()
        if not self.font_file:
            return False
        
        # Ensure attachment exists
        self._create_font_attachment()
        
        # Get attachment
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'custom.font.file'),
            ('res_id', '=', self.id),
        ], limit=1)
        
        if not attachment:
            return False
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        if for_pdf:
            # For PDF, use the standard attachment URL which wkhtmltopdf can access via cookies
            # Make sure attachment is public
            if not attachment.public:
                attachment.write({'public': True})
            return f"{base_url}/web/content/{attachment.id}/{attachment.name}"
        else:
            # For preview, use custom controller
            filename = self.font_filename or f"{self.font_family_name}.ttf"
            return f"{base_url}/web/content/font/{self.id}/{filename}"

    def get_font_data_uri(self):
        """Get the font file as a data URI (base64) for PDF embedding"""
        self.ensure_one()
        if not self.font_file:
            return False
        
        # Ensure attachment exists
        self._create_font_attachment()
        
        # Get attachment to access raw data
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'custom.font.file'),
            ('res_id', '=', self.id),
        ], limit=1)
        
        if not attachment:
            # Fallback: try to use font_file field directly
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Font {self.name} (ID: {self.id}): No attachment found, using font_file field directly")
            if self.font_file:
                try:
                    # font_file is base64 encoded string
                    raw_data = base64.b64decode(self.font_file)
                    font_data_b64 = base64.b64encode(raw_data).decode('ascii')
                    filename = self.font_filename or f"{self.font_family_name}.ttf"
                    if filename.endswith('.woff'):
                        mime_type = 'font/woff'
                    elif filename.endswith('.woff2'):
                        mime_type = 'font/woff2'
                    elif filename.endswith('.otf'):
                        mime_type = 'font/opentype'
                    elif filename.endswith('.eot'):
                        mime_type = 'application/vnd.ms-fontobject'
                    else:
                        mime_type = 'application/font-sfnt'
                    return f"data:{mime_type};base64,{font_data_b64}"
                except Exception as e:
                    _logger.error(f"Error creating font data URI from font_file field: {e}")
            return False
        
        # Determine MIME type based on file extension
        filename = self.font_filename or f"{self.font_family_name}.ttf"
        if filename.endswith('.woff'):
            mime_type = 'font/woff'
        elif filename.endswith('.woff2'):
            mime_type = 'font/woff2'
        elif filename.endswith('.otf'):
            mime_type = 'font/opentype'
        elif filename.endswith('.eot'):
            mime_type = 'application/vnd.ms-fontobject'
        else:
            mime_type = 'application/font-sfnt'  # Standard MIME type for TTF
        
        # Get raw font data from attachment and encode to base64
        try:
            # Get raw bytes from attachment
            raw_data = attachment.raw
            if not raw_data:
                # Fallback to datas field (base64) and decode it
                if attachment.datas:
                    raw_data = base64.b64decode(attachment.datas)
                else:
                    return False
            
            # Ensure we have bytes
            if isinstance(raw_data, str):
                # If it's a string, try to decode it as base64 first
                try:
                    raw_data = base64.b64decode(raw_data)
                except Exception:
                    # If that fails, encode the string to bytes
                    raw_data = raw_data.encode('latin-1')
            
            # Encode to base64 for data URI
            font_data_b64 = base64.b64encode(raw_data).decode('ascii')
            
            # Return data URI - format: data:mime/type;base64,<base64_data>
            return f"data:{mime_type};base64,{font_data_b64}"
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error creating font data URI: {e}")
            return False

