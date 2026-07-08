# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class RingCentralController(http.Controller):

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
            data = {}
            if request.httprequest.data:
                try:
                    data = request.jsonrequest
                except Exception:
                    # Try to parse raw data
                    import json
                    try:
                        data = json.loads(request.httprequest.data.decode('utf-8'))
                    except Exception as parse_error:
                        _logger.warning(f"Could not parse webhook body: {str(parse_error)}")
                        # Return OK even if we can't parse - might be a validation request
                        return request.make_response('OK', status=200)
            
            # Check if this is a subscription validation event
            if data.get('event') == '/restapi/v1.0/subscription':
                return request.make_response('OK', status=200)
            
            # If no data or empty event, return OK (might be a validation ping)
            if not data or not data.get('event'):
                return request.make_response('OK', status=200)
            
            event_type = data.get('event')

            # Handle different event types by event path
            if '/telephony/sessions' in str(event_type) or '/presence' in str(event_type):
                self._handle_call_notification(config, data)
            elif '/call-log' in str(event_type):
                self._handle_call_log_event(config, data)
            elif '/message-store' in str(event_type):
                self._handle_message_store_event(config, data)

            return request.make_response('OK', status=200)
        except Exception as e:
            _logger.error(f"Error processing RingCentral webhook: {str(e)}", exc_info=True)
            # Return 200 OK even on error to prevent RingCentral from retrying
            # Log the error but don't fail the webhook validation
            return request.make_response('OK', status=200)

    def _handle_call_notification(self, config, data):
        """Handle call notification webhook"""
        try:
            body = data.get('body', {})
            call_id = body.get('telephonySessionId') or body.get('sessionId')
            direction = 'inbound' if body.get('direction') == 'Inbound' else 'outbound'
            
            from_info = body.get('from', {})
            to_info = body.get('to', {})
            
            from_number = from_info.get('phoneNumber', '') if isinstance(from_info, dict) else str(from_info)
            to_number = to_info.get('phoneNumber', '') if isinstance(to_info, dict) else str(to_info)
            
            status = body.get('status', 'unknown')
            start_time = body.get('startTime')
            
            # Map RingCentral status to our status
            status_mapping = {
                'Setup': 'initiated',
                'Proceeding': 'ringing',
                'Answered': 'answered',
                'Disconnected': 'completed',
                'Gone': 'failed',
                'Parked': 'ringing',
                'Hold': 'answered',
            }
            mapped_status = status_mapping.get(status, 'unknown')
            
            # Find or create call history (use sudo for webhook operations)
            call_history = request.env['ringcentral.call.history'].sudo().search([
                ('ringcentral_call_id', '=', call_id)
            ], limit=1)
            
            vals = {
                'config_id': config.id,
                'ringcentral_call_id': call_id,
                'direction': direction,
                'from_number': from_number,
                'to_number': to_number,
                'status': mapped_status,
                'start_time': start_time,
            }
            
            if call_history:
                call_history.write(vals)
            else:
                request.env['ringcentral.call.history'].sudo().create(vals)

            # Don't sync from webhook - let scheduled cron handle it
            # Webhook must return quickly to RingCentral (Odoo 19 best practice)
            # The existing scheduled action will sync call history periodically
                
        except Exception as e:
            _logger.error(f"Error handling call notification: {str(e)}")

    def _handle_recording_ready(self, config, data):
        """Handle recording ready webhook"""
        try:
            body = data.get('body', {})
            recording_id = body.get('recordingId') or body.get('id')
            call_id = body.get('sessionId') or body.get('telephonySessionId')
            
            if call_id and recording_id:
                call_history = request.env['ringcentral.call.history'].sudo().search([
                    ('ringcentral_call_id', '=', call_id)
                ], limit=1)
                
                if call_history:
                    call_history.write({
                        'recording_id': recording_id,
                    })
                    
        except Exception as e:
            _logger.error(f"Error handling recording ready: {str(e)}")

    def _handle_transcription_ready(self, config, data):
        """Handle transcription ready webhook"""
        try:
            body = data.get('body', {})
            transcript_text = body.get('transcript') or body.get('text', '')
            call_id = body.get('sessionId') or body.get('telephonySessionId')
            
            if call_id and transcript_text:
                call_history = request.env['ringcentral.call.history'].sudo().search([
                    ('ringcentral_call_id', '=', call_id)
                ], limit=1)
                
                if call_history:
                    call_history.write({
                        'transcript': transcript_text,
                        'transcript_available': True,
                    })
                    
        except Exception as e:
            _logger.error(f"Error handling transcription ready: {str(e)}")

    def _handle_call_log_event(self, config, data):
        """Lightweight handler for call-log webhook - no sync needed."""
        # Don't sync from webhook - let scheduled cron handle it
        # This ensures webhook returns quickly (Odoo 19 best practice)
        pass

    def _handle_message_store_event(self, config, data):
        """Placeholder for message-store events (SMS/voicemail)."""
        try:
            pass  # Message-store events not currently processed
        except Exception as e:
            _logger.error(f"Error handling message-store event: {str(e)}")

    @http.route('/ringcentral/api/config', type='json', auth='user', methods=['POST'],csrf=False,)
    def api_get_config(self, **kwargs):
        """API endpoint to get RingCentral configuration for widget"""
        try:
            # Fast lookup - avoid computing is_connected which might be slow
            # Use sudo() to avoid any permission checks that might slow things down
            config = request.env['ringcentral.config'].sudo().search([('active', '=', True)], limit=1)
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
    def get_recording(self, call_history_id, **kwargs):
        """Proxy recording with authentication"""
        try:
            call_history = request.env['ringcentral.call.history'].browse(call_history_id)
            if not call_history.exists():
                return request.make_response('Recording not found', status=404)
            
            if not call_history.recording_id:
                return request.make_response('No recording available', status=404)
            
            config = call_history.config_id
            if not config or not config.access_token:
                return request.make_response('Not authenticated', status=401)
            
            # Get recording URL
            recording_url = call_history.recording_url
            if not recording_url:
                return request.make_response('Recording URL not available', status=404)
            
            # Fetch recording with authentication
            import requests
            headers = {
                'Authorization': f'Bearer {config.access_token}',
                'Accept': 'audio/*, */*',
            }
            
            req_kwargs = config._build_request_kwargs()
            response = requests.get(recording_url, headers=headers, stream=True, timeout=30, **req_kwargs)
            response.raise_for_status()
            
            # Determine content type
            content_type = response.headers.get('Content-Type', 'audio/mpeg')
            content_length = response.headers.get('Content-Length')
            
            # Stream the recording
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            # Return the recording as a stream
            return request.make_response(
                generate(),
                headers=[
                    ('Content-Type', content_type),
                    ('Content-Disposition', f'inline; filename="recording_{call_history.recording_id}.mp3"'),
                ] + ([('Content-Length', content_length)] if content_length else []),
            )
        except Exception as e:
            _logger.error(f"Error fetching recording: {str(e)}", exc_info=True)
            return request.make_response(f'Error: {str(e)}', status=500)

    @http.route('/ringcentral/oauth', type='http', auth='public', methods=['GET'], csrf=False)
    def ringcentral_oauth_callback(self, **kwargs):
        """OAuth2 callback: exchange code for tokens and redirect to config."""
        try:
            code = kwargs.get('code')
            error = kwargs.get('error')
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_uri = f"{base_url}/ringcentral/oauth"
            config = request.env['ringcentral.config'].sudo().search([('active', '=', True)], limit=1)
            if not config:
                return request.redirect('/web?ringcentral_status=error&ringcentral_message=No+active+configuration')
            if error:
                return request.redirect(f"/web?ringcentral_status=error&ringcentral_message={error}")
            if not code:
                return request.redirect('/web?ringcentral_status=error&ringcentral_message=Missing+authorization+code')
            # Exchange code
            config.exchange_code_for_token(code, redirect_uri)
            return request.redirect('/web?ringcentral_status=success')
        except Exception as e:
            _logger.error(f"OAuth callback error: {str(e)}")
            return request.redirect(f"/web?ringcentral_status=error&ringcentral_message={http.escape(str(e))}")
