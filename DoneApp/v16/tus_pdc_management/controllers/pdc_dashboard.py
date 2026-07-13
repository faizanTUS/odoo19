# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from datetime import date, timedelta


class PdcDashboard(http.Controller):

    @http.route("/tus/pdc/dashboard/data", type="json", auth="user")
    def pdc_dashboard_data(self):
        PDC = request.env["tus.pdc.payment"].sudo()

        today = date.today()
        next_7 = today + timedelta(days=7)

        registered_customer = PDC.search([("pdc_type", "=", "customer"), ("state", "=", "registered")])
        registered_vendor = PDC.search([("pdc_type", "=", "vendor"), ("state", "=", "registered")])
        overdue = PDC.search([("state", "=", "registered"), ("days_overdue", ">", 0)])
        next7 = PDC.search([("state", "=", "registered"), ("cheque_date", "<=", next_7)])

        return {
            "customer_pdc": sum(registered_customer.mapped("amount")),
            "vendor_pdc": sum(registered_vendor.mapped("amount")),
            "overdue": sum(overdue.mapped("amount")),
            "next7": sum(next7.mapped("amount")),
        }
