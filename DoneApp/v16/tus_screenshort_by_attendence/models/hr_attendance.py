# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class HrAttendanceInherit(models.Model):
    _inherit = "hr.attendance"

    check_in_image = fields.Binary("Check In Image", attachment=True)
    check_out_image = fields.Binary("Check Out Image", attachment=True)

# Js to called this method and value get the data from JS.

    def get_image_check_in_out(self, data):

        attendance_id = self.browse(data.get('attendance_id'))
        sign= data.get('check_in_out_image')[data.get('check_in_out_image').index(",") + len(","):]

        if data.get('check_out_time').get('attendance').get('check_out') != False:

            dict_rec = {'id': attendance_id.id,
                        'check_out_image': sign}
            attendance_id.write(dict_rec)
        else:
            dict_rec = {'id': attendance_id.id,
                        'check_in_image': sign}
            attendance_id.write(dict_rec)
