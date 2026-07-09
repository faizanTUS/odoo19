from odoo import models,api

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
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
