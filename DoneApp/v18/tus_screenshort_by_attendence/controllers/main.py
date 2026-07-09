# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.http import request
from odoo.addons.hr_attendance.controllers.main import HrAttendance


class HrAttendance(HrAttendance):

    @http.route('/hr_attendance/systray_check_in_out', type="json", auth="user")
    def systray_attendance(self, latitude=False, longitude=False, check_in_out_image=False):
        employee = request.env.user.employee_id
        geo_ip_response = self._get_geoip_response(mode='systray', latitude=latitude, longitude=longitude)
        employee.with_context(img_data=check_in_out_image)._attendance_action_change(geo_ip_response)
        return self._get_employee_info_response(employee)
