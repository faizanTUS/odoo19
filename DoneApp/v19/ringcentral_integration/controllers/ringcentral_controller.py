# -*- coding: utf-8 -*-
from urllib.parse import quote

from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class RingCentralController(http.Controller):

    def _ensure_ringcentral_access(self):
        """Raise AccessError when the current user lacks RingCentral access."""
        if not request.env.user.has_ringcentral_access():
            raise AccessError(request.env._('You do not have RingCentral access.'))

    def _parse_webhook_json(self):
        """Parse RingCentral webhook POST body as JSON."""
        import json
        raw = request.httprequest.data
        if not raw:
            return {}
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')
        try:
            return json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            _logger.warning('Could not parse webhook body: %s', error)
            return {}

    @http.route('/ringcentral/webhook/<int:config_id>', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def webhook_handler(self, config_id, **kwargs):
        """Handle RingCentral webhook events and validation token"""
        # Handle validation token FIRST (GET or POST during subscription creation)
        # This must be checked before any other processing
        validation_token = request.httprequest.headers.get('Validation-Token')
        if validation_token:
            # Echo back Validation-Token in response header as required by RingCentral
            response = request.make_response('', status=200)
            response.headers['Validation-Token'] = validation_token
            return response
        
        # For GET requests without validation token, just return OK
        if request.httprequest.method == 'GET':
            return request.make_response('OK', status=200)
        
        # Handle webhook events (POST request)
        try:
            # Use sudo() to bypass access rights - webhooks are external calls without user auth
            # Validate config exists and is active
            config = request.env['ringcentral.config'].sudo().browse(config_id)
            if not config.exists() or not config.active:
                _logger.warning(f"Invalid or inactive config ID: {config_id}")
                return request.make_response('Invalid configuration', status=400)

            # Get webhook data - handle empty body gracefully
            data = self._parse_webhook_json()
            print("data>>>>>>>>>>>>>>>>>>>>", data)
            # Check if this is a subscription validation event
            if data.get('event') == '/restapi/v1.0/subscription':
                return request.make_response('OK', status=200)
            
            # If no data or empty event, return OK (might be a validation ping)
            if not data or not data.get('event'):
                return request.make_response('OK', status=200)
            
            event_type = data.get('event')
            _logger.info(
                'RingCentral webhook config=%s event=%s uuid=%s',
                config_id, event_type, data.get('uuid'),
            )

            # Handle different event types by event path
            if '/telephony/sessions' in str(event_type):
                self._handle_telephony_session(config, data)
            elif '/presence' in str(event_type):
                self._handle_call_notification(config, data)
            elif '/recording' in str(event_type):
                self._handle_recording_ready(config, data)
            elif '/call-log' in str(event_type):
                self._handle_call_log_event(config, data)
            elif '/transcript' in str(event_type):
                self._handle_transcription_ready(config, data)
            elif '/message-store' in str(event_type):
                self._handle_message_store_event(config, data)

            return request.make_response('OK', status=200)
        except Exception as e:
            _logger.error(f"Error processing RingCentral webhook: {str(e)}", exc_info=True)
            # Return 200 OK even on error to prevent RingCentral from retrying
            # Log the error but don't fail the webhook validation
            return request.make_response('OK', status=200)

    def _dispatch_inbound_lead_popup(self, config, data, source='presence'):
        """Extension point for inbound lead popup (ringcentral_lead_creation)."""
        if 'ringcentral.inbound.popup' not in request.env:
            return
        try:
            request.env['ringcentral.inbound.popup'].sudo().notify_from_webhook(
                config, data, source=source,
            )
        except KeyError:
            pass

    def _handle_call_notification(self, config, data):
        """Handle presence call notification webhook."""
        try:
            self._dispatch_inbound_lead_popup(config, data, source='presence')
            request.env['ringcentral.call.history'].sudo().process_presence_webhook(config, data)
        except Exception as e:
            _logger.error("Error handling call notification: %s", str(e), exc_info=True)

    def _handle_telephony_session(self, config, data):
        """Handle account/extension telephony session webhook."""
        try:
            from odoo.addons.ringcentral_integration.utils import telephony_session_webhook as tsw_utils
            normalized = tsw_utils.normalize_telephony_session_payload(data)
            if normalized:
                self._dispatch_inbound_lead_popup(config, normalized, source='telephony')
            request.env['ringcentral.call.history'].sudo().process_telephony_session_webhook(
                config, data,
            )
        except Exception as e:
            _logger.error("Error handling telephony session: %s", str(e), exc_info=True)

    def _handle_recording_ready(self, config, data):
        """Handle recording ready webhook."""
        try:
            body = data.get('body', {}) or {}
            recording_id = (
                body.get('recordingId')
                or body.get('id')
                or (body.get('recording') or {}).get('id')
            )
            session_id = (
                body.get('sessionId')
                or body.get('telephonySessionId')
                or (body.get('telephonySession') or {}).get('sessionId')
            )
            if not recording_id:
                return

            CallHistory = request.env['ringcentral.call.history'].sudo()
            call_history = CallHistory.browse()
            if session_id:
                session_id = str(session_id)
                call_history = CallHistory._find_call_for_session(config, [session_id])
            if not call_history and body.get('callLogId'):
                call_history = CallHistory.search([
                    ('config_id', '=', config.id),
                    ('ringcentral_call_log_id', '=', str(body['callLogId'])),
                ], limit=1)

            if call_history:
                call_history.write({'recording_id': str(recording_id)})
                _logger.info(
                    'Stored recording %s on call history %s (session %s)',
                    recording_id, call_history.id, session_id,
                )
            else:
                _logger.info(
                    'Recording webhook received but no call history for session %s',
                    session_id,
                )
        except Exception as e:
            _logger.error("Error handling recording ready: %s", str(e), exc_info=True)

    def _handle_transcription_ready(self, config, data):
        """Handle transcription ready webhook"""
        try:
            body = data.get('body', {})
            transcript_text = body.get('transcript') or body.get('text', '')
            call_id = body.get('sessionId') or body.get('telephonySessionId')
            
            if call_id and transcript_text:
                call_history = request.env['ringcentral.call.history'].sudo()._find_call_for_session(
                    config, [str(call_id)],
                )
                
                if call_history:
                    call_history.write({
                        'transcript': transcript_text,
                        'transcript_available': True,
                    })
                    
        except Exception as e:
            _logger.error(f"Error handling transcription ready: {str(e)}")

    def _handle_call_log_event(self, config, data):
        """Enrich or create call history from a call-log webhook payload."""
        try:
            body = data.get('body') or {}
            if not body:
                return
            log_record = body if body.get('id') or body.get('sessionId') else body.get('record') or body
            if not log_record or not isinstance(log_record, dict):
                return
            CallHistory = request.env['ringcentral.call.history'].sudo()
            action, record = CallHistory.sync_from_call_log_record(config, log_record, update_existing=True)
            if action in ('created', 'updated') and record:
                _logger.info(
                    'Call-log webhook %s call history %s (session %s)',
                    action, record.id, record.ringcentral_call_id,
                )
        except Exception as e:
            _logger.error("Error handling call-log event: %s", str(e), exc_info=True)

    def _handle_message_store_event(self, config, data):
        """Placeholder for message-store events (SMS/voicemail)."""
        try:
            pass  # Message-store events not currently processed
        except Exception as e:
            _logger.error(f"Error handling message-store event: {str(e)}")

    @http.route('/ringcentral/api/call-event', type='jsonrpc', auth='user', methods=['POST'])
    def api_call_event(self, event, phone_number=None, session_id=None, direction='outbound', caller_name=None, **kwargs):
        """Record call lifecycle events from the embedded widget."""
        try:
            self._ensure_ringcentral_access()
            record_id = request.env['ringcentral.call.history'].process_call_event(
                event,
                phone_number=phone_number,
                session_id=session_id,
                direction=direction,
                caller_name=caller_name,
            )
            return {'status': 'success', 'record_id': record_id or False}
        except Exception as e:
            _logger.error("Error processing call event: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/ringcentral/api/session', type='jsonrpc', auth='user', methods=['POST'])
    def api_get_session(self, **kwargs):
        """Lightweight session info for frontend access gating."""
        try:
            return {
                'status': 'success',
                'data': request.env.user.get_ringcentral_session_info(),
            }
        except Exception as e:
            _logger.error("Error getting RingCentral session: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/ringcentral/api/config', type='jsonrpc', auth='user', methods=['POST'])
    def api_get_config(self, **kwargs):
        """API endpoint to get RingCentral configuration for widget"""
        try:
            self._ensure_ringcentral_access()
            config = (
                request.env['ringcentral.config']
                .sudo()
                ._get_company_active_config(request.env.company)
            )
            if not config:
                return {
                    'status': 'success',
                    'data': {
                        'client_id': None,
                        'server_url': None,
                        'is_connected': False,
                    }
                }
            
            # Return minimal data quickly - avoid any computed fields that might be slow
            # Read fields directly without triggering any computes
            return {
                'status': 'success',
                'data': {
                    'client_id': config.client_id or None,
                    'server_url': config.server_url or None,
                    'is_connected': bool(config.access_token),  # Simple check, no compute
                }
            }
        except Exception as e:
            _logger.error(f"Error getting config: {str(e)}")
            # Return error response quickly
            return {'status': 'error', 'message': str(e)}

    @http.route('/ringcentral/recording/<int:call_history_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_recording(self, call_history_id, download=False, **kwargs):
        """Proxy recording with authentication for playback or download."""
        try:
            self._ensure_ringcentral_access()
            call_history = request.env['ringcentral.call.history'].browse(call_history_id)
            if not call_history.exists():
                return request.make_response('Recording not found', status=404)

            if not call_history.recording_id:
                call_history._maybe_enrich_recording()
            if not call_history.recording_id:
                return request.make_response('No recording available', status=404)

            config = call_history.config_id
            if not config:
                return request.make_response('Not authenticated', status=401)

            try:
                content, content_type = config.fetch_recording_content(call_history.recording_id)
            except UserError as error:
                message = str(error)
                status = 410 if 'expired' in message.lower() else 401
                _logger.warning(
                    'Recording fetch denied for call %s (recording %s): %s',
                    call_history.id,
                    call_history.recording_id,
                    message,
                )
                return request.make_response(message, status=status)
            if not content:
                return request.make_response('Recording content empty', status=404)

            range_header = request.httprequest.headers.get('Range')
            status = 200
            content_start = 0
            content_end = len(content) - 1
            body = content
            if range_header and range_header.startswith('bytes='):
                try:
                    range_spec = range_header.split('=', 1)[1]
                    start_str, end_str = (range_spec.split('-', 1) + [''])[:2]
                    if start_str:
                        content_start = int(start_str)
                    if end_str:
                        content_end = int(end_str)
                    if not start_str and end_str:
                        chunk_len = int(end_str)
                        content_start = max(len(content) - chunk_len, 0)
                        content_end = len(content) - 1
                    content_start = max(content_start, 0)
                    content_end = min(content_end, len(content) - 1)
                    if content_start > content_end:
                        return request.make_response(
                            'Invalid range',
                            status=416,
                            headers=[('Content-Range', f'bytes */{len(content)}')],
                        )
                    body = content[content_start:content_end + 1]
                    status = 206
                except Exception:
                    return request.make_response(
                        'Invalid range',
                        status=416,
                        headers=[('Content-Range', f'bytes */{len(content)}')],
                    )

            disposition = 'attachment' if download else 'inline'
            filename = f'recording_{call_history.recording_id}.mp3'
            headers = [
                ('Content-Type', content_type or 'audio/mpeg'),
                ('Content-Disposition', f'{disposition}; filename="{filename}"'),
                ('Accept-Ranges', 'bytes'),
                ('Content-Length', str(len(body))),
            ]
            if status == 206:
                headers.append(('Content-Range', f'bytes {content_start}-{content_end}/{len(content)}'))
            return request.make_response(body, status=status, headers=headers)
        except Exception as e:
            _logger.error("Error fetching recording: %s", str(e), exc_info=True)
            return request.make_response(f'Error: {str(e)}', status=500)

    @http.route('/ringcentral/oauth', type='http', auth='public', methods=['GET'], csrf=False)
    def ringcentral_oauth_callback(self, **kwargs):
        """OAuth2 callback: exchange code for tokens and redirect to originating page."""
        Config = request.env['ringcentral.config'].sudo()
        return_url = '/web'
        try:
            code = kwargs.get('code')
            error = kwargs.get('error')
            state_data = Config._decode_oauth_state(kwargs.get('state'))
            redirect_uri, config_id, session_return_url = Config._pop_oauth_context()
            return_url = state_data.get('return_url') or session_return_url or return_url
            if state_data.get('config_id'):
                config_id = state_data.get('config_id')
            if config_id:
                config = Config.browse(config_id)
            else:
                config = Config.search([('active', '=', True)], limit=1)
            if not config:
                return request.redirect(
                    Config._build_oauth_error_redirect(return_url, 'No active configuration')
                )
            if not redirect_uri:
                redirect_uri = config._get_oauth_redirect_uri()
            if error:
                return request.redirect(Config._build_oauth_error_redirect(return_url, error))
            if not code:
                return request.redirect(
                    Config._build_oauth_error_redirect(return_url, 'Missing authorization code')
                )
            _logger.info('RingCentral OAuth callback redirect_uri=%s return_url=%s', redirect_uri, return_url)
            config.exchange_code_for_token(code, redirect_uri)
            return request.redirect(Config._build_oauth_success_redirect(return_url))
        except Exception as e:
            _logger.error("OAuth callback error: %s", str(e))
            return request.redirect(Config._build_oauth_error_redirect(return_url, str(e)))
