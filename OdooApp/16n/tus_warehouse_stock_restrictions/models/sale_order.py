# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, count=False):
        """Odoo 18 List View hits this method via search_fetch()."""

        user_limit = self.env.user.limit_sale_order
        has_restriction_group = self.env.user.has_group('tus_warehouse_stock_restrictions.group_restrict_sale_order_limit')

        if has_restriction_group and user_limit and not self.env.context.get('ignore_so_limit'):
            # enforce our limit
            if not limit:
                limit = user_limit
            else:
                limit = min(limit, user_limit)

        # Call parent with the EXACT Odoo 18 signature
        return super()._search(domain, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Higher-level API must also enforce the same limit."""
        user_limit = self.env.user.limit_sale_order
        has_restriction_group = self.env.user.has_group('tus_warehouse_stock_restrictions.group_restrict_sale_order_limit')

        if has_restriction_group and user_limit and not count and not self.env.context.get('ignore_so_limit'):
            if not limit:
                limit = user_limit
            else:
                limit = min(limit, user_limit)

        return super().search(args, offset=offset, limit=limit, order=order, count=count)