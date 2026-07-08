# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime
from datetime import timedelta, datetime, timezone
from urllib.parse import quote, urlparse, urlsplit, urlunsplit, parse_qsl, urlencode
import socket
import requests
import json
import logging
import random
import time
import base64
import secrets

_logger = logging.getLogger(__name__)

try:
    from psycopg2 import errors as psycopg2_errors
    PG_SERIALIZATION_ERRORS = (psycopg2_errors.SerializationFailure,)
except ImportError:
    PG_SERIALIZATION_ERRORS = ()

RATE_LIMIT_BACKOFF_MINUTES = 15
CRON_SYNC_MIN_INTERVAL_MINUTES = 25
# RingCentral WebHook transport max lifetime (10 years per Subscription API).
WEBHOOK_MAX_EXPIRES_IN = 315360000
RC_FILTER_PRESENCE = (
    '/restapi/v1.0/account/~/extension/~/presence'
    '?detailedTelephonyState=true&sipData=true'
)
RC_FILTER_ACCOUNT_TELEPHONY = '/restapi/v1.0/account/~/telephony/sessions'
RC_FILTER_EXTENSION_TELEPHONY = '/restapi/v1.0/account/~/extension/~/telephony/sessions'


class RingCentralRateLimitError(Exception):
    """RingCentral API rate limit (CMN-301 / HTTP 429)."""


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
    oauth_redirect_uri = fields.Char(
        string='OAuth Redirect URI',
        help='Optional. Must match your RingCentral app redirect URI exactly '
             '(e.g. https://your-domain.ngrok-free.dev/ringcentral/oauth). '
             'Leave empty to auto-detect from your public Odoo URL.',
    )
    oauth_redirect_uri_effective = fields.Char(
        string='Effective OAuth Redirect URI',
        compute='_compute_oauth_redirect_uri_effective',
        help='Register this URL in the RingCentral Developer Portal.',
    )
    webhook_secret = fields.Char(string='Webhook Secret', readonly=True)
    subscription_id = fields.Char(string='Subscription ID', readonly=True, help='RingCentral webhook subscription ID')
    subscription_expires_at = fields.Datetime(string='Subscription Expires At', readonly=True)
    
    # Widget settings removed; widget loads statically via frontend boot script
    
    # Status
    is_connected = fields.Boolean(string='Connected', compute='_compute_is_connected', store=False)
    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    last_contact_sync = fields.Datetime(string='Last Contact Sync', readonly=True)
    contact_sync_overwrite = fields.Boolean(
        string='Overwrite Existing Contact Fields',
        default=False,
        help='When enabled, RingCentral values overwrite existing Odoo contact and lead field values. '
             'When disabled, only empty fields are updated.',
    )
    push_contacts_to_ringcentral = fields.Boolean(
        string='Create/Update Contact To RingCentral',
        default=False,
        help='When enabled, Odoo contacts linked to this configuration are pushed to this '
             'RingCentral personal address book on save.',
    )
    api_rate_limit_until = fields.Datetime(
        string='API Rate Limit Until',
        readonly=True,
        help='Backoff timestamp after RingCentral CMN-301 rate limit responses.',
    )
    call_history_count = fields.Integer(string='Call Count', compute='_compute_call_history_count')
    
    active = fields.Boolean(string='Active', default=True)
    company_ids = fields.Many2many(
        'res.company',
        'ringcentral_config_company_rel',
        'config_id',
        'company_id',
        string='Companies',
        default=lambda self: self.env.company,
        help='Odoo companies served by this configuration. Leave empty to apply to all companies. '
             'Multiple active configurations may share the same company.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Primary Company',
        compute='_compute_company_id',
        store=True,
        index=True,
        tracking=True,
        help='First company in the Companies list (backward compatibility helper).',
    )
    
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

    @api.depends('company_ids')
    def _compute_company_id(self):
        for record in self:
            record.company_id = record.company_ids[:1].id if record.company_ids else False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('company_ids') and self.env.company:
                vals['company_ids'] = [(6, 0, [self.env.company.id])]
        return super().create(vals_list)

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
        for record in self:
            if not record.id:
                record.webhook_url = False
                continue
            base = record._get_public_base_url()
            record.webhook_url = f"{base}/ringcentral/webhook/{record.id}" if base else False

    @api.depends('oauth_redirect_uri')
    def _compute_oauth_redirect_uri_effective(self):
        for record in self:
            try:
                record.oauth_redirect_uri_effective = record._get_oauth_redirect_uri()
            except UserError:
                record.oauth_redirect_uri_effective = False

    @api.model
    def _normalize_public_base_url(self, base_url):
        """Force HTTPS for tunnel hosts (ngrok, etc.) when Odoo sees HTTP internally."""
        base_url = (base_url or '').strip().rstrip('/')
        if not base_url:
            return ''
        parsed = urlparse(base_url)
        host = (parsed.hostname or '').lower()
        scheme = parsed.scheme or 'https'
        if host and (
            'ngrok' in host
            or host.endswith('.loca.lt')
            or host.endswith('.trycloudflare.com')
        ):
            scheme = 'https'
        elif scheme == 'http' and host and not host.startswith('localhost') and host != '127.0.0.1':
            # Public deployments behind TLS terminators often report http locally.
            scheme = 'https'
        port = parsed.port
        netloc = parsed.hostname or ''
        if port and not ((scheme == 'https' and port == 443) or (scheme == 'http' and port == 80)):
            netloc = f"{netloc}:{port}"
        return f"{scheme}://{netloc}"

    @api.model
    def _public_base_url_from_request(self, httprequest):
        """Build base URL from the incoming HTTP request (proxy/ngrok aware)."""
        if not httprequest:
            return ''
        headers = httprequest.headers
        host = (
            headers.get('X-Forwarded-Host')
            or headers.get('Host')
            or getattr(httprequest, 'host', '')
            or ''
        )
        host = host.split(',')[0].strip()
        if not host:
            return ''
        proto = (
            headers.get('X-Forwarded-Proto')
            or httprequest.environ.get('HTTP_X_FORWARDED_PROTO')
            or httprequest.environ.get('wsgi.url_scheme')
            or getattr(httprequest, 'scheme', 'https')
        )
        proto = (proto or 'https').split(',')[0].strip()
        return self._normalize_public_base_url(f"{proto}://{host}")

    def _get_public_base_url(self):
        """Public base URL for OAuth callbacks and webhooks."""
        from odoo.http import request
        if request and getattr(request, 'httprequest', None):
            base = self._public_base_url_from_request(request.httprequest)
            if base:
                return base
        icp_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        return self._normalize_public_base_url(icp_base)

    def _get_oauth_redirect_uri(self):
        """Return the OAuth redirect URI used for authorize + token exchange."""
        self.ensure_one()
        override = (self.oauth_redirect_uri or '').strip().rstrip('/')
        if override:
            return override
        base = self._get_public_base_url()
        if not base:
            raise UserError(_(
                'Cannot determine OAuth redirect URI. Set "OAuth Redirect URI" on the '
                'RingCentral configuration or update System Parameter web.base.url to your '
                'public HTTPS URL (e.g. https://your-domain.ngrok-free.dev).'
            ))
        return f"{base}/ringcentral/oauth"

    def _resolve_oauth_return_url(self):
        """Determine where to send the user after OAuth completes."""
        return_url = self.env.context.get('ringcentral_oauth_return_url')
        from odoo.http import request
        if not return_url and request and getattr(request, 'httprequest', None):
            return_url = request.httprequest.referrer
        if not return_url or '/ringcentral/oauth' in (return_url or ''):
            action = self.env.ref('ringcentral_integration.action_ringcentral_config', raise_if_not_found=False)
            if action:
                return_url = f'/web#action={action.id}&model=ringcentral.config&id={self.id}&view_type=form'
            else:
                return_url = '/web'
        return return_url

    @api.model
    def _encode_oauth_state(self, payload):
        raw = json.dumps(payload, separators=(',', ':')).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip('=')

    @api.model
    def _decode_oauth_state(self, state):
        if not state:
            return {}
        try:
            padding = '=' * (-len(state) % 4)
            raw = base64.urlsafe_b64decode(state + padding)
            return json.loads(raw.decode())
        except Exception:
            _logger.warning('Invalid RingCentral OAuth state payload')
            return {}

    @api.model
    def _append_query_param(self, url, key, value):
        parts = urlsplit(url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query[key] = value
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

    def _store_oauth_context(self, redirect_uri, return_url):
        """Persist OAuth callback context in session and return encoded state."""
        csrf_token = secrets.token_urlsafe(16)
        from odoo.http import request
        if request and getattr(request, 'session', None) is not None:
            request.session['ringcentral_oauth_redirect_uri'] = redirect_uri
            request.session['ringcentral_oauth_config_id'] = self.id
            request.session['ringcentral_oauth_return_url'] = return_url
            request.session['ringcentral_oauth_csrf'] = csrf_token
        return self._encode_oauth_state({
            'config_id': self.id,
            'return_url': return_url,
            'csrf': csrf_token,
        })

    @api.model
    def _pop_oauth_context(self):
        """Read OAuth context stored when authorization started."""
        from odoo.http import request
        if not request or not getattr(request, 'session', None):
            return None, None, None
        redirect_uri = request.session.pop('ringcentral_oauth_redirect_uri', None)
        config_id = request.session.pop('ringcentral_oauth_config_id', None)
        return_url = request.session.pop('ringcentral_oauth_return_url', None)
        request.session.pop('ringcentral_oauth_csrf', None)
        return redirect_uri, config_id, return_url

    @api.model
    def _pop_oauth_redirect_uri_session(self):
        """Backward-compatible helper for legacy session keys."""
        redirect_uri, config_id, _return_url = self._pop_oauth_context()
        return redirect_uri, config_id

    @api.model
    def _build_oauth_success_redirect(self, return_url):
        """Build redirect URL with success query parameter."""
        return_url = return_url or '/web'
        return self._append_query_param(return_url, 'ringcentral_status', 'success')

    @api.model
    def _build_oauth_error_redirect(self, return_url, message):
        return_url = return_url or '/web'
        url = self._append_query_param(return_url, 'ringcentral_status', 'error')
        return self._append_query_param(url, 'ringcentral_message', quote(message or 'OAuth failed', safe=''))

    def _store_oauth_redirect_uri_session(self, redirect_uri):
        """Legacy wrapper."""
        return_url = self._resolve_oauth_return_url()
        return self._store_oauth_context(redirect_uri, return_url)

    @api.model
    def _config_sort_key(self, cfg, company):
        if not cfg.company_ids:
            return (1, 0, cfg.id)
        if company in cfg.company_ids:
            return (0, len(cfg.company_ids), cfg.id)
        return (2, 0, cfg.id)

    @api.model
    def _get_company_configs(self, company=None):
        """Return all active RingCentral configurations for a company."""
        company = company or self.env.company
        domain = [
            ('active', '=', True),
            '|',
            ('company_ids', '=', False),
            ('company_ids', 'in', company.id),
        ]
        configs = self.search(domain)
        return configs.sorted(key=lambda cfg: self._config_sort_key(cfg, company))

    @api.model
    def _get_company_active_config(self, company=None, raise_if_missing=False):
        company = company or self.env.company
        configs = self._get_company_configs(company)
        config = configs[:1]
        if not config and raise_if_missing:
            raise UserError(
                _('No active RingCentral configuration found for company %s.')
                % company.display_name
            )
        return config

    @api.model
    def get_config(self):
        """Get active RingCentral configuration for the current company."""
        return self._get_company_active_config(raise_if_missing=True)

    @api.model
    def get_systray_status(self):
        """Get status for systray indicator"""
        try:
            config = self._get_company_active_config()
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
        if self._is_api_rate_limited():
            _logger.warning(
                'Skipping token refresh for config %s during API backoff',
                self.id,
            )
            return False

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
        redirect_uri = self._get_oauth_redirect_uri()
        return_url = self._resolve_oauth_return_url()
        state = self._store_oauth_context(redirect_uri, return_url)
        authorize = (
            f"{server_url}/restapi/oauth/authorize"
            f"?response_type=code"
            f"&client_id={quote(client_id, safe='')}"
            f"&redirect_uri={quote(redirect_uri, safe='')}"
            f"&state={quote(state, safe='')}"
            f"&prompt=login%20consent"
        )
        _logger.info('RingCentral OAuth authorize redirect_uri=%s return_url=%s', redirect_uri, return_url)
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
            if not self.subscription_id:
                try:
                    self.create_webhook_subscription()
                except Exception as e:
                    _logger.warning("Failed to create webhook subscription after OAuth: %s", str(e))
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

    def _is_api_rate_limited(self):
        """True when we are in a post-CMN-301 backoff window."""
        self.ensure_one()
        if not self.api_rate_limit_until:
            return False
        return fields.Datetime.now() < self.api_rate_limit_until

    def _mark_rate_limited(self, retry_after_seconds=None):
        """Record backoff window after a rate-limit response."""
        self.ensure_one()
        minutes = RATE_LIMIT_BACKOFF_MINUTES
        if retry_after_seconds:
            minutes = max(minutes, int(retry_after_seconds / 60) + 1)
        until = fields.Datetime.now() + timedelta(minutes=minutes)
        self.sudo().write({'api_rate_limit_until': until})
        _logger.warning(
            'RingCentral rate limit for config %s; pausing API calls until %s',
            self.id, until,
        )

    def _raise_if_rate_limited(self):
        if self._is_api_rate_limited():
            raise RingCentralRateLimitError(
                f'RingCentral API backoff active until {self.api_rate_limit_until}'
            )

    def _raise_user_friendly_rate_limit(self):
        """Raise a user-facing validation error during API backoff."""
        self.ensure_one()
        if self._is_api_rate_limited():
            until = format_datetime(self.env, self.api_rate_limit_until)
            raise UserError(_(
                'RingCentral API rate limit is active. Please wait until %(until)s '
                'before retrying subscription sync or call history sync.'
            ) % {'until': until})

    def _handle_rate_limit_error(self, error):
        if isinstance(error, RingCentralRateLimitError):
            self._raise_user_friendly_rate_limit()
        raise error

    @staticmethod
    def _response_is_rate_limited(response):
        if response is not None and response.status_code == 429:
            return True
        try:
            payload = response.json() if response is not None and response.content else {}
        except Exception:
            payload = {}
        error_code = str(payload.get('errorCode', ''))
        message = str(payload.get('message', '')).lower()
        return error_code == 'CMN-301' or 'rate exceeded' in message or 'rate limit' in message

    def _make_api_request(self, method, endpoint, data=None, params=None, parse_json=True):
        """Make API request to RingCentral.

        Set parse_json=False for binary endpoints (e.g. recording content).
        """
        self.ensure_one()
        self._raise_if_rate_limited()

        access_token = self._get_access_token()
        url = f"{self.server_url}/restapi/v1.0{endpoint}"
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        if parse_json:
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json'
        else:
            headers['Accept'] = 'audio/*, application/octet-stream, */*'
        
        try:
            req_kwargs = self._build_request_kwargs()
            timeout = 120 if not parse_json else 30
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout, **req_kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=timeout, **req_kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=timeout, **req_kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout, **req_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if self._response_is_rate_limited(response):
                retry_after = response.headers.get('Retry-After')
                retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
                self._mark_rate_limited(retry_seconds)
                raise RingCentralRateLimitError('RingCentral request rate exceeded')

            response.raise_for_status()
            if not parse_json:
                return response
            if not response.content:
                return {}
            try:
                return response.json()
            except ValueError as error:
                content_type = response.headers.get('Content-Type', '')
                preview = (response.text or '')[:200]
                _logger.error(
                    'RingCentral API returned non-JSON response for %s %s (content-type=%s): %s',
                    method, endpoint, content_type, preview,
                )
                raise UserError(
                    _('RingCentral API returned an unexpected response (not JSON).')
                ) from error
        except RingCentralRateLimitError:
            raise
        except requests.exceptions.HTTPError as e:
            if e.response is not None and self._response_is_rate_limited(e.response):
                retry_after = e.response.headers.get('Retry-After')
                retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
                self._mark_rate_limited(retry_seconds)
                raise RingCentralRateLimitError('RingCentral request rate exceeded') from e
            _logger.error("RingCentral API request error: %s", str(e))
            if e.response is not None and e.response.text:
                _logger.error("Response: %s", e.response.text)
                try:
                    err_body = e.response.json()
                    err_msg = (
                        err_body.get('message')
                        or err_body.get('error_description')
                        or err_body.get('errors')
                        or e.response.text
                    )
                except Exception:
                    err_msg = e.response.text
                raise UserError(_('RingCentral API request failed: %s') % err_msg) from e
            raise UserError(_('RingCentral API request failed: %s') % str(e)) from e
        except requests.exceptions.RequestException as e:
            _logger.error("RingCentral API request error: %s", str(e))
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

        CallHistory = self.env['ringcentral.call.history']
        user = user_id or self.env.user.id
        pending = CallHistory._find_pending_outbound_merge(self, to_number, False)
        if pending:
            if not pending.initiated_by_id:
                pending.write({'initiated_by_id': user})
        else:
            CallHistory.with_context(rc_allow_direction_update=True).create({
                'config_id': self.id,
                'initiated_by_id': user,
                'direction': 'outbound',
                'from_number': from_number or 'unknown',
                'to_number': to_number,
                'status': 'initiated',
                'start_time': fields.Datetime.now(),
            })

        return result

    def get_call_logs(self, date_from=None, date_to=None, limit=100, user_id=None,
                      session_id=None, view='Detailed'):
        """Get call logs from RingCentral
        
        Args:
            date_from: Start date for filtering
            date_to: End date for filtering
            limit: Maximum number of records
            user_id: User ID to get logs for (uses user's extension)
            session_id: Filter by RingCentral sessionId
            view: Call log view (Detailed includes recording metadata)
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
            'view': view,
        }
        
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if session_id:
            params['sessionId'] = session_id

        return self._make_api_request('GET', endpoint, params=params)

    def _sync_call_log_records(self, records, update_existing=True):
        """Apply call-log records using shared matching logic (sessionId-aware)."""
        self.ensure_one()
        CallHistory = self.env['ringcentral.call.history']
        created_count = 0
        updated_count = 0
        skipped_count = 0
        for record in records:
            action, _history = CallHistory.sync_from_call_log_record(
                self, record, update_existing=update_existing,
            )
            if action == 'created':
                created_count += 1
            elif action == 'updated':
                updated_count += 1
            elif action == 'skipped':
                skipped_count += 1
        return created_count, updated_count, skipped_count

    def fetch_recording_content(self, recording_id):
        """Fetch raw recording bytes and content type from RingCentral."""
        self.ensure_one()
        response = self._make_api_request(
            'GET',
            f'/account/~/recording/{recording_id}/content',
            parse_json=False,
        )
        content_type = response.headers.get('Content-Type', 'audio/mpeg')
        if content_type and 'json' in content_type.lower():
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            message = payload.get('message') or payload.get('error_description') or _('Recording unavailable')
            raise UserError(_('RingCentral recording error: %s') % message)
        return response.content, content_type

    def lookup_recording_id_for_session(self, session_id):
        """Resolve a recording ID from the call-log API for a session."""
        self.ensure_one()
        if not session_id:
            return False
        try:
            result = self.get_call_logs(session_id=str(session_id), limit=5, view='Detailed')
        except UserError as error:
            _logger.warning(
                'Could not fetch call log for session %s: %s',
                session_id, error,
            )
            return False
        for record in result.get('records') or []:
            recording = record.get('recording') or {}
            rec_id = recording.get('id')
            if rec_id:
                return str(rec_id)
        return False

    def get_call_recording(self, recording_id):
        """Backward-compatible alias — returns recording bytes."""
        content, _content_type = self.fetch_recording_content(recording_id)
        return content

    def _make_ai_api_request(self, method, path, data=None, params=None, allow_404=False):
        """Make API request to RingCentral AI endpoints (RingSense, Speech-to-Text).
        AI APIs use base path /ai/... (not /restapi/v1.0/...).
        If allow_404=True, returns None on 404 instead of raising."""
        self.ensure_one()
        access_token = self._get_access_token()
        server_url = self.server_url or 'https://platform.ringcentral.com'
        url = f"{server_url}{path}" if path.startswith('/') else f"{server_url}/{path}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        try:
            req_kwargs = self._build_request_kwargs()
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=60, **req_kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=60, **req_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            if allow_404 and response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            if allow_404 and e.response is not None and e.response.status_code == 404:
                return None
            _logger.error(f"RingCentral AI API request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    err_body = e.response.json()
                    err_msg = err_body.get('message') or err_body.get('error_description') or str(e)
                except Exception:
                    err_msg = e.response.text or str(e)
                raise UserError(_('RingCentral AI API failed: %s') % err_msg)
            raise UserError(_('RingCentral AI API failed: %s') % str(e))
        except requests.exceptions.RequestException as e:
            _logger.error(f"RingCentral AI API request error: {str(e)}")
            raise UserError(_('RingCentral API request failed: %s') % str(e))

    def _fetch_ringsense_insights(self, recording_id):
        """Fetch RingSense insights for a recording. Returns dict with insights or None on 404/403/no license."""
        self.ensure_one()
        path = f"/ai/ringsense/v1/public/accounts/~/domains/pbx/records/{recording_id}/insights"
        try:
            result = self._make_ai_api_request('GET', path, allow_404=True)
            return result
        except UserError as e:
            err_str = str(e)
            if '403' in err_str or 'Forbidden' in err_str or 'permission' in err_str.lower():
                _logger.warning(
                    "RingSense not available for recording %s (403/forbidden). Falling back to Speech-to-Text. %s",
                    recording_id, err_str
                )
                return None
            _logger.warning("RingSense request failed for recording %s: %s", recording_id, err_str)
            raise

    def _request_speech_to_text(self, recording_id):
        """Start async speech-to-text transcription for a recording. Returns jobId."""
        self.ensure_one()
        server_url = self.server_url or 'https://platform.ringcentral.com'
        content_uri = f"{server_url}/restapi/v1.0/account/~/recording/{recording_id}/content"
        path = "/ai/audio/v1/async/speech-to-text"
        data = {
            "contentUri": content_uri,
            "encoding": "Mpeg",
            "languageCode": "en-US",
            "enablePunctuation": True,
        }
        result = self._make_ai_api_request('POST', path, data=data)
        job_id = result.get('jobId')
        if not job_id:
            raise UserError(_('Speech-to-text API did not return a job ID.'))
        return job_id

    def _get_speech_to_text_result(self, job_id):
        """Get speech-to-text job result. Returns dict with status and response."""
        self.ensure_one()
        path = f"/ai/audio/v1/async/speech-to-text/{job_id}"
        return self._make_ai_api_request('GET', path)

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

    def _should_skip_cron_sync(self):
        """Avoid hammering call-log API; webhooks handle live call updates."""
        self.ensure_one()
        if self._is_api_rate_limited():
            return True
        if self.last_sync:
            elapsed = fields.Datetime.now() - self.last_sync
            if elapsed < timedelta(minutes=CRON_SYNC_MIN_INTERVAL_MINUTES):
                return True
        return False

    def _should_skip_cron_contact_sync(self):
        """Avoid hammering address-book API between scheduled contact sync runs."""
        self.ensure_one()
        if self._is_api_rate_limited():
            return True
        if self.last_contact_sync:
            elapsed = fields.Datetime.now() - self.last_contact_sync
            if elapsed < timedelta(minutes=CRON_SYNC_MIN_INTERVAL_MINUTES):
                return True
        return False

    def sync_contacts_recent(self):
        """Lightweight cron sync: fetch RingCentral address book into Odoo contacts."""
        Sync = self.env['ringcentral.contact.sync']
        try:
            for config in self:
                if not config.active or not config.access_token:
                    continue
                if config._should_skip_cron_contact_sync():
                    _logger.debug(
                        'Skipping RingCentral contact cron for config %s (rate limit or recent sync)',
                        config.id,
                    )
                    continue
                try:
                    Sync.with_context(ringcentral_skip_push=True).sync_contacts(config)
                except RingCentralRateLimitError:
                    _logger.warning(
                        'RingCentral rate limit during contact cron for config %s',
                        config.id,
                    )
                except Exception as error:
                    _logger.error(
                        'Error in contact cron for config %s: %s',
                        config.id, error, exc_info=True,
                    )
        except Exception as error:
            _logger.error('Error in contact cron: %s', error, exc_info=True)

    def sync_call_history_recent(self):
        """Lightweight cron sync: backfill and update recent call-log rows."""
        try:
            for config in self:
                if not config.active or not config.access_token:
                    continue

                if config._should_skip_cron_sync():
                    _logger.debug(
                        'Skipping RingCentral cron sync for config %s (rate limit or recent sync)',
                        config.id,
                    )
                    continue

                try:
                    from_date = (fields.Datetime.now() - timedelta(hours=6)).strftime(
                        '%Y-%m-%dT%H:%M:%S.000Z'
                    )
                    call_logs = config.get_call_logs(
                        limit=50,
                        date_from=from_date,
                        view='Simple',
                    )
                    records = call_logs.get('records', [])
                    config._sync_call_log_records(records, update_existing=True)
                    self._safe_update_last_sync(config)
                except RingCentralRateLimitError:
                    _logger.warning(
                        'RingCentral rate limit during cron sync for config %s',
                        config.id,
                    )
                except Exception as e:
                    _logger.error(
                        'Error in recent sync for config %s: %s',
                        config.id, str(e), exc_info=True,
                    )
        except Exception as e:
            _logger.error('Error in recent sync: %s', str(e), exc_info=True)

    def sync_call_history(self):
        """Sync call history from RingCentral (full sync)"""
        self.ensure_one()
        self._raise_user_friendly_rate_limit()

        try:
            call_logs = self.get_call_logs(limit=1000)
        except RingCentralRateLimitError as error:
            self._handle_rate_limit_error(error)
        records = call_logs.get('records', [])
        created_count, updated_count, _skipped = self._sync_call_log_records(records)

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

    def action_sync_contacts(self):
        """Synchronize RingCentral address book contacts into existing Odoo records."""
        self.ensure_one()
        self._raise_user_friendly_rate_limit()
        Sync = self.env['ringcentral.contact.sync']
        try:
            counters = Sync.sync_contacts(self)
        except RingCentralRateLimitError:
            self._raise_user_friendly_rate_limit()
        wizard = self.env['ringcentral.contact.sync.result'].create({
            'config_id': self.id,
            'processed': counters.get('processed', 0),
            'partners_updated': counters.get('partners_updated', 0),
            'leads_updated': counters.get('leads_updated', 0),
            'skipped': counters.get('skipped', 0),
            'failed': counters.get('failed', 0),
            'rate_limited': counters.get('rate_limited', False),
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contact Sync Summary'),
            'res_model': 'ringcentral.contact.sync.result',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_webhook_event_filters(self):
        """Return the preferred RingCentral webhook event filter set.

        Recordings are resolved via call-log sync / ``_maybe_enrich_recording``;
        RingCentral does not expose a wildcard recording event filter.
        """
        return self._get_webhook_event_filter_sets()[0]

    def _get_webhook_event_filter_sets(self):
        """Return event filter sets from fullest to minimal (for API fallback)."""
        return [
            [RC_FILTER_PRESENCE, RC_FILTER_ACCOUNT_TELEPHONY],
            [RC_FILTER_PRESENCE, RC_FILTER_EXTENSION_TELEPHONY],
            [RC_FILTER_PRESENCE],
        ]

    @api.model
    def _is_event_filters_api_error(self, error):
        """True when RingCentral rejected the subscription eventFilters payload."""
        message = str(error).lower()
        return (
            'eventfilter' in message
            or 'event filter' in message
            or 'parameter [eventfilters]' in message
        )

    def _log_subscription_filter_result(self, result, requested_filters):
        """Log active and disabled filters returned by RingCentral."""
        disabled = result.get('disabledFilters') or []
        for item in disabled:
            _logger.warning(
                'RC subscription disabled filter %s (%s): %s',
                item.get('filter'),
                item.get('reason'),
                item.get('message'),
            )
        active = result.get('eventFilters') or requested_filters
        if disabled:
            _logger.info(
                'RC webhook subscription %s active filters: %s',
                result.get('id'), active,
            )
        else:
            _logger.info(
                'RC webhook subscription %s filters: %s',
                result.get('id'), active,
            )

    def _build_webhook_subscription_payload(self, event_filters=None):
        """Build subscription payload for create/update requests."""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        webhook_url = f"{base_url}/ringcentral/webhook/{self.id}"
        return {
            'eventFilters': event_filters or self._get_webhook_event_filters(),
            'deliveryMode': {
                'transportType': 'WebHook',
                'address': webhook_url,
            },
            'expiresIn': WEBHOOK_MAX_EXPIRES_IN,
        }

    def _create_or_update_subscription(self, subscription_data):
        """POST a new subscription or PUT an existing one."""
        self.ensure_one()
        if self.subscription_id:
            endpoint = f'/subscription/{self.subscription_id}'
            method = 'PUT'
        else:
            endpoint = '/subscription'
            method = 'POST'
        return self._make_api_request(method, endpoint, data=subscription_data)

    def _create_or_update_subscription_resilient(self, subscription_data):
        """Create/update subscription, falling back to fewer filters on RC rejection."""
        self.ensure_one()
        base_payload = dict(subscription_data)
        filter_sets = self._get_webhook_event_filter_sets()

        last_error = None
        for filters in filter_sets:
            payload = dict(base_payload)
            payload['eventFilters'] = filters
            try:
                result = self._create_or_update_subscription(payload)
                self._log_subscription_filter_result(result, filters)
                return result
            except UserError as error:
                if not self._is_event_filters_api_error(error):
                    raise
                last_error = error
                _logger.warning(
                    'RC subscription rejected eventFilters %s for config %s: %s',
                    filters, self.id, error,
                )
        if last_error:
            raise last_error
        raise UserError(_('Failed to create webhook subscription: no event filters available.'))

    def _save_subscription_result(self, result):
        """Persist subscription id and expiry from RingCentral response."""
        self.ensure_one()
        self.write({
            'subscription_id': result.get('id') or self.subscription_id,
            'subscription_expires_at': fields.Datetime.now() + timedelta(
                seconds=min(result.get('expiresIn', WEBHOOK_MAX_EXPIRES_IN), WEBHOOK_MAX_EXPIRES_IN),
            ),
        })

    def create_webhook_subscription(self):
        """Create or update webhook subscription using RingCentral Subscription API"""
        self.ensure_one()

        if not self.access_token:
            raise UserError(_('Not authenticated. Please authenticate first.'))

        self._raise_user_friendly_rate_limit()

        subscription_data = self._build_webhook_subscription_payload()
        method = 'PUT' if self.subscription_id else 'POST'

        try:
            result = self._create_or_update_subscription_resilient(subscription_data)
        except RingCentralRateLimitError as error:
            self._handle_rate_limit_error(error)
        except UserError as error:
            if self.subscription_id and (
                '400' in str(error) or self._is_event_filters_api_error(error)
            ):
                _logger.warning(
                    'Webhook subscription %s update failed for config %s; recreating subscription: %s',
                    self.subscription_id, self.id, error,
                )
                old_subscription_id = self.subscription_id
                try:
                    self._make_api_request('DELETE', f'/subscription/{old_subscription_id}')
                except RingCentralRateLimitError as rate_error:
                    self._handle_rate_limit_error(rate_error)
                except Exception as delete_error:
                    _logger.info(
                        'Could not delete stale subscription %s: %s',
                        old_subscription_id, delete_error,
                    )
                self.write({'subscription_id': False, 'subscription_expires_at': False})
                result = self._create_or_update_subscription_resilient(subscription_data)
                method = 'POST'
            else:
                raise

        try:
            self._save_subscription_result(result)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Webhook subscription %s successfully.') % (
                        'created' if method == 'POST' else 'updated'
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error("Failed to create webhook subscription: %s", str(e), exc_info=True)
            raise UserError(_('Failed to create webhook subscription: %s') % str(e))
    
    def renew_webhook_subscription(self):
        """Renew existing webhook subscription"""
        self.ensure_one()

        if not self.subscription_id:
            return self.create_webhook_subscription()

        self._raise_user_friendly_rate_limit()

        try:
            endpoint = f'/subscription/{self.subscription_id}/renew'
            result = self._make_api_request('POST', endpoint)
            self._save_subscription_result(result)
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
        except RingCentralRateLimitError as error:
            self._handle_rate_limit_error(error)
        except UserError as error:
            _logger.warning(
                'Webhook renew failed for config %s subscription %s, falling back to update: %s',
                self.id, self.subscription_id, error,
            )
            return self.create_webhook_subscription()
        except Exception as e:
            _logger.error("Failed to renew webhook subscription: %s", str(e), exc_info=True)
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
    def _deactivate_legacy_finalize_cron(self):
        """Disable removed per-call finalize cron that caused API rate limits."""
        cron = self.env.ref(
            'ringcentral_integration.ir_cron_finalize_calls_from_call_log',
            raise_if_not_found=False,
        )
        if cron and cron.active:
            cron.sudo().write({'active': False})
            _logger.info('Deactivated legacy RingCentral finalize cron (rate-limit fix)')

    @api.model
    def cron_maintain_tokens_and_subscription(self):
        """Scheduled task: auto-refresh token and auto-renew subscription for active configs.
        
        - If token expires within 10 minutes, refresh it.
        - If subscription missing, create it.
        - If subscription expires within 1 day, renew it.
        """
        self._deactivate_legacy_finalize_cron()
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

