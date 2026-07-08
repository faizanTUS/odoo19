# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ringcentral_integration.models.ringcentral_config import RingCentralRateLimitError
from odoo.addons.ringcentral_integration.utils import phone as phone_utils

_logger = logging.getLogger(__name__)

ADDRESS_BOOK_ENDPOINT = '/account/~/extension/~/address-book/contact'
ADDRESS_BOOK_PER_PAGE = 250
RC_PHONE_FIELDS = (
    'mobilePhone',
    'businessPhone',
    'businessPhone2',
    'homePhone',
    'otherPhone',
    'companyPhone',
    'callbackPhone',
)


class RingCentralContactSync(models.AbstractModel):
    _name = 'ringcentral.contact.sync'
    _description = 'RingCentral Address Book Contact Synchronization'

    @api.model
    def fetch_address_book_contacts(self, config):
        """Fetch all personal address book contacts with pagination."""
        config.ensure_one()
        records = []
        page = 1
        while True:
            try:
                result = config._make_api_request(
                    'GET',
                    ADDRESS_BOOK_ENDPOINT,
                    params={'page': page, 'perPage': ADDRESS_BOOK_PER_PAGE},
                )
            except RingCentralRateLimitError:
                raise
            except UserError:
                raise
            except Exception as error:
                _logger.error(
                    'RingCentral address book fetch failed on page %s for config %s: %s',
                    page, config.id, error,
                )
                raise UserError(_(
                    'Failed to fetch RingCentral contacts (page %(page)s): %(error)s'
                ) % {'page': page, 'error': error}) from error

            batch = result.get('records') or []
            for item in batch:
                if (item.get('availability') or 'Alive') == 'Deleted':
                    continue
                records.append(item)

            paging = result.get('paging') or {}
            total_pages = paging.get('totalPages') or page
            if page >= total_pages or not batch:
                break
            page += 1
        return records

    @api.model
    def _build_display_name(self, rc_record):
        parts = [
            (rc_record.get('firstName') or '').strip(),
            (rc_record.get('lastName') or '').strip(),
        ]
        name = ' '.join(part for part in parts if part)
        if not name:
            name = (rc_record.get('nickName') or '').strip()
        return name

    @api.model
    def _pick_email(self, rc_record):
        for field in ('email', 'email2', 'email3'):
            value = (rc_record.get(field) or '').strip()
            if value:
                return value
        return ''

    @api.model
    def _pick_address(self, rc_record):
        for key in ('businessAddress', 'homeAddress', 'otherAddress'):
            address = rc_record.get(key)
            if isinstance(address, dict) and any(address.values()):
                return address
        return {}

    @api.model
    def _resolve_country_id(self, country_name):
        if not country_name:
            return False
        Country = self.env['res.country'].sudo()
        country = Country.search([('code', '=', country_name)], limit=1)
        if not country:
            country = Country.search([('name', 'ilike', country_name)], limit=1)
        return country.id if country else False

    @api.model
    def _resolve_state_id(self, state_name, country_id):
        if not state_name:
            return False
        State = self.env['res.country.state'].sudo()
        domain = [('name', 'ilike', state_name)]
        if country_id:
            domain.append(('country_id', '=', country_id))
        state = State.search(domain, limit=1)
        return state.id if state else False

    @api.model
    def normalize_rc_contact(self, rc_record):
        """Map a RingCentral contact record to a normalized dict."""
        address = self._pick_address(rc_record)
        country_id = self._resolve_country_id((address.get('country') or '').strip())
        state_id = self._resolve_state_id((address.get('state') or '').strip(), country_id)
        phones = self.collect_phone_numbers(rc_record)
        return {
            'rc_id': rc_record.get('id'),
            'name': self._build_display_name(rc_record),
            'company': (rc_record.get('company') or '').strip(),
            'email': self._pick_email(rc_record),
            # Odoo 19 has a single ``phone`` field (no ``mobile``); mobilePhone is
            # the most reachable number, so it takes priority.
            'phone': (
                (rc_record.get('mobilePhone') or '').strip()
                or (rc_record.get('businessPhone') or '').strip()
                or (rc_record.get('companyPhone') or '').strip()
                or (rc_record.get('homePhone') or '').strip()
            ),
            'function': (rc_record.get('jobTitle') or '').strip(),
            'notes': (rc_record.get('notes') or '').strip(),
            'street': (address.get('street') or '').strip(),
            'city': (address.get('city') or '').strip(),
            'zip': (address.get('zip') or '').strip(),
            'state_id': state_id,
            'country_id': country_id,
            'phones': phones,
            'primary_phone': phones[0] if phones else '',
        }

    @api.model
    def collect_phone_numbers(self, rc_record):
        """Return deduplicated phone numbers from an RC contact."""
        seen = set()
        numbers = []
        for field in RC_PHONE_FIELDS:
            raw = (rc_record.get(field) or '').strip()
            if not raw:
                continue
            digits = phone_utils.normalize_phone_number(raw, self.env) or phone_utils.normalize_phone(raw)
            if not digits or len(digits) < 7:
                continue
            key = phone_utils.get_last10(digits) or digits
            if key in seen:
                continue
            seen.add(key)
            numbers.append(raw)
        return numbers

    @api.model
    def _is_empty(self, value):
        return value in (None, False, '')

    @api.model
    def _maybe_set(self, vals, field_name, new_value, current_value, overwrite):
        if self._is_empty(new_value):
            return
        if overwrite or self._is_empty(current_value):
            vals[field_name] = new_value

    @api.model
    def build_partner_vals(self, rc_data, partner, overwrite=False):
        """Build write values for res.partner enrichment."""
        vals = {}
        self._maybe_set(vals, 'name', rc_data.get('name'), partner.name, overwrite)
        self._maybe_set(vals, 'email', rc_data.get('email'), partner.email, overwrite)
        self._maybe_set(vals, 'phone', rc_data.get('phone'), partner.phone, overwrite)
        if 'function' in partner._fields:
            self._maybe_set(vals, 'function', rc_data.get('function'), partner.function, overwrite)
        if 'comment' in partner._fields:
            self._maybe_set(vals, 'comment', rc_data.get('notes'), partner.comment, overwrite)
        if 'company_name' in partner._fields:
            self._maybe_set(vals, 'company_name', rc_data.get('company'), partner.company_name, overwrite)
        if 'street' in partner._fields:
            self._maybe_set(vals, 'street', rc_data.get('street'), partner.street, overwrite)
        if 'city' in partner._fields:
            self._maybe_set(vals, 'city', rc_data.get('city'), partner.city, overwrite)
        if 'zip' in partner._fields:
            self._maybe_set(vals, 'zip', rc_data.get('zip'), partner.zip, overwrite)
        if 'state_id' in partner._fields:
            self._maybe_set(vals, 'state_id', rc_data.get('state_id'), partner.state_id.id, overwrite)
        if 'country_id' in partner._fields:
            self._maybe_set(vals, 'country_id', rc_data.get('country_id'), partner.country_id.id, overwrite)
        return vals

    @api.model
    def build_lead_vals(self, rc_data, lead, overwrite=False):
        """Build write values for crm.lead enrichment (used by lead_creation extension)."""
        vals = {}
        Lead = lead.env['crm.lead']
        if 'contact_name' in Lead._fields:
            self._maybe_set(vals, 'contact_name', rc_data.get('name'), lead.contact_name, overwrite)
        if 'partner_name' in Lead._fields:
            self._maybe_set(vals, 'partner_name', rc_data.get('company'), lead.partner_name, overwrite)
        if 'email_from' in Lead._fields:
            self._maybe_set(vals, 'email_from', rc_data.get('email'), lead.email_from, overwrite)
        if 'phone' in Lead._fields:
            self._maybe_set(vals, 'phone', rc_data.get('phone') or rc_data.get('primary_phone'), lead.phone, overwrite)
        if 'function' in Lead._fields:
            self._maybe_set(vals, 'function', rc_data.get('function'), lead.function, overwrite)
        if 'description' in Lead._fields:
            self._maybe_set(vals, 'description', rc_data.get('notes'), lead.description, overwrite)
        if 'street' in Lead._fields:
            self._maybe_set(vals, 'street', rc_data.get('street'), lead.street, overwrite)
        if 'city' in Lead._fields:
            self._maybe_set(vals, 'city', rc_data.get('city'), lead.city, overwrite)
        if 'zip' in Lead._fields:
            self._maybe_set(vals, 'zip', rc_data.get('zip'), lead.zip, overwrite)
        if 'state_id' in Lead._fields:
            self._maybe_set(vals, 'state_id', rc_data.get('state_id'), lead.state_id.id, overwrite)
        if 'country_id' in Lead._fields:
            self._maybe_set(vals, 'country_id', rc_data.get('country_id'), lead.country_id.id, overwrite)
        return vals

    @api.model
    def _find_partner_for_rc_contact(self, rc_data):
        CallHistory = self.env['ringcentral.call.history'].sudo()
        for number in rc_data.get('phones') or []:
            partner = CallHistory.find_partner_for_phone(number)
            if partner:
                return partner
        return self.env['res.partner'].browse()

    @api.model
    def _sync_partner_for_rc_contact(self, rc_data, overwrite, updated_partner_ids):
        partner = self._find_partner_for_rc_contact(rc_data)
        if not partner:
            return False
        if partner.id in updated_partner_ids:
            return False
        vals = self.build_partner_vals(rc_data, partner, overwrite=overwrite)
        if vals:
            partner.with_context(ringcentral_skip_push=True).write(vals)
            updated_partner_ids.add(partner.id)
            return True
        return False

    @api.model
    def _sync_lead_for_rc_contact(self, rc_data, config, overwrite, updated_lead_ids):
        """Hook for ringcentral_lead_creation to override."""
        return False

    @api.model
    def _process_rc_contact(self, rc_record, config, overwrite, counters, updated_partner_ids, updated_lead_ids):
        rc_data = self.normalize_rc_contact(rc_record)
        if not rc_data.get('phones'):
            counters['skipped'] += 1
            return

        partner_updated = self._sync_partner_for_rc_contact(
            rc_data, overwrite, updated_partner_ids,
        )
        lead_updated = self._sync_lead_for_rc_contact(
            rc_data, config, overwrite, updated_lead_ids,
        )

        if partner_updated:
            counters['partners_updated'] += 1
        if lead_updated:
            counters['leads_updated'] += 1
        if not partner_updated and not lead_updated:
            counters['skipped'] += 1

    @api.model
    def sync_contacts(self, config):
        """Synchronize RingCentral address book contacts into existing Odoo records."""
        config.ensure_one()
        config._raise_user_friendly_rate_limit()

        counters = {
            'processed': 0,
            'partners_updated': 0,
            'leads_updated': 0,
            'skipped': 0,
            'failed': 0,
            'rate_limited': False,
        }
        updated_partner_ids = set()
        updated_lead_ids = set()
        overwrite = bool(config.contact_sync_overwrite)

        try:
            rc_contacts = self.fetch_address_book_contacts(config)
        except RingCentralRateLimitError:
            counters['rate_limited'] = True
            raise

        for rc_record in rc_contacts:
            counters['processed'] += 1
            try:
                with self.env.cr.savepoint():
                    self._process_rc_contact(
                        rc_record,
                        config,
                        overwrite,
                        counters,
                        updated_partner_ids,
                        updated_lead_ids,
                    )
            except Exception as error:
                counters['failed'] += 1
                _logger.warning(
                    'RingCentral contact sync failed for RC contact %s (config %s): %s',
                    rc_record.get('id'), config.id, error,
                    exc_info=True,
                )

        config.sudo().write({'last_contact_sync': fields.Datetime.now()})
        return counters

    @api.model
    def _split_partner_name(self, name):
        name = (name or '').strip()
        if not name:
            return '', ''
        parts = name.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

    @api.model
    def _build_business_address(self, partner):
        address = {}
        if partner.street:
            address['street'] = partner.street
        if partner.city:
            address['city'] = partner.city
        if partner.zip:
            address['zip'] = partner.zip
        if partner.state_id:
            address['state'] = partner.state_id.name
        if partner.country_id:
            address['country'] = partner.country_id.code
        return address or None

    @api.model
    def build_rc_contact_payload(self, partner):
        """Map an Odoo partner to a RingCentral address book contact payload."""
        first_name, last_name = self._split_partner_name(partner.name)
        payload = {}
        if first_name:
            payload['firstName'] = first_name
        if last_name:
            payload['lastName'] = last_name
        if partner.email:
            payload['email'] = partner.email
        if partner.phone:
            payload['mobilePhone'] = partner.phone
        company = partner.company_name
        if not company and partner.parent_id and partner.parent_id.is_company:
            company = partner.parent_id.name
        if company:
            payload['company'] = company
        if 'function' in partner._fields and partner.function:
            payload['jobTitle'] = partner.function
        if 'comment' in partner._fields and partner.comment:
            payload['notes'] = partner.comment
        address = self._build_business_address(partner)
        if address:
            payload['businessAddress'] = address
        return payload

    @api.model
    def find_rc_contact_by_phone(self, config, phone):
        if not phone:
            return None
        try:
            result = config._make_api_request(
                'GET',
                ADDRESS_BOOK_ENDPOINT,
                params={'phoneNumber': phone},
            )
        except Exception as error:
            _logger.warning(
                'RingCentral contact lookup by phone failed for config %s: %s',
                config.id, error,
            )
            return None
        records = result.get('records') or []
        return records[0] if records else None

    @api.model
    def _get_partner_contact_link(self, partner, config):
        return self.env['ringcentral.partner.contact.link'].sudo().search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', config.id),
        ], limit=1)

    @api.model
    def push_partner_to_ringcentral(self, config, partner):
        """Create or update a RingCentral address book contact from an Odoo partner."""
        config.ensure_one()
        partner.ensure_one()
        if config._is_api_rate_limited():
            return False

        link = self._get_partner_contact_link(partner, config)
        rc_contact_id = link.ringcentral_contact_id if link else None
        payload = self.build_rc_contact_payload(partner)
        if not partner.phone:
            return False
        if not payload.get('mobilePhone'):
            payload['mobilePhone'] = partner.phone

        try:
            if rc_contact_id:
                result = config._make_api_request(
                    'PUT',
                    f'{ADDRESS_BOOK_ENDPOINT}/{rc_contact_id}',
                    data=payload,
                )
            else:
                existing = self.find_rc_contact_by_phone(config, partner.phone)
                if existing and existing.get('id'):
                    rc_contact_id = str(existing['id'])
                    result = config._make_api_request(
                        'PUT',
                        f'{ADDRESS_BOOK_ENDPOINT}/{rc_contact_id}',
                        data=payload,
                    )
                else:
                    result = config._make_api_request(
                        'POST',
                        ADDRESS_BOOK_ENDPOINT,
                        data=payload,
                    )
                    rc_contact_id = str(result.get('id') or '')

            if not rc_contact_id and result:
                rc_contact_id = str(result.get('id') or '')

            if rc_contact_id:
                Link = self.env['ringcentral.partner.contact.link'].sudo()
                if link:
                    link.write({'ringcentral_contact_id': rc_contact_id})
                else:
                    Link.create({
                        'partner_id': partner.id,
                        'config_id': config.id,
                        'ringcentral_contact_id': rc_contact_id,
                    })
            return bool(rc_contact_id)
        except RingCentralRateLimitError:
            raise
        except Exception as error:
            _logger.warning(
                'RingCentral contact push failed for partner %s config %s: %s',
                partner.id, config.id, error,
            )
            return False

    @api.model
    def push_partner_if_enabled(self, partner):
        """Push partner to RingCentral when a target configuration is resolved and enabled."""
        partner.ensure_one()
        config = partner._get_partner_ringcentral_config()
        if not config or not config.push_contacts_to_ringcentral or not config.access_token:
            return False
        return self.push_partner_to_ringcentral(config, partner)
