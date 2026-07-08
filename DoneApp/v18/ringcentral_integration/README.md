# RingCentral Integration Module for Odoo 19

## Overview

This module provides comprehensive RingCentral integration for Odoo 19, enabling seamless communication management within your Odoo instance. It features full CTI (Computer Telephony Integration) capabilities including call management, history tracking, contact linking, call recordings, transcripts, and real-time analytics.

## Key Features

### 🔐 Authentication & Security
- **OAuth 2.0 Authorization Code Flow**: Secure authentication with automatic token refresh
- **Account-Level Authentication**: For webhooks and background synchronization
- **User-Level Widget Authentication**: Each user authenticates individually via embedded widget

### 📞 Calling Features
- **Embedded RingCentral Widget**: Native RingCentral calling experience embedded directly in Odoo
- **Click-to-Call**: One-click calling from partner records with automatic dialer population
- **Call Controls**: Full widget functionality including dialer, call controls, and presence management
- **Widget Visibility Control**: Toggle widget via systray icon, exclusive control prevents accidental hiding

### 📊 Call History & Analytics
- **Comprehensive Call History**: Complete call tracking with automatic contact linking
- **Advanced Dashboard**: Multiple graph views (line, bar, pie) and pivot tables
- **Search & Filters**: Filter by direction, status, date, contact, phone numbers
- **KPIs & Metrics**: Call duration, success rates, hourly/weekly distribution

### 🔗 Contact Integration
- **Intelligent Contact Mapping**: Automatic linking of calls to Odoo contacts based on phone numbers
- **Multiple Matching Strategies**: Exact match, normalized digits, and fuzzy matching
- **Latest Contact Priority**: When multiple contacts match, selects the most recently updated
- **Backfill Support**: Manual action to link existing call history to contacts

### 📝 Call Data
- **Call Transcripts**: Automatic storage of call transcripts from RingCentral AI
- **Call Recordings**: Access and playback call recordings with authenticated proxy support
- **Call Metadata**: Duration, direction, status, timestamps, and user information

### 🔔 Real-Time Features
- **Webhook Subscriptions**: Automatic subscription for call events, recordings, and transcripts
- **Real-Time Updates**: Instant call history updates without polling
- **Presence Management**: Real-time user status updates with color-coded indicators

### 🎨 User Interface
- **Systray Icon**: System tray icon with color-coded status indicators
- **Status Management**: Quick access to user presence (Available, Busy, Offline, DND)
- **Widget Integration**: Seamless integration with Odoo interface
- **Responsive Design**: Works across different screen sizes

### ⚙️ Configuration & Management
- **Self-Service Setup**: Easy configuration interface
- **Test Connection**: Verify DNS, HTTPS, proxy, and SSL settings
- **Proxy Support**: Configurable HTTP/HTTPS proxy for enterprise networks
- **SSL Controls**: Configurable SSL certificate verification
- **Automatic Maintenance**: Token refresh and subscription renewal handled automatically

## Installation

### Prerequisites
- Odoo 19.0
- Python `requests` library (usually included)
- RingCentral account and application

### Step 1: Install Module
1. Copy the `ringcentral_integration` module to your Odoo addons directory
2. Restart your Odoo server
3. Go to **Apps** menu in Odoo
4. Remove the "Apps" filter and search for "RingCentral Integration"
5. Click **Install**

