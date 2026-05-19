# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
def post_init_hook(env):
    """Create default configuration for all companies"""
    # Get all companies
    companies = env['res.company'].search([])
    
    # Create configuration for each company if not exists
    config_model = env['hr.attendance.report.config']
    for company in companies:
        existing_config = config_model.search([
            ('company_id', '=', company.id)
        ], limit=1)
        
        if not existing_config:
            config_model.create({
                'company_id': company.id,
            })

