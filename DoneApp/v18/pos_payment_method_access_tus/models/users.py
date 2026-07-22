# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, models


class ResUsersTus(models.Model):
    _inherit = "res.users"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if self._context.get("is_pos_users"):
            users = self.env.ref("point_of_sale.group_pos_manager").users.ids
            users += self.env.ref("point_of_sale.group_pos_user").users.ids
            users = list(set(users))
            args = [("id", "in", users)]
        return super(ResUsersTus, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
