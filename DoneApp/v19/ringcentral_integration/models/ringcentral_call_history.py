# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re

try:
    from psycopg2 import IntegrityError as Psycopg2IntegrityError
except ImportError:
    Psycopg2IntegrityError = None

from odoo.addons.ringcentral_integration.utils import phone as phone_utils
from odoo.addons.ringcentral_integration.utils import presence_webhook as pw_utils
from odoo.addons.ringcentral_integration.utils import telephony_session_webhook as tsw_utils

_logger = logging.getLogger(__name__)

_STATUS_RANK = {
    'unknown': -1,
    'initiated': 0,
    'ringing': 1,
    'failed': 2,
    'busy': 2,
    'no-answer': 2,
    'answered': 3,
    'completed': 4,
}

class RingCentralCallHistory(models.Model):
    _name = 'ringcentral.call.history'
    _description = 'RingCentral Call History'
    _order = 'start_time desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Call ID', compute='_compute_name', store=True)
    config_id = fields.Many2one('ringcentral.config', string='Configuration', required=True, ondelete='cascade')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        index=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    ringcentral_call_id = fields.Char(
        string='RingCentral Session ID',
        index=True,
        help='RingCentral sessionId — unique identifier for the call across all legs.',
    )
    ringcentral_telephony_session_id = fields.Char(
        string='RingCentral Telephony Session ID',
        index=True,
        help='RingCentral telephonySessionId (s-...) alias for the same call.',
    )
    ringcentral_call_log_id = fields.Char(
        string='RingCentral Call Log ID',
        index=True,
        help='RingCentral call-log API record id (distinct from sessionId).',
    )
    
    # User tracking
    initiated_by_id = fields.Many2one(
        'res.users',
        string='Initiated By',
        help='Odoo user who placed an outbound call',
        ondelete='set null',
        index=True,
    )
    answered_by_id = fields.Many2one(
        'res.users',
        string='Answered By',
        help='Odoo user who answered the call',
        ondelete='set null',
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Agent',
        compute='_compute_user_id',
        inverse='_inverse_user_id',
        store=True,
        readonly=False,
        help='Primary agent for filtering: answerer if set, otherwise initiator.',
    )
    
    # Call details
    direction = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string='Direction', required=True)
    from_number = fields.Char(string='From Number', required=True)
    to_number = fields.Char(string='To Number', required=True)
    caller_name = fields.Char(
        string='Caller Name',
        help='Caller ID name from RingCentral when available.',
    )
    
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

    call_result = fields.Selection([
        ('answered', 'Answered'),
        ('missed', 'Missed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
        ('transferred', 'Transferred'),
    ], string='Call Result', index=True)
    
    # Recording and transcript
    recording_id = fields.Char(string='Recording ID')
    recording_url = fields.Char(string='Recording URL', compute='_compute_recording_url')
    recording_playback_url = fields.Html(string='Recording Player', compute='_compute_recording_playback_url', sanitize=False)
    has_recording = fields.Boolean(string='Has Recording', compute='_compute_has_recording')
    transcript = fields.Text(string='Transcript', help='Call transcript from RingCentral')
    transcript_available = fields.Boolean(string='Transcript Available', default=False)
    transcript_source = fields.Selection([
        ('ringsense', 'RingSense'),
        ('speech_to_text', 'Speech-to-Text'),
    ], string='Transcript Source', help='Method used to generate the transcript')
    transcript_job_id = fields.Char(string='Transcript Job ID', help='Speech-to-text job ID when transcription is in progress')
    
    # Additional info
    cost = fields.Float(string='Cost', digits=(16, 2))
    notes = fields.Text(string='Notes')

    # Webhook debugging
    webhook_payloads = fields.Json(
        string='Webhook Payloads',
        default=list,
        help='Complete RingCentral presence webhook payloads received for this call.',
    )
    termination_type = fields.Char(string='Termination Type')
    last_webhook_sequence = fields.Integer(string='Last Webhook Sequence')
    
    # Activity tracking
    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities', domain=[('res_model', '=', 'ringcentral.call.history')])
    
    # KPI grouping field for kanban
    kpi_type = fields.Char(string='KPI Type', compute='_compute_kpi_type', store=False)

    _config_session_uniq = models.Constraint(
        'unique(config_id, ringcentral_call_id)',
        'A call history record already exists for this RingCentral session.',
    )
    _config_telephony_session_uniq = models.Constraint(
        'unique(config_id, ringcentral_telephony_session_id)',
        'A call history record already exists for this RingCentral telephony session.',
    )

    @api.depends('initiated_by_id', 'answered_by_id')
    def _compute_user_id(self):
        for record in self:
            record.user_id = record.answered_by_id or record.initiated_by_id

    def _inverse_user_id(self):
        for record in self:
            if not record.user_id:
                continue
            if record.direction == 'outbound' and not record.initiated_by_id:
                record.initiated_by_id = record.user_id
            elif record.direction == 'inbound' and not record.answered_by_id:
                record.answered_by_id = record.user_id
            elif not record.initiated_by_id and not record.answered_by_id:
                record.initiated_by_id = record.user_id

    @api.model
    def _find_user_by_extension(self, extension_number=None, extension_id=None):
        """Map a RingCentral extension number or ID to an Odoo user."""
        Users = self.env['res.users'].sudo()
        if extension_id:
            ext_id = str(extension_id).strip()
            if ext_id:
                user = Users.search([('ringcentral_extension_id', '=', ext_id)], limit=1)
                if user:
                    return user
                user = Users.search([('ringcentral_extension', '=', ext_id)], limit=1)
                if user:
                    return user
        if extension_number:
            ext = str(extension_number).strip()
            if not ext:
                return Users.browse()
            user = Users.search([('ringcentral_extension', '=', ext)], limit=1)
            if user:
                return user
            digits = re.sub(r'\D', '', ext)
            if digits and digits != ext:
                user = Users.search([('ringcentral_extension', '=', digits)], limit=1)
                if user:
                    return user
        return Users.browse()

    def _user_vals_from_presence(self, body, leg, payload=None):
        """Derive initiated/answered user from a presence or telephony webhook leg."""
        if not leg and not body:
            return {}
        known_extensions = self.env['res.users'].sudo().search([
            ('ringcentral_extension', '!=', False),
        ]).mapped('ringcentral_extension')
        direction = (leg or {}).get('direction') or ''
        telephony_status = (
            (leg or {}).get('telephonyStatus')
            or (body or {}).get('telephonyStatus')
            or (body or {}).get('aggregatedTelephonyStatus')
        )
        extension_id = (
            (payload or {}).get('ownerId')
            or (body or {}).get('extensionId')
            or (leg or {}).get('extensionId')
        )
        user = self.env['res.users'].browse()
        if direction == 'Outbound':
            user = self._find_user_by_extension(extension_id=extension_id)
            if not user:
                from_info = (leg or {}).get('from')
                if isinstance(from_info, dict):
                    user = self._find_user_by_extension(
                        extension_number=from_info.get('extensionNumber'),
                    )
            if not user:
                from_number = pw_utils.extract_phone((leg or {}).get('from'))
                if from_number in known_extensions:
                    user = self._find_user_by_extension(extension_number=from_number)
        elif direction == 'Inbound':
            user = self._find_user_by_extension(extension_id=extension_id)
            if not user and telephony_status in ('CallConnected', 'OnHold'):
                to_info = (leg or {}).get('to')
                if isinstance(to_info, dict):
                    user = self._find_user_by_extension(
                        extension_number=to_info.get('extensionNumber'),
                    )
            is_internal = pw_utils.is_internal_agent_leg(leg, known_extensions) if leg else False
            if not user and is_internal:
                user = self._find_user_by_extension(
                    extension_number=pw_utils.extract_phone((leg or {}).get('from')),
                )
        else:
            user = self._find_user_by_extension(extension_id=extension_id)

        if not user:
            return {}

        vals = {}
        if telephony_status in ('CallConnected', 'OnHold'):
            vals['answered_by_id'] = user.id
        if direction == 'Outbound' and telephony_status in ('Ringing', 'CallConnected', 'unknown'):
            vals['initiated_by_id'] = user.id
        elif direction == 'Inbound' and telephony_status in ('Ringing',):
            pass
        elif not direction and telephony_status in ('Ringing', 'CallConnected'):
            vals['initiated_by_id'] = user.id
        return vals

    @api.model
    def _session_vals_from_raw_session_id(self, session_id):
        """Map a widget/API session id string to stored session fields."""
        if not session_id:
            return {}
        session_str = str(session_id).strip()
        if session_str.startswith('s-'):
            return {
                'ringcentral_telephony_session_id': session_str,
                'ringcentral_call_id': session_str,
            }
        return {'ringcentral_call_id': session_str}

    @api.model
    def _canonical_record_score(self, record):
        """Higher score = better canonical row for session deduplication."""
        score = 0
        if record.ringcentral_call_id and record.ringcentral_telephony_session_id:
            score += 100
        elif record.ringcentral_call_id or record.ringcentral_telephony_session_id:
            score += 50
        if record.answered_by_id:
            score += 20
        if record.initiated_by_id:
            score += 10
        if record.from_partner_id or record.to_partner_id:
            score += 15
        score += _STATUS_RANK.get(record.status, -1)
        return score

    @api.model
    def _merge_fill_only_missing_vals(self, target, source_vals):
        """Build write vals from source without overwriting populated target fields."""
        skip_keys = {'id', 'config_id', 'create_date', 'create_uid'}
        partner_keys = {'from_partner_id', 'to_partner_id'}
        user_keys = {'initiated_by_id', 'answered_by_id', 'user_id'}
        merged = {}
        for key, value in source_vals.items():
            if key in skip_keys or value in (False, None, '', []):
                continue
            current = target[key] if key in target._fields else False
            if key in partner_keys or key in user_keys:
                if current:
                    continue
            elif current not in (False, None, ''):
                if key == 'status':
                    current_rank = _STATUS_RANK.get(current, -1)
                    new_rank = _STATUS_RANK.get(value, -1)
                    if new_rank < current_rank:
                        continue
                elif key not in ('webhook_payloads', 'last_webhook_sequence'):
                    continue
            merged[key] = value
        return merged

    @api.model
    def _merge_presence_vals_into_record(self, record, create_vals):
        """Merge webhook/widget create vals into an existing call history row."""
        merge_vals = dict(create_vals)
        merge_vals.pop('config_id', None)
        payload_log = merge_vals.pop('webhook_payloads', None)
        filled = self._merge_fill_only_missing_vals(record, merge_vals)
        if payload_log:
            existing_log = list(record.webhook_payloads or [])
            if isinstance(payload_log, list):
                filled['webhook_payloads'] = existing_log + payload_log
            else:
                filled['webhook_payloads'] = existing_log + [payload_log]
        if filled:
            record.with_context(rc_allow_direction_update=True).write(filled)
        record._link_contact_for_call()
        record._maybe_enrich_recording()
        return record

    @api.model
    def _merge_duplicate_session_records(self, config, matches):
        """Merge duplicate call history rows for the same RingCentral session."""
        matches = matches.sudo().exists()
        if len(matches) <= 1:
            return matches[:1]

        ordered = sorted(
            matches,
            key=lambda record: (
                -self._canonical_record_score(record),
                record.create_date or fields.Datetime.now(),
                record.id,
            ),
        )
        canonical = ordered[0]
        duplicates = self.browse([record.id for record in ordered[1:]])

        for duplicate in duplicates:
            source_vals = {}
            for key in (
                'ringcentral_call_id', 'ringcentral_telephony_session_id', 'ringcentral_call_log_id',
                'direction', 'from_number', 'to_number', 'caller_name', 'status', 'call_result',
                'start_time', 'end_time', 'duration', 'initiated_by_id', 'answered_by_id',
                'from_partner_id', 'to_partner_id', 'recording_id', 'company_id',
                'last_webhook_sequence', 'termination_type',
            ):
                if key in duplicate._fields:
                    source_vals[key] = duplicate[key]
            if duplicate.webhook_payloads:
                source_vals['webhook_payloads'] = list(duplicate.webhook_payloads)
            merge_vals = self._merge_fill_only_missing_vals(canonical, source_vals)
            if merge_vals:
                canonical.with_context(rc_allow_direction_update=True).write(merge_vals)
            duplicate.unlink()

        _logger.warning(
            'RC session dedup: merged %d duplicate rows into call history %s (config=%s)',
            len(duplicates), canonical.id, config.id,
        )
        return canonical

    @api.model
    def _find_call_for_session(self, config, aliases):
        """Find call history by any RingCentral session alias (telephony id first)."""
        alias_list = [str(alias).strip() for alias in (aliases or []) if alias]
        if not alias_list:
            return self.browse()
        matches = self.sudo().search([
            ('config_id', '=', config.id),
            '|',
            ('ringcentral_telephony_session_id', 'in', alias_list),
            ('ringcentral_call_id', 'in', alias_list),
        ], order='write_date desc')
        if len(matches) > 1:
            return self._merge_duplicate_session_records(config, matches)
        return matches[:1]

    @api.model
    def _find_pending_inbound_merge(self, config, from_number, session_id):
        """Find a recent pre-created inbound record to merge with this session."""
        if not from_number or from_number == 'unknown':
            return self.browse()
        cutoff = fields.Datetime.now() - timedelta(minutes=10)
        domain = [
            ('config_id', '=', config.id),
            ('direction', '=', 'inbound'),
            ('status', 'in', ['initiated', 'ringing', 'answered']),
            ('start_time', '>=', cutoff),
        ]
        domain.append(('ringcentral_call_id', '=', False))
        domain.append(('ringcentral_telephony_session_id', '=', False))
        candidates = self.sudo().search(domain, order='start_time desc')
        for candidate in candidates:
            if phone_utils.phones_match(from_number, candidate.from_number, self.env):
                return candidate
        return self.browse()

    @api.model
    def _is_bootstrap_session_record(self, record):
        """True when the call history row has no RingCentral session identifiers yet."""
        return not record.ringcentral_call_id and not record.ringcentral_telephony_session_id

    @api.model
    def _find_existing_call(
        self, config, session_aliases=None, direction=None,
        external_number=None, from_number=None, to_number=None,
        start_time=None, session_id=None, time_window_minutes=3,
        allow_phone_window=False,
    ):
        """Unified lookup for upsert paths: session, pending bootstrap, optional time window."""
        if session_aliases:
            match = self._find_call_for_session(config, session_aliases)
            if match:
                return match
        if session_id:
            match = self._find_call_for_session(config, [session_id])
            if match:
                return match

        if direction == 'inbound' and external_number:
            pending = self._find_pending_inbound_merge(config, external_number, session_id)
            if pending:
                return pending
        if direction == 'outbound' and external_number:
            pending = self._find_pending_outbound_merge(config, external_number, session_id)
            if pending:
                return pending

        if allow_phone_window and external_number and start_time:
            window_start = start_time - timedelta(minutes=time_window_minutes)
            window_end = start_time + timedelta(minutes=time_window_minutes)
            recent = self.sudo().search([
                ('config_id', '=', config.id),
                ('start_time', '>=', window_start),
                ('start_time', '<=', window_end),
            ], order='start_time desc', limit=30)
            for candidate in recent:
                if (
                    phone_utils.phones_match(external_number, candidate.from_number, self.env)
                    or phone_utils.phones_match(external_number, candidate.to_number, self.env)
                ):
                    return candidate

        if not allow_phone_window:
            return self.browse()

        if external_number and start_time:
            window_start = start_time - timedelta(minutes=time_window_minutes)
            window_end = start_time + timedelta(minutes=time_window_minutes)
            recent = self.sudo().search([
                ('config_id', '=', config.id),
                ('start_time', '>=', window_start),
                ('start_time', '<=', window_end),
                ('ringcentral_call_id', '=', False),
                ('ringcentral_telephony_session_id', '=', False),
            ], order='start_time desc', limit=30)
            for candidate in recent:
                if not self._is_bootstrap_session_record(candidate):
                    continue
                if (
                    phone_utils.phones_match(external_number, candidate.from_number, self.env)
                    or phone_utils.phones_match(external_number, candidate.to_number, self.env)
                ):
                    return candidate

        if from_number and to_number and start_time and from_number != 'unknown':
            window_start = start_time - timedelta(minutes=time_window_minutes)
            window_end = start_time + timedelta(minutes=time_window_minutes)
            candidates = self.sudo().search([
                ('config_id', '=', config.id),
                ('start_time', '>=', window_start),
                ('start_time', '<=', window_end),
                ('ringcentral_call_id', '=', False),
                ('ringcentral_telephony_session_id', '=', False),
            ], order='start_time desc', limit=20)
            for candidate in candidates:
                if not self._is_bootstrap_session_record(candidate):
                    continue
                to_match = phone_utils.phones_match(to_number, candidate.to_number, self.env)
                from_match = (
                    phone_utils.phones_match(from_number, candidate.from_number, self.env)
                    if from_number != 'unknown'
                    else candidate.from_number in (False, 'unknown')
                )
                if to_match and from_match:
                    return candidate
                if (
                    direction == 'outbound'
                    and to_match
                    and candidate.direction == 'outbound'
                    and candidate.from_number in (False, 'unknown')
                ):
                    return candidate
        return self.browse()

    @api.model
    def process_telephony_session_webhook(self, config, payload):
        """Process account/extension telephony session webhook events."""
        normalized = tsw_utils.normalize_telephony_session_payload(payload)
        if not normalized:
            _logger.debug(
                'RC telephony session webhook: no parties uuid=%s',
                payload.get('uuid'),
            )
            return
        _logger.info(
            'RC telephony session webhook: session=%s uuid=%s parties=%d',
            (normalized.get('body') or {}).get('sessionId'),
            payload.get('uuid'),
            len((normalized.get('body') or {}).get('activeCalls') or []),
        )
        self.process_presence_webhook(config, normalized)

    @api.model
    def _upsert_inbound_call_event(self, config, session_id, phone_number, vals, user=None):
        """Find or create inbound call history for widget CTI events."""
        user = user or self.env.user
        existing = self._find_inbound_call_for_session(config, session_id, phone_number)
        if existing:
            write_vals = dict(vals)
            if user and not existing.answered_by_id:
                write_vals.setdefault('answered_by_id', user.id)
            if existing.caller_name and 'caller_name' in write_vals:
                write_vals.pop('caller_name')
            existing.write(write_vals)
            existing._link_contact_for_call()
            return existing

        from_number = phone_number or 'unknown'
        if not session_id and from_number == 'unknown':
            return self.browse()

        start_time = fields.Datetime.now()
        existing = self._find_existing_call(
            config,
            session_aliases=[str(session_id)] if session_id else None,
            direction='inbound',
            external_number=from_number if from_number != 'unknown' else None,
            from_number=from_number,
            to_number='unknown',
            start_time=start_time,
            session_id=session_id,
            time_window_minutes=10,
            allow_phone_window=True,
        )
        if existing:
            write_vals = dict(vals)
            if user and not existing.answered_by_id:
                write_vals.setdefault('answered_by_id', user.id)
            if existing.caller_name and 'caller_name' in write_vals:
                write_vals.pop('caller_name')
            if session_id:
                write_vals.update(self._session_vals_from_raw_session_id(session_id))
            self._merge_presence_vals_into_record(existing, {
                'direction': 'inbound',
                'from_number': from_number,
                'start_time': start_time,
                'answered_by_id': user.id,
                **write_vals,
            })
            return existing

        create_vals = {
            'config_id': config.id,
            'company_id': self._resolve_company_id({'answered_by_id': user.id}, config=config),
            'direction': 'inbound',
            'from_number': from_number,
            'to_number': 'unknown',
            'start_time': fields.Datetime.now(),
            'answered_by_id': user.id,
            **vals,
        }
        if session_id:
            create_vals.update(self._session_vals_from_raw_session_id(session_id))
            session_info = {
                'primary_key': str(session_id),
                'canonical_id': str(session_id),
                'telephony_session_id': str(session_id) if str(session_id).startswith('s-') else None,
                'numeric_session_id': None if str(session_id).startswith('s-') else str(session_id),
                'aliases': [str(session_id)],
            }
            return self._create_presence_call_history(config, create_vals, session_info)

        record = self.with_context(rc_allow_direction_update=True).create(create_vals)
        record._link_contact_for_call()
        return record

    @api.model
    def _upsert_outbound_call_event(self, config, session_id, phone_number, vals, user=None):
        """Find or create outbound call history for widget/API dial events."""
        user = user or self.env.user
        to_number = phone_number or 'unknown'

        if session_id:
            existing = self._find_call_for_session(config, [session_id])
            if existing:
                write_vals = dict(vals)
                if user and not existing.initiated_by_id:
                    write_vals.setdefault('initiated_by_id', user.id)
                existing.with_context(rc_allow_direction_update=True).write({
                    **write_vals,
                    **self._session_vals_from_raw_session_id(session_id),
                })
                existing._link_contact_for_call()
                return existing

        pending = self._find_pending_outbound_merge(config, to_number, session_id or False)
        if pending:
            write_vals = dict(vals)
            if user and not pending.initiated_by_id:
                write_vals.setdefault('initiated_by_id', user.id)
            if session_id:
                write_vals.update(self._session_vals_from_raw_session_id(session_id))
            pending.with_context(rc_allow_direction_update=True).write(write_vals)
            pending._link_contact_for_call()
            return pending

        if to_number == 'unknown':
            return self.browse()

        start_time = fields.Datetime.now()
        existing = self._find_existing_call(
            config,
            session_aliases=[str(session_id)] if session_id else None,
            direction='outbound',
            external_number=to_number if to_number != 'unknown' else None,
            from_number='unknown',
            to_number=to_number,
            start_time=start_time,
            session_id=session_id,
            time_window_minutes=10,
            allow_phone_window=True,
        )
        if existing:
            write_vals = dict(vals)
            if user and not existing.initiated_by_id:
                write_vals.setdefault('initiated_by_id', user.id)
            if session_id:
                write_vals.update(self._session_vals_from_raw_session_id(session_id))
            self._merge_presence_vals_into_record(existing, {
                'direction': 'outbound',
                'to_number': to_number,
                'start_time': start_time,
                'initiated_by_id': user.id,
                **write_vals,
            })
            return existing

        create_vals = {
            'config_id': config.id,
            'company_id': self._resolve_company_id({'initiated_by_id': user.id}, config=config),
            'initiated_by_id': user.id,
            'direction': 'outbound',
            'from_number': 'unknown',
            'to_number': to_number,
            'start_time': fields.Datetime.now(),
            'status': 'initiated',
            **vals,
        }
        if session_id:
            create_vals.update(self._session_vals_from_raw_session_id(session_id))
            session_info = {
                'primary_key': str(session_id),
                'canonical_id': str(session_id),
                'telephony_session_id': str(session_id) if str(session_id).startswith('s-') else None,
                'numeric_session_id': None if str(session_id).startswith('s-') else str(session_id),
                'aliases': [str(session_id)],
            }
            return self._create_presence_call_history(config, create_vals, session_info)

        record = self.with_context(rc_allow_direction_update=True).create(create_vals)
        record._link_contact_for_call()
        return record

    @api.model
    def process_call_event(self, event, phone_number=None, session_id=None, direction='outbound', caller_name=None):
        """Handle frontend call lifecycle events (outbound start / inbound CTI from widget)."""
        config = self.env['ringcentral.config'].sudo()._get_company_active_config(self.env.company)
        if not config:
            return False

        user = self.env.user

        if event == 'inbound_ring':
            create_vals = {'status': 'ringing'}
            if caller_name:
                create_vals['caller_name'] = caller_name
            record = self._upsert_inbound_call_event(
                config, session_id, phone_number, create_vals, user=user,
            )
            return record.id if record else False

        if event == 'inbound_answered':
            record = self._upsert_inbound_call_event(
                config, session_id, phone_number, {
                    'status': 'answered',
                    'call_result': 'answered',
                }, user=user,
            )
            return record.id if record else False

        if event == 'inbound_rejected':
            record = self._upsert_inbound_call_event(
                config, session_id, phone_number, {
                    'status': 'no-answer',
                    'call_result': 'rejected',
                    'end_time': fields.Datetime.now(),
                }, user=user,
            )
            return record.id if record else False

        if event == 'outbound_start':
            record = self._upsert_outbound_call_event(
                config, session_id, phone_number, {'status': 'initiated'}, user=user,
            )
            return record.id if record else False

        if event == 'call_end' and session_id:
            call_history = self._find_call_for_session(config, [session_id])
            if call_history and call_history.status in ('initiated', 'ringing', 'answered'):
                return call_history.id
        return False

    @api.model
    def _find_inbound_call_for_session(self, config, session_id, phone_number=None):
        """Find a ringing/answered inbound call record for widget CTI events."""
        CallHistory = self.sudo()
        if session_id:
            match = self._find_call_for_session(config, [session_id])
            if match:
                return match

        if not phone_number:
            return CallHistory.browse()

        pending = self._find_pending_inbound_merge(config, phone_number, session_id)
        if pending:
            return pending

        return CallHistory.browse()

    @api.model
    def link_contact_from_phone(self, phone_number, session_id=None):
        """Ensure inbound call history is linked to a contact for the caller number."""
        if not phone_number:
            return self.browse()
        config = self.env['ringcentral.config'].sudo()._get_company_active_config(self.env.company)
        if not config:
            return self.browse()
        call = self._find_inbound_call_for_session(config, session_id, phone_number)
        if call:
            call._link_contact_for_call()
        return call

    @api.model
    def find_partner_for_phone(self, phone_number):
        """Public helper: find a contact matching a phone number."""
        if not phone_number:
            return self.env['res.partner'].browse()
        partner_model = self.env['res.partner'].sudo()
        has_mobile = 'mobile' in partner_model._fields
        has_phone_sanitized = 'phone_sanitized' in partner_model._fields
        partner = self._find_partner_for_number(
            phone_number, partner_model, has_mobile, has_phone_sanitized,
        )
        return partner or self.env['res.partner'].browse()

    @api.model
    def link_lead_to_call(self, lead_id, session_id=None, phone_number=None):
        """Link a CRM lead to the matching call history record."""
        if not lead_id:
            return self.browse()
        config = self.env['ringcentral.config'].sudo()._get_company_active_config(self.env.company)
        if not config:
            return self.browse()
        call = self._find_inbound_call_for_session(config, session_id, phone_number)
        if call and 'lead_id' in call._fields:
            call.write({'lead_id': lead_id})
        return call

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

    def _post_call_log_to_partners(self):
        """Post a chatter note on each linked partner (and their parents) when a call is linked."""
        for record in self:
            partners = set()
            if record.from_partner_id:
                partners.add(record.from_partner_id)
                if record.from_partner_id.parent_id:
                    partners.add(record.from_partner_id.parent_id)
            if record.to_partner_id:
                partners.add(record.to_partner_id)
                if record.to_partner_id.parent_id:
                    partners.add(record.to_partner_id.parent_id)
            if not partners:
                continue
            direction_label = dict(self._fields['direction'].selection).get(record.direction, record.direction)
            status_label = dict(self._fields['status'].selection).get(record.status, record.status)
            body = _(
                'Call: %s from %s to %s - %s - %s'
            ) % (direction_label, record.from_number, record.to_number, record.duration_formatted, status_label)
            for partner in partners:
                try:
                    partner.message_post(
                        body=body,
                        message_type='notification',
                        subtype_xmlid='ringcentral_integration.mt_call_log',
                    )
                except Exception as e:
                    _logger.warning('Could not post call log to partner %s: %s', partner.id, e)

    @api.model
    def _resolve_company_id(self, vals, config=None):
        """Resolve company for a call history record."""
        if vals.get('company_id'):
            return vals['company_id']
        for user_field in ('answered_by_id', 'initiated_by_id', 'user_id'):
            if vals.get(user_field):
                user = self.env['res.users'].browse(vals[user_field])
                if user.exists() and user.company_id:
                    return user.company_id.id
        if config is None and vals.get('config_id'):
            config = self.env['ringcentral.config'].browse(vals['config_id'])
        if config and config.exists():
            if config.company_ids:
                company = self.env.company
                if company in config.company_ids:
                    return company.id
                return config.company_ids[0].id
            if config.company_id:
                return config.company_id.id
        return self.env.company.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('company_id'):
                vals['company_id'] = self._resolve_company_id(vals)
        records = super().create(vals_list)
        for record in records:
            record._auto_link_partner()

        return records

    def write(self, vals):
        """Auto-link partner when phone numbers change; protect immutable call identity fields."""
        if not self.env.context.get('rc_allow_direction_update'):
            vals = {
                k: v for k, v in vals.items()
                if k not in ('direction', 'from_number', 'to_number')
            }
        result = super().write(vals)
        if 'from_number' in vals or 'to_number' in vals:
            self._auto_link_partner()
        if 'from_partner_id' in vals or 'to_partner_id' in vals:
            self._post_call_log_to_partners()
        return result

    def _append_webhook_payload(self, payload):
        """Append a webhook payload entry to the JSON log."""
        self.ensure_one()
        entry = {
            'uuid': payload.get('uuid'),
            'timestamp': payload.get('timestamp'),
            'event': payload.get('event'),
            'body': payload.get('body'),
        }
        existing = list(self.webhook_payloads or [])
        existing.append(entry)
        return existing

    def _build_presence_update_vals(self, payload, status_leg, call_history=None):
        """Build metadata update values from a presence webhook (no direction/numbers)."""
        body = payload.get('body') or {}
        telephony_status = (
            (status_leg or {}).get('telephonyStatus')
            or body.get('telephonyStatus')
            or body.get('aggregatedTelephonyStatus')
        )
        vals = {}
        was_answered = (
            pw_utils.is_call_answered_status((call_history or {}).status)
            if call_history else False
        )
        mapped_status = pw_utils.map_presence_status(telephony_status, was_answered=was_answered)
        if mapped_status != 'unknown':
            if call_history and call_history.status:
                current_rank = _STATUS_RANK.get(call_history.status, -1)
                new_rank = _STATUS_RANK.get(mapped_status, -1)
                if mapped_status == 'completed' or new_rank >= current_rank:
                    vals['status'] = mapped_status
            else:
                vals['status'] = mapped_status

        if status_leg and status_leg.get('terminationType'):
            vals['termination_type'] = status_leg['terminationType']

        sequence = body.get('sequence')
        if sequence is not None:
            vals['last_webhook_sequence'] = sequence

        is_final = (
            telephony_status == 'NoCall'
            or (status_leg or {}).get('terminationType') == 'final'
        )
        if is_final:
            end_time = pw_utils.parse_rc_datetime(payload.get('timestamp'))
            if end_time:
                vals['end_time'] = end_time
                start = call_history.start_time if call_history else None
                if not start and status_leg:
                    start = pw_utils.parse_rc_datetime(status_leg.get('startTime'))
                if start and end_time > start:
                    vals['duration'] = int((end_time - start).total_seconds())

        effective_status = vals.get('status') or (call_history.status if call_history else None)
        session_status_code = (status_leg or {}).get('sessionStatusCode')
        if session_status_code:
            session_result = tsw_utils.map_session_call_result(session_status_code)
            if session_result:
                vals['call_result'] = session_result
        elif effective_status:
            call_result = self._map_call_result_from_status(
                effective_status,
                (status_leg or {}).get('terminationType'),
            )
            if call_result:
                vals['call_result'] = call_result

        caller_name = pw_utils.extract_caller_name(status_leg)
        if caller_name and not (call_history and call_history.caller_name):
            vals['caller_name'] = caller_name

        return vals

    def _session_vals_from_aliases(self, session_info):
        """Build stored session id fields from collected aliases."""
        vals = {}
        telephony_session_id = session_info.get('telephony_session_id')
        numeric_session_id = session_info.get('numeric_session_id')
        if telephony_session_id:
            vals['ringcentral_telephony_session_id'] = telephony_session_id
        if numeric_session_id:
            vals['ringcentral_call_id'] = numeric_session_id
        elif telephony_session_id:
            vals['ringcentral_call_id'] = telephony_session_id
        return vals

    def _maybe_auto_link_partner(self):
        """Link contacts when direction-appropriate partner field is still empty."""
        for record in self.sudo():
            if record.direction == 'inbound' and not record.from_partner_id:
                record._link_contact_for_call()
            elif record.direction == 'outbound' and not record.to_partner_id:
                record._link_contact_for_call()

    @api.model
    def _map_call_result_from_status(self, status, termination_type=None):
        """Map internal call status to a high-level call result."""
        if termination_type and 'transfer' in str(termination_type).lower():
            return 'transferred'
        mapping = {
            'completed': 'answered',
            'answered': 'answered',
            'no-answer': 'missed',
            'busy': 'missed',
            'failed': 'failed',
        }
        return mapping.get(status)

    @api.model
    def _map_call_log_result_status(self, raw_result):
        """Map RingCentral call-log result to ringcentral.call.history status."""
        raw = (raw_result or '').lower().replace('_', ' ').strip()
        if raw in ('missed', 'noanswer', 'no answer', 'cancelled', 'canceled',
                   'rejected', 'declined', 'not answered', 'abandoned', 'hang up'):
            return 'no-answer'
        if raw in ('busy',):
            return 'busy'
        if raw in ('failed', 'error', 'blocked'):
            return 'failed'
        if raw in ('voicemail', 'vm'):
            return 'no-answer'
        if raw in ('answered', 'connected', 'in progress', 'accepted', 'call connected'):
            return 'completed'
        if raw in ('completed',):
            return 'completed'
        return 'unknown'

    @api.model
    def _collect_call_log_session_aliases(self, log_record):
        """Collect dedup aliases from a RingCentral call-log API record."""
        aliases = set()
        for key in ('telephonySessionId', 'sessionId', 'id'):
            value = log_record.get(key)
            if value:
                aliases.add(str(value).strip())
        telephony_ids = sorted(alias for alias in aliases if alias.startswith('s-'))
        numeric_ids = sorted(alias for alias in aliases if not alias.startswith('s-'))
        return {
            'primary_key': (telephony_ids[0] if telephony_ids else None) or (numeric_ids[0] if numeric_ids else None),
            'telephony_session_id': telephony_ids[0] if telephony_ids else None,
            'numeric_session_id': numeric_ids[0] if numeric_ids else None,
            'aliases': list(aliases),
        }

    @api.model
    def _vals_from_call_log_record(self, config, log_record):
        """Build call history values from a RingCentral call-log API record."""
        session_id = log_record.get('sessionId')
        telephony_session_id = log_record.get('telephonySessionId')
        log_id = log_record.get('id')
        start_time = pw_utils.parse_rc_datetime(log_record.get('startTime'))
        duration = log_record.get('duration') or 0

        from_info = log_record.get('from') or {}
        to_info = log_record.get('to') or {}
        from_number = from_info.get('phoneNumber') or from_info.get('extensionNumber') or ''
        to_number = to_info.get('phoneNumber') or to_info.get('extensionNumber') or ''

        end_time = False
        if start_time and duration:
            end_time = start_time + timedelta(seconds=duration)

        recording = log_record.get('recording') or {}
        recording_id = recording.get('id')

        from_number = from_number or 'unknown'
        to_number = to_number or 'unknown'
        direction = self._resolve_business_direction(
            config, from_number, to_number, log_record.get('direction'),
        )
        status = self._map_call_log_result_status(log_record.get('result'))
        call_result = self._map_call_result_from_status(status)

        user_vals = {}
        extension_info = log_record.get('extension') or {}
        extension_id = extension_info.get('id') or log_record.get('extensionId')
        extension_number = extension_info.get('extensionNumber') or extension_info.get('name')
        user = self._find_user_by_extension(extension_number, extension_id)
        if not user and direction == 'outbound':
            user = self._find_user_by_extension(
                extension_number=from_info.get('extensionNumber'),
                extension_id=from_info.get('extensionId'),
            )
        if not user and direction == 'inbound':
            user = self._find_user_by_extension(
                extension_number=to_info.get('extensionNumber'),
                extension_id=to_info.get('extensionId'),
            )
        if user:
            if direction == 'outbound':
                user_vals['initiated_by_id'] = user.id
            else:
                user_vals['answered_by_id'] = user.id

        session_info = self._collect_call_log_session_aliases(log_record)
        session_vals = self._session_vals_from_aliases(session_info)
        if log_id and not session_vals.get('ringcentral_call_id'):
            session_vals['ringcentral_call_id'] = str(log_id)

        return {
            'config_id': config.id,
            'company_id': self._resolve_company_id(user_vals, config=config),
            'ringcentral_call_log_id': str(log_id) if log_id else False,
            'direction': direction,
            'from_number': from_number,
            'to_number': to_number,
            'start_time': start_time or fields.Datetime.now(),
            'end_time': end_time,
            'duration': duration,
            'status': status,
            'call_result': call_result,
            'recording_id': str(recording_id) if recording_id else False,
            **session_vals,
            **user_vals,
        }

    @api.model
    def find_for_call_log(self, config, log_record):
        """Find an existing call history row for a call-log API record."""
        if not log_record:
            return self.browse()

        session_info = self._collect_call_log_session_aliases(log_record)
        if session_info.get('aliases'):
            match = self._find_call_for_session(config, session_info['aliases'])
            if match:
                return match

        log_id = log_record.get('id')
        if log_id:
            log_id_str = str(log_id)
            match = self.sudo().search([
                ('config_id', '=', config.id),
                '|',
                ('ringcentral_call_log_id', '=', log_id_str),
                ('ringcentral_call_id', '=', log_id_str),
            ], limit=1)
            if match:
                return match

        vals = self._vals_from_call_log_record(config, log_record)
        external_number = (
            vals.get('to_number') if vals.get('direction') == 'outbound' else vals.get('from_number')
        )
        return self._find_existing_call(
            config,
            session_aliases=session_info.get('aliases'),
            direction=vals.get('direction'),
            external_number=external_number,
            from_number=vals.get('from_number'),
            to_number=vals.get('to_number'),
            start_time=vals.get('start_time'),
            session_id=log_record.get('sessionId') or log_record.get('telephonySessionId'),
            time_window_minutes=30,
            allow_phone_window=not session_info.get('aliases'),
        )

    @api.model
    def _apply_call_log_sync_vals(self, existing, vals, log_record):
        """Merge call-log API values into an existing call history row."""
        session_info = self._collect_call_log_session_aliases(log_record)
        sync_vals = {
            k: v for k, v in vals.items()
            if k not in ('config_id', 'direction', 'from_number', 'to_number')
        }
        sync_vals.update(self._session_vals_from_aliases(session_info))

        log_id = log_record.get('id')
        if log_id and not existing.ringcentral_call_log_id:
            sync_vals['ringcentral_call_log_id'] = str(log_id)

        call_log_status = vals.get('status')
        if call_log_status and call_log_status != 'unknown':
            current_rank = _STATUS_RANK.get(existing.status, -1)
            new_rank = _STATUS_RANK.get(call_log_status, -1)
            if new_rank >= current_rank:
                sync_vals['status'] = call_log_status

        if vals.get('call_result'):
            sync_vals['call_result'] = vals['call_result']
        if vals.get('end_time'):
            sync_vals['end_time'] = vals['end_time']
        if vals.get('duration'):
            sync_vals['duration'] = vals['duration']
        if vals.get('recording_id'):
            sync_vals['recording_id'] = vals['recording_id']
        if vals.get('initiated_by_id') and not existing.initiated_by_id:
            sync_vals['initiated_by_id'] = vals['initiated_by_id']
        if vals.get('answered_by_id') and not existing.answered_by_id:
            sync_vals['answered_by_id'] = vals['answered_by_id']

        number_vals = {}
        if vals.get('from_number') and vals['from_number'] != 'unknown':
            if not existing.from_number or existing.from_number == 'unknown':
                number_vals['from_number'] = vals['from_number']
        if vals.get('to_number') and vals['to_number'] != 'unknown':
            if not existing.to_number or existing.to_number == 'unknown':
                number_vals['to_number'] = vals['to_number']

        existing.with_context(rc_allow_direction_update=True).write({
            **sync_vals,
            **number_vals,
        })
        existing._link_contact_for_call()
        existing._maybe_enrich_recording()
        return existing

    @api.model
    def sync_from_call_log_record(self, config, log_record, update_existing=True):
        """Create or update call history from a RingCentral call-log record."""
        if not log_record:
            return 'skipped', self.browse()

        existing = self.find_for_call_log(config, log_record)
        vals = self._vals_from_call_log_record(config, log_record)

        if existing:
            if not update_existing:
                return 'skipped', existing
            existing = self._apply_call_log_sync_vals(existing, vals, log_record)
            _logger.info(
                'RC call-log sync: action=updated session=%s call_id=%s history=%s',
                log_record.get('sessionId') or log_record.get('telephonySessionId') or '',
                log_record.get('id') or '',
                existing.id,
            )
            return 'updated', existing

        session_info = self._collect_call_log_session_aliases(log_record)
        record = self._create_presence_call_history(config, vals, session_info)
        record._link_contact_for_call()
        record._maybe_enrich_recording()
        _logger.info(
            'RC call-log sync: action=created session=%s call_id=%s',
            log_record.get('sessionId') or log_record.get('telephonySessionId') or '',
            log_record.get('id') or '',
        )
        return 'created', record

    @api.model
    def _resolve_business_direction(self, config, from_number, to_number, rc_direction):
        """Infer CRM direction from which leg carries the customer contact.

        - Contact on ``from_number`` → inbound (customer calling us)
        - Contact on ``to_number`` → outbound (us calling the customer)
        - Both legs match contacts → use RingCentral leg direction
        - Neither matches → fall back to RingCentral leg direction
        """
        partner_model = self.env['res.partner'].sudo()
        has_mobile = 'mobile' in partner_model._fields
        has_phone_sanitized = 'phone_sanitized' in partner_model._fields
        known_extensions = self.env['res.users'].sudo().search([
            ('ringcentral_extension', '!=', False),
        ]).mapped('ringcentral_extension')

        from_partner = False
        to_partner = False
        if (
            from_number and from_number != 'unknown'
            and pw_utils.is_external_pstn(from_number, known_extensions)
        ):
            from_partner = self._find_partner_for_number(
                from_number, partner_model, has_mobile, has_phone_sanitized,
            )
        if (
            to_number and to_number != 'unknown'
            and pw_utils.is_external_pstn(to_number, known_extensions)
        ):
            to_partner = self._find_partner_for_number(
                to_number, partner_model, has_mobile, has_phone_sanitized,
            )

        if from_partner and to_partner:
            direction = pw_utils.map_direction(rc_direction)
            _logger.info(
                'Direction %s from RC leg: both from %s and to %s match contacts',
                direction, from_number, to_number,
            )
            return direction

        if from_partner:
            _logger.info(
                'Direction inbound: contact on from_number %s (%s)',
                from_number, from_partner.display_name,
            )
            return 'inbound'

        if to_partner:
            _logger.info(
                'Direction outbound: contact on to_number %s (%s)',
                to_number, to_partner.display_name,
            )
            return 'outbound'

        return pw_utils.map_direction(rc_direction)

    @api.model
    def _resolve_call_direction(self, config, session_info, business_leg, call_history=None):
        """Determine CRM call direction; bootstrap merges first, then contact-based rule."""
        if call_history and call_history.direction:
            return call_history.direction

        if not business_leg:
            return 'outbound'

        from_number = pw_utils.extract_phone(business_leg.get('from')) or 'unknown'
        to_number = pw_utils.extract_phone(business_leg.get('to')) or 'unknown'
        session_id = session_info.get('primary_key') or session_info.get('canonical_id')

        pending_in = self._find_pending_inbound_merge(config, from_number, session_id)
        if pending_in:
            return 'inbound'

        pending_out = self._find_pending_outbound_merge(config, to_number, session_id)
        if pending_out:
            return 'outbound'

        return self._resolve_business_direction(
            config, from_number, to_number, business_leg.get('direction'),
        )

    def _find_pending_outbound_merge(self, config, to_number, session_id):
        """Find a recent pre-created outbound record to merge with this session."""
        if not to_number or to_number == 'unknown':
            return self.browse()
        cutoff = fields.Datetime.now() - timedelta(minutes=5)
        domain = [
            ('config_id', '=', config.id),
            ('direction', '=', 'outbound'),
            ('status', 'in', ['initiated', 'ringing', 'answered', 'completed']),
            ('start_time', '>=', cutoff),
        ]
        domain.append(('ringcentral_call_id', '=', False))
        domain.append(('ringcentral_telephony_session_id', '=', False))
        candidates = self.sudo().search(domain, order='start_time desc')
        for candidate in candidates:
            if phone_utils.phones_match(to_number, candidate.to_number, self.env):
                return candidate
        return self.browse()

    @api.model
    def process_presence_webhook(self, config, payload):
        """Process a RingCentral presence webhook and upsert call history by sessionId."""
        body = payload.get('body') or {}
        active_calls = body.get('activeCalls') or []
        if not active_calls:
            _logger.debug('RC presence webhook: no activeCalls in payload uuid=%s', payload.get('uuid'))
            return

        session_info = pw_utils.resolve_session_from_payload(body, active_calls)
        session_id = session_info.get('primary_key')
        if not session_id:
            _logger.warning('RC presence webhook: missing sessionId uuid=%s', payload.get('uuid'))
            return

        _logger.info(
            'RC presence webhook: session=%s uuid=%s legs=%d aliases=%s',
            session_id, payload.get('uuid'), len(active_calls), session_info.get('aliases'),
        )

        known_extensions = self.env['res.users'].sudo().search([
            ('ringcentral_extension', '!=', False),
        ]).mapped('ringcentral_extension')

        call_history = self._find_call_for_session(config, session_info.get('aliases'))

        business_leg = pw_utils.select_business_call_leg(active_calls, known_extensions)
        status_leg = business_leg or active_calls[0]
        current_leg = active_calls[0]
        is_internal = pw_utils.is_internal_agent_leg(current_leg, known_extensions)

        if call_history:
            if is_internal:
                status_leg = {
                    'telephonyStatus': body.get('aggregatedTelephonyStatus') or body.get('telephonyStatus'),
                    'terminationType': current_leg.get('terminationType'),
                    'startTime': current_leg.get('startTime'),
                    'sessionStatusCode': current_leg.get('sessionStatusCode'),
                }
            payload_log = call_history._append_webhook_payload(payload)
            sequence = body.get('sequence')
            if (
                sequence is not None
                and call_history.last_webhook_sequence
                and sequence < call_history.last_webhook_sequence
            ):
                _logger.debug(
                    'RC presence webhook: skipping out-of-order event session=%s seq=%s < %s',
                    session_id, sequence, call_history.last_webhook_sequence,
                )
                call_history.write({'webhook_payloads': payload_log})
                return

            update_vals = call_history._build_presence_update_vals(payload, status_leg, call_history)
            user_vals = call_history._user_vals_from_presence(
                body, current_leg if is_internal else status_leg, payload,
            )
            if user_vals.get('answered_by_id') and not call_history.answered_by_id:
                update_vals['answered_by_id'] = user_vals['answered_by_id']
            if user_vals.get('initiated_by_id') and not call_history.initiated_by_id:
                update_vals['initiated_by_id'] = user_vals['initiated_by_id']
            if business_leg and not is_internal:
                resolved_direction = self._resolve_call_direction(
                    config, session_info, business_leg, call_history=None,
                )
                if resolved_direction and resolved_direction != call_history.direction:
                    update_vals['direction'] = resolved_direction
                from_number = pw_utils.extract_phone(business_leg.get('from'))
                to_number = pw_utils.extract_phone(business_leg.get('to'))
                if from_number and from_number != 'unknown':
                    update_vals['from_number'] = from_number
                if to_number and to_number != 'unknown':
                    update_vals['to_number'] = to_number
            update_vals.update(call_history._session_vals_from_aliases(session_info))
            update_vals['webhook_payloads'] = payload_log
            call_history.with_context(rc_allow_direction_update=True).write(update_vals)
            call_history._link_contact_for_call()
            call_history._maybe_enrich_recording()
            _logger.info(
                'RC presence webhook: action=update session=%s uuid=%s direction=%s from=%s to=%s',
                session_id, payload.get('uuid'), call_history.direction,
                call_history.from_number, call_history.to_number,
            )
            telephony_status = (
                (status_leg or {}).get('telephonyStatus')
                or body.get('telephonyStatus')
                or body.get('aggregatedTelephonyStatus')
            )
            call_history._broadcast_inbound_ring_notification(payload, telephony_status)

            if is_internal:
                _logger.info(
                    'Ignoring internal RC leg for session %s (party %s, from %s): '
                    'direction/numbers unchanged, status updated to %s',
                    session_id,
                    current_leg.get('partyId'),
                    pw_utils.extract_phone(current_leg.get('from')),
                    update_vals.get('status', call_history.status),
                )
            return

        if not business_leg:
            _logger.info(
                'RC presence webhook: skipping create for session %s — '
                'only internal agent leg(s) received (from=%s)',
                session_id,
                pw_utils.extract_phone(current_leg.get('from')),
            )
            return

        from_number = pw_utils.extract_phone(business_leg.get('from'))
        to_number = pw_utils.extract_phone(business_leg.get('to'))
        start_time = pw_utils.parse_rc_datetime(business_leg.get('startTime'))
        if not start_time:
            start_time = pw_utils.parse_rc_datetime(payload.get('timestamp')) or fields.Datetime.now()

        from_number = from_number or 'unknown'
        to_number = to_number or 'unknown'
        caller_name = pw_utils.extract_caller_name(business_leg)
        create_vals = {
            'config_id': config.id,
            'company_id': self._resolve_company_id({}, config=config),
            'direction': self._resolve_call_direction(
                config, session_info, business_leg,
            ),
            'from_number': from_number,
            'to_number': to_number,
            'start_time': start_time,
        }
        create_vals.update(self._session_vals_from_aliases(session_info))
        if caller_name:
            create_vals['caller_name'] = caller_name
        create_vals.update(self._build_presence_update_vals(payload, status_leg))
        user_vals = self._user_vals_from_presence(body, business_leg, payload)
        if user_vals.get('initiated_by_id'):
            create_vals['initiated_by_id'] = user_vals['initiated_by_id']
        if user_vals.get('answered_by_id'):
            create_vals['answered_by_id'] = user_vals['answered_by_id']
        create_vals['webhook_payloads'] = [{
            'uuid': payload.get('uuid'),
            'timestamp': payload.get('timestamp'),
            'event': payload.get('event'),
            'body': body,
        }]

        resolved_direction = create_vals['direction']
        external_number = from_number if resolved_direction == 'inbound' else to_number
        existing = self._find_existing_call(
            config,
            session_aliases=session_info.get('aliases'),
            direction=resolved_direction,
            external_number=external_number if external_number != 'unknown' else None,
            from_number=from_number,
            to_number=to_number,
            start_time=start_time,
            session_id=session_id,
            time_window_minutes=10,
            allow_phone_window=True,
        )
        if existing:
            self._merge_presence_vals_into_record(existing, create_vals)
            _logger.info(
                'RC presence webhook: action=update session=%s uuid=%s direction=%s from=%s to=%s '
                '(merged into existing call record %s)',
                session_id, payload.get('uuid'), create_vals['direction'],
                from_number, to_number, existing.id,
            )
            telephony_status = (
                (status_leg or {}).get('telephonyStatus')
                or body.get('telephonyStatus')
                or body.get('aggregatedTelephonyStatus')
            )
            existing._broadcast_inbound_ring_notification(payload, telephony_status)
            return

        pending = self._find_pending_inbound_merge(config, from_number, session_id)
        if not pending:
            pending = self._find_pending_outbound_merge(config, to_number, session_id)
        if pending:
            self._merge_presence_vals_into_record(pending, create_vals)
            _logger.info(
                'RC presence webhook: action=update session=%s uuid=%s direction=%s from=%s to=%s '
                '(merged into pre-created call record %s)',
                session_id, payload.get('uuid'), create_vals['direction'],
                from_number, to_number, pending.id,
            )
            telephony_status = (
                (status_leg or {}).get('telephonyStatus')
                or body.get('telephonyStatus')
                or body.get('aggregatedTelephonyStatus')
            )
            pending._broadcast_inbound_ring_notification(payload, telephony_status)
            return

        _logger.info(
            'RC presence webhook: action=create session=%s uuid=%s direction=%s from=%s to=%s',
            session_id, payload.get('uuid'), create_vals['direction'], from_number, to_number,
        )
        record = self._create_presence_call_history(config, create_vals, session_info)
        telephony_status = (
            (status_leg or {}).get('telephonyStatus')
            or body.get('telephonyStatus')
            or body.get('aggregatedTelephonyStatus')
        )
        record._broadcast_inbound_ring_notification(payload, telephony_status)

    @api.model
    def _is_session_unique_violation(self, error):
        """True when create failed due to config_id + ringcentral_call_id uniqueness."""
        if Psycopg2IntegrityError and isinstance(error, Psycopg2IntegrityError):
            if getattr(error, 'pgcode', None) == '23505':
                return True
        cause = getattr(error, '__cause__', None)
        if cause and getattr(cause, 'pgcode', None) == '23505':
            return True
        message = str(error).lower()
        return (
            'config_session_uniq' in message
            or 'config_telephony_session_uniq' in message
            or 'duplicate key' in message
        )

    @api.model
    def _create_presence_call_history(self, config, create_vals, session_info):
        """Create call history from webhook, merging on unique constraint races."""
        try:
            with self.env.cr.savepoint():
                record = self.with_context(rc_allow_direction_update=True).create(create_vals)
        except Exception as error:
            if not self._is_session_unique_violation(error):
                raise
            _logger.info(
                'RC presence webhook: concurrent create for session %s — merging into existing record',
                session_info.get('primary_key') or session_info.get('canonical_id'),
            )
            existing = self._find_call_for_session(config, session_info.get('aliases'))
            if not existing:
                raise
            self._merge_presence_vals_into_record(existing, create_vals)
            return existing

        record._link_contact_for_call()
        record._maybe_enrich_recording()
        return record

    def _broadcast_inbound_ring_notification(self, payload=None, telephony_status=None):
        """Hook for submodules to push inbound ring notifications to connected clients."""
        return

    def _link_contact_for_call(self):
        """Link contact on the external PSTN side based on call direction."""
        self = self.sudo()
        partner_model = self.env['res.partner'].sudo()
        has_mobile = 'mobile' in partner_model._fields
        has_phone_sanitized = 'phone_sanitized' in partner_model._fields
        known_extensions = self.env['res.users'].sudo().search([
            ('ringcentral_extension', '!=', False),
        ]).mapped('ringcentral_extension')

        for record in self:
            write_vals = {}
            if record.direction == 'inbound':
                if (
                    not record.from_partner_id
                    and record.from_number
                    and record.from_number != 'unknown'
                ):
                    partner = record._find_partner_for_number(
                        record.from_number, partner_model, has_mobile, has_phone_sanitized,
                        call_record=record,
                    )
                    if partner:
                        write_vals['from_partner_id'] = partner.id
            elif record.direction == 'outbound':
                if (
                    not record.to_partner_id
                    and record.to_number
                    and record.to_number != 'unknown'
                ):
                    partner = record._find_partner_for_number(
                        record.to_number, partner_model, has_mobile, has_phone_sanitized,
                        call_record=record,
                    )
                    if partner:
                        write_vals['to_partner_id'] = partner.id

            if not write_vals:
                for number, field_name in (
                    (record.from_number, 'from_partner_id'),
                    (record.to_number, 'to_partner_id'),
                ):
                    if (
                        write_vals.get(field_name)
                        or getattr(record, field_name)
                        or not number
                        or number == 'unknown'
                        or not pw_utils.is_external_pstn(number, known_extensions)
                    ):
                        continue
                    partner = record._find_partner_for_number(
                        number, partner_model, has_mobile, has_phone_sanitized,
                        call_record=record,
                    )
                    if partner:
                        write_vals[field_name] = partner.id
                        break

            if write_vals:
                record.write(write_vals)

    def _auto_link_partner(self):
        """Backward-compatible wrapper for direction-aware contact linking."""
        self._link_contact_for_call()

    def _maybe_enrich_recording(self):
        """Fetch recording ID from call-log API when the call is finished."""
        for record in self.sudo():
            if record.recording_id or not record.ringcentral_call_id or not record.config_id:
                continue
            if record.status not in ('completed', 'answered', 'no-answer', 'failed', 'busy'):
                continue
            rec_id = record.config_id.lookup_recording_id_for_session(record.ringcentral_call_id)
            if rec_id:
                record.write({'recording_id': rec_id})
                _logger.info(
                    'Linked recording %s to call history %s (session %s)',
                    rec_id, record.id, record.ringcentral_call_id,
                )

    def _clean_phone_number(self, phone):
        """Clean phone number for matching - remove all non-digit characters."""
        return phone_utils.normalize_phone(phone)

    def _normalize_phone_number(self, phone):
        """Normalize phone number using partner utilities when available."""
        return phone_utils.normalize_phone_number(phone, self.env)

    def _get_all_phone_variants(self, number):
        """Generate all possible variants of a phone number for matching."""
        return phone_utils.get_phone_variants(number, self.env)

    def _normalize_for_comparison(self, phone):
        """Normalize phone number to digits only for comparison."""
        return phone_utils.normalize_phone(phone)

    def _find_partner_for_number(self, number, partner_model, has_mobile, has_phone_sanitized, call_record=None):
        """Find partner matching a given phone number - tries multiple matching strategies."""
        if not number:
            return False

        input_digits = self._normalize_for_comparison(number)
        if not input_digits or len(input_digits) < 7:
            return False

        domain = phone_utils.build_partner_phone_domain(number, partner_model)
        if domain:
            candidates = partner_model.search(
                domain, order='write_date desc, create_date desc', limit=30,
            )
            for partner in candidates:
                if phone_utils.partner_matches_phone(partner, number, self.env):
                    if call_record:
                        _logger.info(
                            'Linked partner %s to call %s (input %s)',
                            partner.display_name, call_record.id, number,
                        )
                    return partner

        # Fallback: scan partners whose phone/mobile may match (last-10 ilike).
        last10 = phone_utils.get_last10(input_digits)
        if last10 and len(last10) >= 7:
            clauses = []
            for field in phone_utils.partner_phone_fields(partner_model):
                clauses.append((field, 'ilike', last10))
            if clauses:
                fallback_domain = (
                    clauses if len(clauses) == 1
                    else ['|'] * (len(clauses) - 1) + clauses
                )
                potential_partners = partner_model.search(
                    fallback_domain, order='write_date desc, create_date desc', limit=50,
                )
                for partner in potential_partners:
                    if phone_utils.partner_matches_phone(partner, number, self.env):
                        if call_record:
                            _logger.info(
                                'Linked partner %s to call %s via normalized fallback (input %s)',
                                partner.display_name, call_record.id, number,
                            )
                        return partner

        if call_record:
            _logger.debug(
                'No partner match for call %s (input %s, normalized digits %s)',
                call_record.id, number, input_digits,
            )
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

    def _format_ringsense_transcript(self, insights_data):
        """Format RingSense insights.Transcript into readable text."""
        insights = insights_data.get('insights') or {}
        transcript_items = insights.get('Transcript') or []
        speaker_info = {s.get('speakerId'): s.get('name', 'Unknown') for s in (insights_data.get('speakerInfo') or [])}
        lines = []
        for item in sorted(transcript_items, key=lambda x: float(x.get('start', 0))):
            text = (item.get('text') or '').strip()
            if not text:
                continue
            speaker_id = item.get('speakerId', '')
            speaker_name = speaker_info.get(speaker_id) or f"Speaker {speaker_id}" if speaker_id else "Speaker"
            lines.append(f"[{speaker_name}]: {text}")
        return '\n\n'.join(lines) if lines else ''

    def action_fetch_transcript(self):
        """Fetch transcript from RingCentral. Prioritizes RingSense; falls back to Speech-to-Text."""
        self.ensure_one()

        if not self.recording_id:
            raise UserError(_('No recording available for this call.'))

        config = self.config_id
        if not config:
            raise UserError(_('No RingCentral configuration found.'))

        try:
            # 1. Try RingSense first
            insights = config._fetch_ringsense_insights(self.recording_id)
            if insights:
                transcript_text = self._format_ringsense_transcript(insights)
                if transcript_text:
                    self.write({
                        'transcript': transcript_text,
                        'transcript_available': True,
                        'transcript_source': 'ringsense',
                        'transcript_job_id': False,
                    })
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Success'),
                            'message': _('Transcript fetched from RingSense.'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }

            # 2. Fallback to Speech-to-Text (async)
            job_id = config._request_speech_to_text(self.recording_id)
            self.write({
                'transcript_job_id': job_id,
                'transcript_source': 'speech_to_text',
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Transcription Started'),
                    'message': _('Transcription is in progress. Check back in a few minutes.'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        except UserError as e:
            err_str = str(e)
            if '403' in err_str or 'Forbidden' in err_str or 'permission' in err_str.lower() or '[AI]' in err_str:
                _logger.warning(
                    "Transcript unavailable (AI/permission). RingSense and Speech-to-Text require app permissions: %s",
                    err_str
                )
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Transcript unavailable'),
                        'message': _(
                            'To use transcripts, enable the [AI] permission for your RingCentral app '
                            'in the Developer Console, then reconnect the integration.'
                        ),
                        'type': 'warning',
                        'sticky': True,
                    }
                }
            raise
        except Exception as e:
            _logger.error("Error fetching transcript: %s", str(e), exc_info=True)
            raise UserError(_('Failed to fetch transcript: %s') % str(e))

    @api.model
    def cron_poll_transcript_jobs(self):
        """Poll pending speech-to-text jobs and update transcripts when complete."""
        pending = self.sudo().search([
            ('transcript_job_id', '!=', False),
            ('transcript_available', '=', False),
        ], limit=20)
        for record in pending:
            try:
                config = record.config_id
                if not config or not config.access_token:
                    continue
                if config._is_api_rate_limited():
                    break
                result = config._get_speech_to_text_result(record.transcript_job_id)
                status = (result or {}).get('status', '')
                if status == 'Success':
                    response = (result or {}).get('response') or {}
                    transcript = response.get('transcript', '')
                    record.write({
                        'transcript': transcript or _('(No speech detected)'),
                        'transcript_available': True,
                        'transcript_job_id': False,
                    })
                elif status and status not in ('InProgress', 'Pending', 'Accepted'):
                    _logger.warning("Speech-to-text job %s failed with status: %s", record.transcript_job_id, status)
                    record.write({'transcript_job_id': False})
            except Exception as e:
                _logger.warning("Error polling transcript job for call %s: %s", record.id, str(e))

    def action_refresh_recording(self):
        """Fetch recording metadata from RingCentral call-log API."""
        self.ensure_one()
        self._maybe_enrich_recording()
        if not self.recording_id:
            raise UserError(_('No recording found for this call yet. Try again after the call completes.'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recording Ready'),
                'message': _('Recording is now linked to this call.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_download_recording(self):
        """Download call recording via authenticated Odoo proxy."""
        self.ensure_one()

        if not self.recording_id:
            self._maybe_enrich_recording()
        if not self.recording_id:
            raise UserError(_('No recording available for this call.'))

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': f'{base_url}/ringcentral/recording/{self.id}?download=1',
            'target': 'new',
        }

