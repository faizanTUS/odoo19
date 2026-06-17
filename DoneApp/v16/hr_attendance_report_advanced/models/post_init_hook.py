# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    """Create default configuration for all companies"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    companies = env['res.company'].search([])
    config_model = env['hr.attendance.report.config']

    for company in companies:
        existing_config = config_model.search(
            [('company_id', '=', company.id)],
            limit=1
        )
        if not existing_config:
            config_model.create({
                'company_id': company.id,
            })

