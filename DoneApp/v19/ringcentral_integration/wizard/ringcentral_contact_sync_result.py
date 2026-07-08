# -*- coding: utf-8 -*-
from odoo import fields, models


class RingCentralContactSyncResult(models.TransientModel):
    _name = 'ringcentral.contact.sync.result'
    _description = 'RingCentral Contact Sync Summary'

    config_id = fields.Many2one('ringcentral.config', readonly=True)
    processed = fields.Integer(string='Total Contacts Processed', readonly=True)
    partners_updated = fields.Integer(string='Odoo Contacts Updated', readonly=True)
    leads_updated = fields.Integer(string='CRM Leads Updated', readonly=True)
    skipped = fields.Integer(string='Contacts Skipped', readonly=True)
    failed = fields.Integer(string='Failed Records', readonly=True)
    rate_limited = fields.Boolean(string='Rate Limited', readonly=True)
