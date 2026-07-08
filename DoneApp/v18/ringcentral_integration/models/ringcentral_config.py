# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, timezone
from urllib.parse import urlparse
import socket
import requests
import json
import logging
import random
import time

_logger = logging.getLogger(__name__)

try:
    from psycopg2 import errors as psycopg2_errors
    PG_SERIALIZATION_ERRORS = (psycopg2_errors.SerializationFailure,)
except ImportError:
    PG_SERIALIZATION_ERRORS = ()


class RingCentralConfig(models.Model):
    _name = 'ringcentral.config'
    _description = 'RingCentral Configuration'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Configuration Name', required=True, default='RingCentral Configuration')
    client_id = fields.Char(string='Client ID', required=True, help='RingCentral Application Client ID')
    client_secret = fields.Char(string='Client Secret', required=True, help='RingCentral Application Client Secret')
    server_url = fields.Selection([
        ('https://platform.ringcentral.com', 'Production'),
        ('https://platform.devtest.ringcentral.com', 'Sandbox'),
    ], string='Server URL', default='https://platform.ringcentral.com', required=True)
    
    # OAuth tokens (account-level for webhooks and background sync)
    access_token = fields.Text(string='Access Token', readonly=True, 
                               help='OAuth access token for account-level operations (webhooks, call history sync)')
    refresh_token = fields.Text(string='Refresh Token', readonly=True)
    token_expires_at = fields.Datetime(string='Token Expires At', readonly=True)
    
    # Note: User credentials (username/password) removed - widget uses OAuth per user
    # Each user authenticates individually via the embedded widget
    # Extensions are stored per-user in res.users.ringcentral_extension
    
    # Webhook configuration
    webhook_url = fields.Char(string='Webhook URL', readonly=True, compute='_compute_webhook_url')
    webhook_secret = fields.Char(string='Webhook Secret', readonly=True)
    subscription_id = fields.Char(string='Subscription ID', readonly=True, help='RingCentral webhook subscription ID')
    subscription_expires_at = fields.Datetime(string='Subscription Expires At', readonly=True)
    
    # Widget settings removed; widget loads statically via frontend boot script
    
    # Status
    is_connected = fields.Boolean(string='Connected', compute='_compute_is_connected', store=False)
    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    call_history_count = fields.Integer(string='Call Count', compute='_compute_call_history_count')
    
    active = fields.Boolean(string='Active', default=True)
    
    # Status indicator fields
    status_icon = fields.Char(string='Status Icon', compute='_compute_status_icon', store=False)
    status_color = fields.Char(string='Status Color', compute='_compute_status_icon', store=False)
    status_text = fields.Char(string='Status Text', compute='_compute_status_icon', store=False)
    status_html = fields.Html(string='Status HTML', compute='_compute_status_icon', store=False, sanitize=False)

    # Network/proxy settings
    proxy_enabled = fields.Boolean(string='Enable Proxy', default=False, 
                                   help='Enable this if your network requires a proxy server to access RingCentral API')
    http_proxy = fields.Char(string='HTTP Proxy URL', 
                            help='HTTP proxy URL format: http://username:password@proxy.company.com:8080')
    https_proxy = fields.Char(string='HTTPS Proxy URL', 
                              help='HTTPS proxy URL format: https://username:password@proxy.company.com:8080')
    verify_ssl = fields.Boolean(string='Verify SSL Certificates', default=True, 
                               help='Enable SSL certificate verification. Disable only for self-signed certificates (not recommended for production)')

    @api.depends('access_token', 'token_expires_at')
    def _compute_is_connected(self):
        for record in self:
            if record.access_token and record.token_expires_at:
                record.is_connected = fields.Datetime.now() < record.token_expires_at
            else:
                record.is_connected = False

    @api.depends('active', 'is_connected', 'access_token')
    def _compute_status_icon(self):
        """Compute status icon, color, and text based on active and connection status"""
        for record in self:
            if not record.active:
                record.status_icon = 'fa-circle'
                record.status_color = 'text-muted'
                record.status_text = 'Inactive'
                record.status_html = '<i class="fa fa-circle text-muted me-2"></i><span class="text-muted">Inactive</span>'
            elif record.is_connected and record.access_token:
                record.status_icon = 'fa-check-circle'
                record.status_color = 'text-success'
                record.status_text = 'Connected'
                record.status_html = '<i class="fa fa-check-circle text-success me-2"></i><span class="text-success">Connected</span>'
            elif record.access_token:
                record.status_icon = 'fa-exclamation-circle'
                record.status_color = 'text-warning'
                record.status_text = 'Token Expired'
                record.status_html = '<i class="fa fa-exclamation-circle text-warning me-2"></i><span class="text-warning">Token Expired</span>'
            else:
                record.status_icon = 'fa-times-circle'
                record.status_color = 'text-danger'
                record.status_text = 'Not Connected'
                record.status_html = '<i class="fa fa-times-circle text-danger me-2"></i><span class="text-danger">Not Connected</span>'

    def _compute_call_history_count(self):
        for record in self:
            record.call_history_count = self.env['ringcentral.call.history'].search_count([
                ('config_id', '=', record.id)
            ])

    def _compute_webhook_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.webhook_url = f"{base_url}/ringcentral/webhook/{record.id}" if record.id else False

    @api.model
    def get_config(self):
        """Get active RingCentral configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise UserError(_('No active RingCentral configuration found. Please configure RingCentral first.'))
        return config

    @api.model
    def get_systray_status(self):
        """Get status for systray indicator"""
        try:
            config = self.search([('active', '=', True)], limit=1)
            if not config:
                return {
                    'status': None,
                    'icon': 'fa-times-circle',
                    'color': 'text-muted',
                    'text': 'Not Configured',
                }
            # Compute status
            config._compute_status_icon()
            return {
                'status': config.id,
                'icon': config.status_icon,
                'color': config.status_color,
                'text': config.status_text,
            }
        except Exception as e:
            # Safe fallback during upgrade when new columns may not exist yet
            _logger.warning("Systray status fallback due to error: %s", str(e))
            return {
                'status': None,
                'icon': 'fa-exclamation-triangle',
                'color': 'text-warning',
                'text': 'Updating... Please reload',
            }

    def action_test_connection(self):
        """Test DNS and HTTPS reachability of the configured RingCentral server."""
        self.ensure_one()

        # Be resilient during upgrades: read only 'server_url' without prefetching new columns
        try:
            data = self.with_context(prefetch_fields=False).read(['server_url'])[0]
            server_url = data.get('server_url') or ''
        except Exception as e:
            _logger.warning("Test connection failed to read server_url (likely upgrade pending): %s", e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Upgrade Required'),
                    'message': _('Please upgrade the module to apply database changes, then retry Test Connection.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        parsed = urlparse(server_url)
        host = parsed.hostname or server_url

        # Step 1: DNS resolution
        try:
            socket.gethostbyname(host)
            dns_ok = True
        except Exception as e:
            dns_ok = False
            dns_err = str(e)

        # Step 2: HTTPS reachability (best-effort, public endpoint if available)
        https_ok = False
        https_err = ''
        if dns_ok:
            try:
                # Attempt a lightweight GET to the API root which typically answers with metadata
                # If that fails, we still report DNS success but surface HTTPS error
                try:
                    req_kwargs = self._build_request_kwargs()
                except Exception as e:
                    _logger.warning("Using default request kwargs (upgrade pending?): %s", e)
                    req_kwargs = {}
                requests.get(f"{server_url}/restapi/v1.0", timeout=8, **req_kwargs)
                https_ok = True
            except requests.exceptions.RequestException as e:
                https_err = str(e)

        # Build user-friendly message
        if dns_ok and https_ok:
            title = _('Connection OK')
            message = _('Successfully resolved %(host)s and reached %(url)s') % {
                'host': host,
                'url': f"{server_url}/restapi/v1.0",
            }
            notif_type = 'success'
        elif not dns_ok:
            title = _('DNS Resolution Failed')
            message = _('Could not resolve %(host)s. Please check your DNS, VPN/Proxy, or network policy. Error: %(err)s') % {
                'host': host,
                'err': dns_err,
            }
            notif_type = 'danger'
        else:
            title = _('HTTPS Reachability Failed')
            message = _('Resolved %(host)s but could not reach %(url)s. Ensure firewall/proxy allows outbound HTTPS. Error: %(err)s') % {
                'host': host,
                'url': f"{server_url}/restapi/v1.0",
                'err': https_err or _('Unknown error'),
            }
            notif_type = 'warning'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notif_type,
                'sticky': False,
            }
        }

    def authenticate(self):
        """Authenticate with RingCentral using OAuth (Password Grant deprecated)
        
        Note: This method is deprecated. Use OAuth flow via 'Connect (OAuth)' button instead.
        The embedded widget handles user authentication individually via OAuth.
        This method is kept for backward compatibility but redirects to OAuth flow.
        """
        self.ensure_one()
        raise UserError(_(
            'Password Grant authentication is deprecated. Please use OAuth authentication instead.\n\n'
            'Click the "Connect (OAuth)" button to authenticate via OAuth.\n\n'
            'Note: Each user authenticates individually through the embedded widget. '
            'The config stores account-level OAuth tokens for webhooks and background sync.'
        ))

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        self.ensure_one()

        data = self._safe_read(['refresh_token', 'server_url'])
        refresh_token = data.get('refresh_token')
        server_url = data.get('server_url') or self.server_url

        if not refresh_token:
            raise UserError(_('No refresh token available. Please authenticate first.'))

        url = f"{server_url}/restapi/oauth/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self._get_basic_auth()}',
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        
        try:
            req_kwargs = self._build_request_kwargs()
            response = requests.post(url, headers=headers, data=data, timeout=30, **req_kwargs)
            response.raise_for_status()
            result = response.json()
            
            self.write({
                'access_token': result.get('access_token'),
                'refresh_token': result.get('refresh_token', self.refresh_token),
                'token_expires_at': fields.Datetime.now() + timedelta(seconds=result.get('expires_in', 3600)),
            })
            
            return True
        except requests.exceptions.RequestException as e:
            _logger.error(f"RingCentral token refresh error: {str(e)}")
            return False

    def action_connect_oauth(self):
        """Start OAuth Authorization Code flow by redirecting to RingCentral authorize page."""
        self.ensure_one()
        params = self._safe_read(['client_id', 'server_url'])
        client_id = params.get('client_id')
        server_url = params.get('server_url') or self.server_url
        if not client_id:
            raise UserError(_('Please set Client ID before connecting.'))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirect_uri = f"{base_url}/ringcentral/oauth"
        # Build authorize URL
        authorize = (
            f"{server_url}/restapi/oauth/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&prompt=login%20consent"
        )
        return {
            'type': 'ir.actions.act_url',
            'url': authorize,
            'target': 'self',
        }

    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access/refresh token."""
        self.ensure_one()
        data = self._safe_read(['client_id', 'client_secret', 'server_url'])
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        server_url = data.get('server_url') or self.server_url
        if not all([client_id, client_secret]):
            raise UserError(_('Client ID/Secret are required.'))
        url = f"{server_url}/restapi/oauth/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self._get_basic_auth()}',
        }
        form = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
        }
        try:
            req_kwargs = self._build_request_kwargs()
            resp = requests.post(url, headers=headers, data=form, timeout=30, **req_kwargs)
            resp.raise_for_status()
            payload = resp.json()
            self.write({
                'access_token': payload.get('access_token'),
                'refresh_token': payload.get('refresh_token'),
                'token_expires_at': fields.Datetime.now() + timedelta(seconds=payload.get('expires_in', 3600)),
                'last_sync': fields.Datetime.now(),
            })
            # Automatically create webhook subscription after OAuth
            try:
                self.create_webhook_subscription()
            except Exception as e:
                _logger.warning(f"Failed to create webhook subscription after OAuth: {str(e)}")
        except requests.exceptions.RequestException as e:
            _logger.error(f"RingCentral token exchange error: {str(e)}")
            err_text = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    err_desc = e.response.json().get('error_description')
                    if err_desc:
                        err_text = f"{err_text} - {err_desc}"
                except Exception:
                    if e.response.text:
                        err_text = f"{err_text} - {e.response.text}"
            raise UserError(_('Failed to complete OAuth: %s') % err_text)
    def _get_basic_auth(self):
        """Get Basic Auth header value"""
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    def _get_access_token(self):
        """Get valid access token, refresh if needed"""
        self.ensure_one()
        
        if not self.access_token:
            raise UserError(_('Not authenticated. Please authenticate first.'))
        
        # Check if token is expired
        if self.token_expires_at and fields.Datetime.now() >= self.token_expires_at:
            if not self.refresh_access_token():
                raise UserError(_('Token expired and refresh failed. Please authenticate again.'))
        
        return self.access_token

    def _make_api_request(self, method, endpoint, data=None, params=None):
        """Make API request to RingCentral"""
        self.ensure_one()
        
        access_token = self._get_access_token()
        url = f"{self.server_url}/restapi/v1.0{endpoint}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        try:
            req_kwargs = self._build_request_kwargs()
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30, **req_kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30, **req_kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30, **req_kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30, **req_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            _logger.error(f"RingCentral API request error: {str(e)}")
            if hasattr(e.response, 'text'):
                _logger.error(f"Response: {e.response.text}")
            raise UserError(_('RingCentral API request failed: %s') % str(e))

    def _build_request_kwargs(self):
        """Build common kwargs for requests respecting proxy and SSL settings."""
        try:
            data = self._safe_read(['proxy_enabled', 'http_proxy', 'https_proxy', 'verify_ssl'])
            proxy_enabled = data.get('proxy_enabled') or False
            http_proxy = data.get('http_proxy')
            https_proxy = data.get('https_proxy')
            verify_ssl = data.get('verify_ssl', True)
        except Exception as e:
            _logger.warning("Request kwargs fallback (upgrade pending?): %s", e)
            proxy_enabled = False
            http_proxy = None
            https_proxy = None
            verify_ssl = True

        proxies = None
        if proxy_enabled and (http_proxy or https_proxy):
            proxies = {}
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
        return {
            'proxies': proxies,
            'verify': verify_ssl,
        }

    def _safe_read(self, field_names):
        """Safely read fields without triggering full prefetch during upgrades."""
        vals = self.with_context(prefetch_fields=False).read(field_names)
        return vals and vals[0] or {}

    def make_call(self, to_number, from_number=None, user_id=None):
        """Make an outbound call
        
        Args:
            to_number: Phone number to call
            from_number: Phone number to call from (defaults to config username)
            user_id: User making the call (for extension and tracking)
        """
        self.ensure_one()
        
        # Get user extension if user is provided
        extension = None
        if user_id:
            user = self.env['res.users'].browse(user_id)
            if user.exists():
                extension = user.get_ringcentral_extension()
        
        # Always use the authenticated user's extension ("~") to avoid 404 on unknown extension ids/numbers
        # If you need to dial as a specific extension, authenticate with that extension or implement
        # an extension lookup to translate extension numbers to internal ids before calling RingOut.
        endpoint = '/account/~/extension/~/ringout'
        
        data = {
            'to': {'phoneNumber': to_number},
            'from': {'phoneNumber': from_number},
        }
        
        result = self._make_api_request('POST', endpoint, data=data)
        
        # Create call history record
        self.env['ringcentral.call.history'].create({
            'config_id': self.id,
            'user_id': user_id or self.env.user.id,
            'direction': 'outbound',
                'from_number': from_number,
            'to_number': to_number,
            'status': 'initiated',
            'ringcentral_call_id': result.get('id'),
        })
        
        return result

    def get_call_logs(self, date_from=None, date_to=None, limit=100, user_id=None):
        """Get call logs from RingCentral
        
        Args:
            date_from: Start date for filtering
            date_to: End date for filtering
            limit: Maximum number of records
            user_id: User ID to get logs for (uses user's extension)
        """
        self.ensure_one()
        
        # Get user extension if user is provided
        extension = None
        if user_id:
            user = self.env['res.users'].browse(user_id)
            if user.exists():
                extension = user.get_ringcentral_extension()
        
        # Use extension in endpoint if available, otherwise use default
        if extension:
            endpoint = f'/account/~/extension/{extension}/call-log'
        else:
            endpoint = '/account/~/extension/~/call-log'
        
        params = {
            'perPage': limit,
        }
        
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        
        return self._make_api_request('GET', endpoint, params=params)

    def get_call_recording(self, recording_id):
        """Get call recording content"""
        self.ensure_one()
        
        endpoint = f'/account/~/recording/{recording_id}/content'
        return self._make_api_request('GET', endpoint)

    # Removed _schedule_async_sync() - Odoo 19 best practice:
    # Webhooks should return immediately without creating dynamic cron jobs
    # Use predefined scheduled actions (ir.cron) defined in XML data files instead

    def _safe_update_last_sync(self, config):
        """Update last_sync field with retry logic for concurrent updates"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Lock the record to prevent concurrent updates
                config.with_for_update().write({'last_sync': fields.Datetime.now()})
                return
            except Exception as e:
                # Check if it's a serialization/concurrency error
                if isinstance(e, PG_SERIALIZATION_ERRORS) or 'serialize' in str(e).lower() or 'concurrent' in str(e).lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff: wait random time before retry
                        wait_time = random.uniform(0.1, 0.5 * (2 ** attempt))
                        time.sleep(wait_time)
                        continue
                # If not a concurrency error or max retries reached, log and re-raise
                _logger.warning(f"Failed to update last_sync for config {config.id} after {attempt + 1} attempts: {str(e)}")
                # Don't fail the entire sync if we can't update last_sync
                return

    def sync_call_history_recent(self):
        """Lightweight sync - only recent calls (last 24 hours) for webhook triggers
        Can be called on multiple configs (for shared cron)"""
        try:
            for config in self:
                if not config.active or not config.access_token:
                    continue
                    
                try:
                    # Only sync recent calls (last 24 hours) to avoid timeout
                    from_date = (fields.Datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
                    call_logs = config.get_call_logs(limit=100, date_from=from_date)
                    records = call_logs.get('records', [])
                    
                    created_count = 0
                    updated_count = 0
                    
                    for record in records:
                        call_id = record.get('id')
                        existing = config.env['ringcentral.call.history'].search([
                            ('ringcentral_call_id', '=', call_id)
                        ], limit=1)
                        
                        # Parse start time (ISO 8601) to naive UTC datetime
                        start_time_val = record.get('startTime')
                        start_time = False
                        if isinstance(start_time_val, str) and start_time_val:
                            try:
                                dt = datetime.fromisoformat(start_time_val.replace('Z', '+00:00'))
                                start_time = dt.astimezone(timezone.utc).replace(tzinfo=None)
                            except Exception:
                                start_time = False

                        # Normalize direction and status
                        raw_direction = (record.get('direction') or '').lower()
                        direction = 'inbound' if raw_direction.startswith('in') else 'outbound' if raw_direction.startswith('out') else 'unknown'
                        raw_result = (record.get('result') or '').lower()
                        if raw_result in ('completed',):
                            status = 'completed'
                        elif raw_result in ('missed', 'noanswer', 'no answer', 'cancelled', 'canceled'):
                            status = 'no-answer'
                        elif raw_result in ('busy',):
                            status = 'busy'
                        elif raw_result in ('failed', 'error'):
                            status = 'failed'
                        elif raw_result in ('answered', 'connected'):
                            status = 'answered'
                        else:
                            status = 'unknown'

                        vals = {
                            'config_id': config.id,
                            'ringcentral_call_id': call_id,
                            'direction': direction,
                            'from_number': record.get('from', {}).get('phoneNumber', ''),
                            'to_number': record.get('to', {}).get('phoneNumber', ''),
                            'start_time': start_time,
                            'duration': record.get('duration', 0),
                            'status': status,
                            'recording_id': record.get('recording', {}).get('id') if record.get('recording') else False,
                        }
                        
                        if existing:
                            existing.write(vals)
                            updated_count += 1
                        else:
                            config.env['ringcentral.call.history'].create(vals)
                            created_count += 1
                            # Auto-link partner for new records
                            new_record = config.env['ringcentral.call.history'].search([
                                ('ringcentral_call_id', '=', call_id)
                            ], limit=1)
                            if new_record:
                                new_record._auto_link_partner()
                    
                    # Update last_sync with retry logic for concurrent updates
                    self._safe_update_last_sync(config)
                except Exception as e:
                    _logger.error(f"Error in recent sync for config {config.id}: {str(e)}", exc_info=True)
        except Exception as e:
            _logger.error(f"Error in recent sync: {str(e)}", exc_info=True)

    def sync_call_history(self):
        """Sync call history from RingCentral (full sync)"""
        self.ensure_one()
        
        call_logs = self.get_call_logs(limit=1000)
        records = call_logs.get('records', [])
        
        created_count = 0
        updated_count = 0
        
        for record in records:
            call_id = record.get('id')
            existing = self.env['ringcentral.call.history'].search([
                ('ringcentral_call_id', '=', call_id)
            ], limit=1)
            
            # Parse start time (ISO 8601) to naive UTC datetime
            start_time_val = record.get('startTime')
            start_time = False
            if isinstance(start_time_val, str) and start_time_val:
                try:
                    # Example: '2025-11-11T10:37:29.972Z'
                    dt = datetime.fromisoformat(start_time_val.replace('Z', '+00:00'))
                    start_time = dt.astimezone(timezone.utc).replace(tzinfo=None)
                except Exception:
                    start_time = False

            # Normalize direction to selection values
            raw_direction = (record.get('direction') or '').lower()
            direction = 'inbound' if raw_direction.startswith('in') else 'outbound' if raw_direction.startswith('out') else 'unknown'
            # Normalize status to our selection when possible
            raw_result = (record.get('result') or '').lower()
            if raw_result in ('completed',):
                status = 'completed'
            elif raw_result in ('missed', 'noanswer', 'no answer', 'cancelled', 'canceled'):
                status = 'no-answer'
            elif raw_result in ('busy',):
                status = 'busy'
            elif raw_result in ('failed', 'error'):
                status = 'failed'
            elif raw_result in ('answered', 'connected'):
                status = 'answered'
            else:
                status = 'unknown'

            vals = {
                'config_id': self.id,
                'ringcentral_call_id': call_id,
                'direction': direction,
                'from_number': record.get('from', {}).get('phoneNumber', ''),
                'to_number': record.get('to', {}).get('phoneNumber', ''),
                'start_time': start_time,
                'duration': record.get('duration', 0),
                'status': status,
                'recording_id': record.get('recording', {}).get('id') if record.get('recording') else False,
            }
            
            if existing:
                existing.write(vals)
                updated_count += 1
            else:
                self.env['ringcentral.call.history'].create(vals)
                created_count += 1
        
        # Update last_sync with retry logic for concurrent updates
        self._safe_update_last_sync(self)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Complete'),
                'message': _('Created: %d, Updated: %d') % (created_count, updated_count),
                'type': 'success',
                'sticky': False,
            }
        }

    def create_webhook_subscription(self):
        """Create or update webhook subscription using RingCentral Subscription API"""
        self.ensure_one()
        
        if not self.access_token:
            raise UserError(_('Not authenticated. Please authenticate first.'))
        
        # Get webhook URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        webhook_url = f"{base_url}/ringcentral/webhook/{self.id}"
        
        # Event filters: Use only presence (supported for subscriptions).
        # We'll pull call-log/recordings/transcripts on presence updates.
        event_filters = [
            '/restapi/v1.0/account/~/extension/~/presence?detailedTelephonyState=true&sipData=true',
        ]
        
        # Subscription payload
        subscription_data = {
            'eventFilters': event_filters,
            'deliveryMode': {
                'transportType': 'WebHook',
                'address': webhook_url,
            },
            'expiresIn': 630720000,  # 20 years in seconds (max allowed)
        }
        
        try:
            # If subscription exists, renew it; otherwise create new
            if self.subscription_id:
                endpoint = f'/subscription/{self.subscription_id}'
                method = 'PUT'
            else:
                endpoint = '/subscription'
                method = 'POST'
            
            result = self._make_api_request(method, endpoint, data=subscription_data)
            
            # Save subscription details
            self.write({
                'subscription_id': result.get('id'),
                'subscription_expires_at': fields.Datetime.now() + timedelta(seconds=result.get('expiresIn', 630720000)),
            })
            
            # Webhook subscription created/renewed
            
            # Return notification when called from UI button
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Webhook subscription %s successfully.') % ('created' if method == 'POST' else 'updated'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Failed to create webhook subscription: {str(e)}")
            raise UserError(_('Failed to create webhook subscription: %s') % str(e))
    
    def renew_webhook_subscription(self):
        """Renew existing webhook subscription"""
        self.ensure_one()
        
        if not self.subscription_id:
            # Create new subscription if none exists
            return self.create_webhook_subscription()
        
        try:
            self.create_webhook_subscription()  # This will update if subscription_id exists
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Webhook subscription renewed successfully.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error(f"Failed to renew webhook subscription: {str(e)}")
            raise UserError(_('Failed to renew webhook subscription: %s') % str(e))
    
    def delete_webhook_subscription(self):
        """Delete webhook subscription"""
        self.ensure_one()
        
        if not self.subscription_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('No subscription to delete.'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        try:
            endpoint = f'/subscription/{self.subscription_id}'
            self._make_api_request('DELETE', endpoint)
            
            self.write({
                'subscription_id': False,
                'subscription_expires_at': False,
            })
            
            # Webhook subscription deleted
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Webhook subscription deleted successfully.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Failed to delete webhook subscription: {str(e)}")
            raise UserError(_('Failed to delete webhook subscription: %s') % str(e))
    
    def action_view_call_history(self):
        """View call history for this configuration"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Call History'),
            'res_model': 'ringcentral.call.history',
            'domain': [('config_id', '=', self.id)],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def write(self, vals):
        """Override write to handle subscription deletion on deactivation"""
        # Check if active is being set to False
        if 'active' in vals and not vals['active']:
            for record in self:
                if record.active and record.subscription_id:
                    # Delete subscription when deactivating
                    record.delete_webhook_subscription()
        
        # Check if active is being set to True and subscription doesn't exist
        if 'active' in vals and vals['active']:
            for record in self:
                if not record.active and record.access_token and not record.subscription_id:
                    # Try to create subscription when reactivating
                    try:
                        record.create_webhook_subscription()
                    except Exception as e:
                        _logger.warning(f"Failed to create subscription on reactivation: {str(e)}")
        
        return super().write(vals)
    
    @api.constrains('client_id', 'client_secret')
    def _check_credentials(self):
        for record in self:
            if record.active and (not record.client_id or not record.client_secret):
                raise ValidationError(_('Client ID and Client Secret are required for active configuration.'))

    @api.model
    def cron_maintain_tokens_and_subscription(self):
        """Scheduled task: auto-refresh token and auto-renew subscription for active configs.
        
        - If token expires within 10 minutes, refresh it.
        - If subscription missing, create it.
        - If subscription expires within 1 day, renew it.
        """
        configs = self.search([('active', '=', True)])
        now = fields.Datetime.now()
        for cfg in configs:
            try:
                # Refresh token if expiring soon
                if cfg.token_expires_at:
                    delta = cfg.token_expires_at - now
                    if delta.total_seconds() <= 600:  # 10 minutes
                        cfg.refresh_access_token()
                # Ensure subscription exists
                if not cfg.subscription_id:
                    # Avoid UI notifications in cron
                    cfg.with_context(return_notification=False).create_webhook_subscription()
                else:
                    # Renew if expiring soon
                    if cfg.subscription_expires_at:
                        sub_delta = cfg.subscription_expires_at - now
                        if sub_delta.total_seconds() <= 24 * 3600:  # 1 day
                            cfg.renew_webhook_subscription()
            except Exception as e:
                _logger.warning("Maintenance failed for config %s: %s", cfg.id, str(e))
        return True

