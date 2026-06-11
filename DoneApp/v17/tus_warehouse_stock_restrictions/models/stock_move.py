# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, api, _, fields
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def _check_user_location_rights(self):
        user = self.env.user
        if not user.restrict_locations:
            return

        allowed = user.stock_location_ids.ids

        for rec in self:
            if rec.state == 'draft':
                continue

            if rec.location_id.id not in allowed:
                raise UserError(_("You cannot move stock from location '%s'.") % rec.location_id.display_name)

            if rec.location_dest_id.id not in allowed:
                raise UserError(_("You cannot move stock to location '%s'.") % rec.location_dest_id.display_name)
