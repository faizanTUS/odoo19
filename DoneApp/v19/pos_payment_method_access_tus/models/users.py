# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, models


class ResUsersTus(models.Model):
    _inherit = "res.users"

    @api.model
    def name_search(self, name='', domain=None, operator="ilike", limit=100):
        if domain is None:
            domain = []
        if self._context.get("is_pos_users"):
            pos_manager_users = self.env.ref("point_of_sale.group_pos_manager").user_ids.ids
            pos_user_users = self.env.ref("point_of_sale.group_pos_user").user_ids.ids
            users = list(set(pos_manager_users + pos_user_users))
            domain = [("id", "in", users)] + domain
        return super(ResUsersTus, self).name_search(
            name, domain, operator, limit
        )