### Step 2: RingCentral Application Setup
1. Log in to [RingCentral Developer Portal](https://developer.ringcentral.com)
2. Create a new application or use an existing one
3. Configure OAuth Redirect URI:
   ```
   https://your-odoo-instance.com/ringcentral/oauth
   ```
4. Enable the following permissions:
   - **Read Accounts**
   - **Read Call Log**
   - **Read Presence**
   - **RingOut** (for making calls)
   - **Webhook Subscriptions**
5. Note your **Client ID** and **Client Secret**

## Configuration

### Initial Setup

1. **Access Configuration**
   - Navigate to **RingCentral > Configuration** in Odoo menu

2. **Create Configuration Record**
   - Click **Create**
   - Fill in required fields:
     - **Configuration Name**: Friendly name
     - **Client ID**: From RingCentral Developer Portal
     - **Client Secret**: From RingCentral Developer Portal
     - **Server URL**: Production or Sandbox
     - **Active**: Enable/disable

3. **Test Connection**
   - Click **Test Connection** button
   - Verifies DNS, HTTPS, proxy, and SSL settings

4. **OAuth Authentication**
   - Click **Connect (OAuth)** button
   - You'll be redirected to RingCentral login
   - Log in and authorize the application
   - You'll be redirected back to Odoo
   - Configuration will show as "Connected"

### Advanced Settings

#### Proxy Configuration
If your network requires a proxy server:
1. Enable **Enable Proxy** checkbox
2. Enter **HTTP Proxy URL** (format: `http://user:pass@proxy.company.com:8080`)
3. Enter **HTTPS Proxy URL** if different

#### SSL Certificate Verification
- Default: SSL certificates are verified
- Disable only for self-signed certificates in development
- **Warning**: Not recommended for production

## Usage

### Making Calls

#### From Partner Record
1. Open any partner/contact record in Odoo
2. Click the **Call** button in the header
3. RingCentral widget will open (if hidden)
4. Dialer will be populated with partner's phone number
5. Call will be initiated automatically

#### From Widget Directly
1. Click RingCentral icon in system tray (top right)
2. Embedded widget will open
3. Log in to RingCentral if prompted
4. Use dialer to make calls manually

### Managing Widget Visibility
- **Click RingCentral icon**: Toggle widget visibility
- **Click Status icon**: Open user presence dropdown
- Widget visibility controlled exclusively through systray icon

### User Presence Management
1. Click the status icon (colored circle) in systray
2. Select desired status:
   - **Available** - Green circle
   - **Busy** - Orange circle
   - **Offline** - Gray circle
   - **Do Not Disturb** - Red circle with ban icon
3. Status changes are sent to RingCentral widget

**Note**: Status changes only available when logged into RingCentral widget.

### Viewing Call History

#### Dashboard View
1. Go to **RingCentral > Dashboard**
2. View call history in list, pivot, or graph views
3. Use search filters:
   - Phone numbers (from/to)
   - Contacts (from/to)
   - Direction (Inbound/Outbound)
   - Status (Completed/Failed)
   - Date range
4. Switch between views using view selector

### Call History Features
- **Contact Linking**: Automatic linking based on phone numbers
- **Transcripts**: View call transcripts if available
- **Recordings**: Play call recordings directly
- **Chatter**: Notes and activities on call records

### Backfilling Contact Links
If you have existing call history without contact links:
1. Go to **RingCentral > Dashboard**
2. Select call history records (or leave unselected for all)
3. Click **Action > Backfill Contact Links**
4. System will attempt to match phone numbers to contacts
5. May need to run multiple times for large datasets

## API Reference

### Webhook Endpoints
- `GET/POST /ringcentral/webhook/{config_id}` - Receives RingCentral webhook events
- `GET /ringcentral/oauth` - OAuth callback endpoint

### JSON-RPC Endpoints
- `POST /ringcentral/api/config` - Get configuration for widget (JSON-RPC 2.0)

### Webhook Events
The module subscribes to:
- **Call Notifications**: `/restapi/v1.0/account/~/extension/~/telephony/sessions`
- **Presence Updates**: `/restapi/v1.0/account/~/extension/~/presence`
- **Recording Ready**: `/restapi/v1.0/account/~/recording/{recordingId}`
- **Transcription Ready**: `/restapi/v1.0/account/~/recording/{recordingId}/transcript`

### Models

#### ringcentral.config
Main configuration model storing RingCentral credentials and settings.

**Key Fields:**
- `client_id` - RingCentral Application Client ID
- `client_secret` - RingCentral Application Client Secret
- `server_url` - Production or Sandbox URL
- `access_token` - OAuth access token (account-level)
- `refresh_token` - OAuth refresh token
- `subscription_id` - Webhook subscription ID
- `webhook_url` - Computed webhook URL

#### ringcentral.call.history
Stores all call records with partner linking, transcripts, and recordings.

**Key Fields:**
- `ringcentral_call_id` - Unique RingCentral call ID
- `direction` - inbound or outbound
- `status` - completed, failed, busy, no-answer, etc.
- `from_number` - Caller's phone number
- `to_number` - Recipient's phone number
- `from_partner_id` - Linked Odoo contact (from)
- `to_partner_id` - Linked Odoo contact (to)
- `start_time` - Call start timestamp
- `duration` - Call duration in seconds
- `recording_id` - RingCentral recording ID
- `transcript` - Call transcript text

## Troubleshooting

### Widget Not Loading
- Check browser console for JavaScript errors
- Verify configuration is active and authenticated
- Check Client ID and Server URL are correct
- Ensure browser allows popups/iframes from RingCentral domain

### OAuth Authentication Fails
- Verify redirect URI in RingCentral Developer Portal matches: `https://your-domain.com/ringcentral/oauth`
- Check Client ID and Client Secret are correct
- Ensure application has required permissions enabled
- Try clearing browser cache and cookies

### Webhooks Not Receiving Events
- Check webhook subscription status in configuration
- Verify webhook URL is publicly accessible
- Check Odoo server logs for webhook errors
- Ensure subscription hasn't expired (auto-renewal should handle this)
- Verify event filters are correct in subscription

### Contact Linking Not Working
- Run "Backfill Contact Links" action manually
- Verify phone numbers in contacts match call numbers (format may vary)
- Check contacts have phone or mobile fields populated
- Review call history records - linking happens during sync

### Token Expiration Errors
- Automatic token refresh should handle this - check scheduled actions
- Manually re-authenticate via "Connect (OAuth)" button
- Verify refresh token is valid in RingCentral Developer Portal
- Check that configuration is active

### Proxy Connection Issues
- Verify proxy URL format: `http://user:pass@proxy:port`
- Test proxy connectivity using "Test Connection" button
- Check proxy credentials are correct
- If using custom SSL certificates, disable SSL verification (development only)
- Verify proxy allows connections to RingCentral domains

### Logging
Enable debug logging:
1. Edit Odoo configuration file (`odoo.conf`)
2. Add: `log_level = debug`
3. Restart Odoo server
4. Check logs for RingCentral-related messages

## Technical Details

### Architecture
- **Frontend**: Owl components, JavaScript for widget integration
- **Backend**: Python models with Odoo ORM
- **Authentication**: OAuth 2.0 Authorization Code flow
- **Webhooks**: Non-blocking handlers with scheduled sync
- **Synchronization**: Scheduled actions for call history sync

### Scheduled Actions
- **Token Refresh**: Automatically refreshes access tokens before expiration
- **Subscription Renewal**: Renews webhook subscriptions before expiration
- **Call History Sync**: Syncs recent call history every 15 minutes

### Security
- System administrators can manage configurations
- Regular users can view and create call history
- Webhook endpoint uses config ID for security
- OAuth tokens stored securely in database

## Support

For support, contact: **support@techultra.in**

## License

OPL-1 (Odoo Proprietary License v1.0)

## Version History

### 19.0.0.0.1 (2025)
- Initial release for Odoo 19
- OAuth 2.0 Authorization Code flow
- Embedded RingCentral widget integration
- Call history with contact mapping
- Dashboard with analytics
- Webhook support for real-time updates
- Systray icon with status management
- Click-to-call functionality
- Call recordings and transcripts
- Automatic token refresh and subscription renewal
- Proxy and network support
- Test connection functionality

## Additional Resources

- [RingCentral Developer Portal](https://developer.ringcentral.com)
- [RingCentral Embeddable Widget Documentation](https://developers.ringcentral.com/embeddable-voice/docs)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
