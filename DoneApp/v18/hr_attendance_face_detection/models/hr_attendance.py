# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields
import requests
import logging

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_latitude = fields.Float("Check-In Latitude")
    check_in_longitude = fields.Float("Check-In Longitude")
    check_in_address = fields.Char("Check-In Address")

    check_out_latitude = fields.Float("Check-Out Latitude")
    check_out_longitude = fields.Float("Check-Out Longitude")
    check_out_address = fields.Char("Check-Out Address")

    def _get_address_from_coords(self, lat, lng):
        """Fetch human-readable address using OpenStreetMap Nominatim API"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
            headers = {"User-Agent": "OdooFaceAttendance/1.0"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return data.get("display_name")
        except Exception as e:
            _logger.error("Reverse geocoding failed: %s", e)
        return None
