# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields,models,api,_

class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        if res.get('search_params') and res.get('search_params').get('fields'):
            field = res.get('search_params').get('fields')
            field.extend(['generate_unique_ref_code'])
        return res