# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models,api

class PosSession(models.Model):
    _inherit = 'pos.session'

    # def _pos_ui_models_to_load(self):
    def _load_pos_data_models(self,config):
        res = super()._load_pos_data_models(config)
        res.append('hr.employee')
        return res

    def _loader_params_custom_model(self):
        return {
            'search_params': {
                'fields': ['name', 'id'],
            },
        }

    def _get_pos_ui_custom_model(self, params):
        return self.env['hr.employee'].search_read(**params['search_params'])
