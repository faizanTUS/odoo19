# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re

_logger = logging.getLogger(__name__)


class RingCentralCallHistory(models.Model):
    _name = 'ringcentral.call.history'
    _description = 'RingCentral Call History'
    _order = 'start_time desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Call ID', compute='_compute_name', store=True)
    config_id = fields.Many2one('ringcentral.config', string='Configuration', required=True, ondelete='cascade')
    ringcentral_call_id = fields.Char(string='RingCentral Call ID', index=True)
    
    # User tracking
    user_id = fields.Many2one('res.users', string='User', help='User who made/received this call', ondelete='set null')
    
    # Call details
    direction = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string='Direction', required=True)
    from_number = fields.Char(string='From Number', required=True)
    to_number = fields.Char(string='To Number', required=True)
    
    # Partner linking
    from_partner_id = fields.Many2one('res.partner', string='From Contact', ondelete='set null')
    to_partner_id = fields.Many2one('res.partner', string='To Contact', ondelete='set null')
    
    # Call timing
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time')
    duration = fields.Integer(string='Duration (seconds)', default=0)
    duration_formatted = fields.Char(string='Duration', compute='_compute_duration_formatted')
    
    # Call status
    status = fields.Selection([
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('answered', 'Answered'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('busy', 'Busy'),
        ('no-answer', 'No Answer'),
        ('unknown', 'Unknown'),
    ], string='Status', default='initiated')
    
    # Recording and transcript
    recording_id = fields.Char(string='Recording ID')
    recording_url = fields.Char(string='Recording URL', compute='_compute_recording_url')
    recording_playback_url = fields.Html(string='Recording Player', compute='_compute_recording_playback_url', sanitize=False)
    has_recording = fields.Boolean(string='Has Recording', compute='_compute_has_recording')
    transcript = fields.Text(string='Transcript', help='Call transcript from RingCentral')
    transcript_available = fields.Boolean(string='Transcript Available', default=False)
    
    # Additional info
    cost = fields.Float(string='Cost', digits=(16, 2))
    notes = fields.Text(string='Notes')
    
    # Activity tracking
    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities', domain=[('res_model', '=', 'ringcentral.call.history')])
    
    # KPI grouping field for kanban
    kpi_type = fields.Char(string='KPI Type', compute='_compute_kpi_type', store=False)
    
    @api.depends('ringcentral_call_id', 'from_number', 'to_number', 'start_time')
    def _compute_name(self):
        for record in self:
            if record.ringcentral_call_id:
                record.name = record.ringcentral_call_id
            else:
                record.name = f"{record.direction or 'Call'} - {record.from_number or ''} to {record.to_number or ''}"

    @api.depends('duration')
    def _compute_duration_formatted(self):
        for record in self:
            if record.duration:
                hours = record.duration // 3600
                minutes = (record.duration % 3600) // 60
                seconds = record.duration % 60
                if hours > 0:
                    record.duration_formatted = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    record.duration_formatted = f"{minutes}m {seconds}s"
                else:
                    record.duration_formatted = f"{seconds}s"
            else:
                record.duration_formatted = "0s"

    @api.depends('recording_id', 'config_id')
    def _compute_recording_url(self):
        for record in self:
            if record.recording_id and record.config_id:
                record.recording_url = f"{record.config_id.server_url}/restapi/v1.0/account/~/recording/{record.recording_id}/content"
            else:
                record.recording_url = False

    @api.depends('recording_id', 'config_id')
    def _compute_recording_playback_url(self):
        """Compute HTML audio player with authenticated playback URL"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.recording_id and record.id:
                playback_url = f"{base_url}/ringcentral/recording/{record.id}"
                record.recording_playback_url = f'''
                    <audio controls style="width: 100%; max-width: 600px;">
                        <source src="{playback_url}" type="audio/mpeg">
                        <source src="{playback_url}" type="audio/wav">
                        Your browser does not support the audio element.
                    </audio>
                '''
            else:
                record.recording_playback_url = False

    @api.depends('recording_id')
    def _compute_has_recording(self):
        for record in self:
            record.has_recording = bool(record.recording_id)
    
    def _compute_kpi_type(self):
        """Compute KPI type for kanban grouping - not used for actual records"""
        for record in self:
            record.kpi_type = 'kpi'

    @api.model
    def create(self, vals):
        """Auto-link partner based on phone number"""
        record = super().create(vals)
        record._auto_link_partner()
        return record

    def write(self, vals):
        """Auto-link partner when phone numbers change"""
        result = super().write(vals)
        if 'from_number' in vals or 'to_number' in vals:
            self._auto_link_partner()
        return result

    def _auto_link_partner(self):
        """Automatically link partner based on phone number"""
        self = self.sudo()
        partner_model = self.env['res.partner'].sudo()
        has_mobile = 'mobile' in partner_model._fields
        has_phone_sanitized = 'phone_sanitized' in partner_model._fields
        
        for record in self:
            from_partner = False
            to_partner = False
            
            # Find partner for from_number
            if record.from_number:
                from_partner = record._find_partner_for_number(
                    record.from_number, partner_model, has_mobile, has_phone_sanitized
                )
                if from_partner:
                    pass  # Partner matched
                else:
                    pass  # No partner found
            
            # Find partner for to_number
            if record.to_number:
                to_partner = record._find_partner_for_number(
                    record.to_number, partner_model, has_mobile, has_phone_sanitized
                )
                if to_partner:
                    pass  # Partner matched
                else:
                    pass  # No partner found
            
            # Write both partners at once
            write_vals = {}
            if from_partner:
                write_vals['from_partner_id'] = from_partner.id
            elif record.from_partner_id:
                write_vals['from_partner_id'] = False
                
            if to_partner:
                write_vals['to_partner_id'] = to_partner.id
            elif record.to_partner_id:
                write_vals['to_partner_id'] = False
            
            if write_vals:
                record.write(write_vals)

    def _clean_phone_number(self, phone):
        """Clean phone number for matching - remove all non-digit characters"""
        if not phone:
            return ''
        # Remove all non-digit characters
        return re.sub(r'\D', '', phone)

    def _normalize_phone_number(self, phone):
        """Normalize phone number using partner utilities when available"""
        if not phone:
            return ''

        partner_model = self.env['res.partner']
        
        # Try Odoo's built-in phone normalization if available
        normalize = getattr(partner_model, '_phone_normalize', None)
        if callable(normalize):
            try:
                normalized = normalize(phone)
                if normalized:
                    # Remove + and return digits only
                    return re.sub(r'\D', '', normalized)
            except Exception:
                pass

        # Fallback: extract digits only
        return re.sub(r'\D', '', phone)

    def _get_all_phone_variants(self, number):
        """Generate all possible variants of a phone number for matching"""
        if not number:
            return []
        
        variants = set()
        
        # Original number
        variants.add(number)
        
        # Digits only
        digits_only = re.sub(r'\D', '', number)
        if digits_only:
            variants.add(digits_only)
            variants.add(f"+{digits_only}")
        
        # Without leading + or country code (last 10 digits for US numbers)
        if len(digits_only) > 10:
            # Try last 10 digits (US format)
            variants.add(digits_only[-10:])
            # Try last 11 digits
            if len(digits_only) > 11:
                variants.add(digits_only[-11:])
        
        # Normalized version
        normalized = self._normalize_phone_number(number)
        if normalized:
            variants.add(normalized)
            # Last 10 digits of normalized
            if len(normalized) > 10:
                variants.add(normalized[-10:])
        
        return list(variants)

    def _normalize_for_comparison(self, phone):
        """Normalize phone number to digits only for comparison"""
        if not phone:
            return ''
        # Remove all non-digit characters
        return re.sub(r'\D', '', str(phone))

    def _find_partner_for_number(self, number, partner_model, has_mobile, has_phone_sanitized):
        """Find partner matching a given phone number - tries multiple matching strategies"""
        if not number:
            return False

        # Normalize the input number to digits only
        input_digits = self._normalize_for_comparison(number)
        if not input_digits or len(input_digits) < 7:
            return False

        # Get all phone number variants to try
        variants = self._get_all_phone_variants(number)
        
        # Strategy 1: Try exact matches on all variants
        for variant in variants:
            if not variant:
                continue
            
            variant_digits = self._normalize_for_comparison(variant)
            if not variant_digits:
                continue
                
            # Try phone_sanitized field if available (exact match)
            if has_phone_sanitized:
                partner = partner_model.search([
                    ('phone_sanitized', '=', variant)
                ], order='write_date desc, create_date desc', limit=1)
                if partner:
                    return partner
            
            # Try exact match on phone field
            partner = partner_model.search([
                ('phone', '=', variant)
            ], order='write_date desc, create_date desc', limit=1)
            if partner:
                return partner
            
            # Try exact match on mobile field
            if has_mobile:
                partner = partner_model.search([
                    ('mobile', '=', variant)
                ], order='write_date desc, create_date desc', limit=1)
                if partner:
                    return partner
        
        # Strategy 2: Normalize and compare digits-only versions
        # Use ilike to filter potential matches first, then normalize and compare
        # This is more efficient than checking all partners
        search_number = input_digits[-10:] if len(input_digits) >= 10 else input_digits
        
        # Find partners whose phone/mobile contains our search digits
        # Limit to 20 partners max to avoid performance issues
        domain = [('phone', 'ilike', search_number)]
        if has_mobile:
            domain = ['|'] + domain + [('mobile', 'ilike', search_number)]
        # Order by write_date desc, create_date desc to get the latest one first
        potential_partners = partner_model.search(domain, order='write_date desc, create_date desc', limit=20)  # Reduced limit for performance
        
        # Only check first few matches to avoid timeout
        for partner in potential_partners[:10]:  # Check only first 10
            # Normalize partner's phone
            partner_phone_digits = self._normalize_for_comparison(partner.phone) if partner.phone else ''
            partner_mobile_digits = self._normalize_for_comparison(partner.mobile) if (has_mobile and partner.mobile) else ''
            
            # Try full match
            if partner_phone_digits == input_digits or partner_mobile_digits == input_digits:
                return partner
            
            # Try last 10 digits match (US format - area code + number)
            if len(input_digits) >= 10:
                input_last10 = input_digits[-10:]
                if partner_phone_digits and len(partner_phone_digits) >= 10:
                    if partner_phone_digits[-10:] == input_last10:
                        return partner
                if partner_mobile_digits and len(partner_mobile_digits) >= 10:
                    if partner_mobile_digits[-10:] == input_last10:
                        return partner
        
        # Strategy 3: Fallback to ilike search (contains)
        search_number = input_digits[-10:] if len(input_digits) >= 10 else input_digits
        
        domain = [('phone', 'ilike', search_number)]
        if has_mobile:
            domain = ['|'] + domain + [('mobile', 'ilike', search_number)]
        
        partner = partner_model.search(domain, order='write_date desc, create_date desc', limit=1)
        if partner:
            return partner

        return False

    def action_backfill_partner_links(self):
        """Re-run partner linking logic for existing records - processes in small batches to avoid timeout"""
        calls = self
        if not calls:
            calls = self.sudo().search([])
        else:
            calls = calls.sudo()
        
        if not calls:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('No call records to process'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        # Process in very small batches to avoid timeout (Odoo thread limit is 120s)
        batch_size = 20  # Small batches to avoid timeout
        total_calls = len(calls)
        total_processed = 0
        matched_count = 0
        
        # Process only first few batches to avoid timeout
        max_batches = 5  # Process max 5 batches (100 records) per request
        batches_to_process = min(max_batches, (total_calls + batch_size - 1) // batch_size)
        
        for i in range(batches_to_process):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, total_calls)
            batch = calls[start_idx:end_idx]
            
            if batch:
                batch._auto_link_partner()
                total_processed += len(batch)
                
                # Count how many got matched
                matched = batch.filtered(lambda r: r.from_partner_id or r.to_partner_id)
                matched_count += len(matched)
        
        # If there are more records, inform user to run again
        remaining = total_calls - total_processed
        if remaining > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Backfill In Progress'),
                    'message': _('Processed %d of %d records. Matched %d contacts. Please run the action again to process remaining %d records.') % (total_processed, total_calls, matched_count, remaining),
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        # All processed
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Backfill Complete'),
                'message': _('Processed %d call record(s). Matched contacts for %d record(s).') % (total_processed, matched_count),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_fetch_transcript(self):
        """Fetch transcript from RingCentral"""
        self.ensure_one()
        
        if not self.recording_id:
            raise UserError(_('No recording available for this call.'))
        
        try:
            # This would need to be implemented based on RingCentral API for transcripts
            # For now, we'll mark it as a placeholder
            config = self.config_id
            # TODO: Implement actual transcript fetching from RingCentral API
            # transcript = config._get_call_transcript(self.recording_id)
            
            self.write({
                'transcript_available': True,
                'transcript': 'Transcript fetching not yet implemented. Please check RingCentral dashboard.',
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('Transcript fetching is in progress. Please check back later.'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error(f"Error fetching transcript: {str(e)}")
            raise UserError(_('Failed to fetch transcript: %s') % str(e))

    def action_download_recording(self):
        """Download call recording"""
        self.ensure_one()
        
        if not self.recording_id:
            raise UserError(_('No recording available for this call.'))
        
        config = self.config_id
        try:
            recording_data = config.get_call_recording(self.recording_id)
            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': self.recording_url,
                'target': 'new',
            }
        except Exception as e:
            _logger.error(f"Error downloading recording: {str(e)}")
            raise UserError(_('Failed to download recording: %s') % str(e))

