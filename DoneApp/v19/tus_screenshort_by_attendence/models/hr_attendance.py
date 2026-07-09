# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class HrAttendanceInherit(models.Model):
    _inherit = "hr.attendance"

    check_in_image = fields.Binary("Check In Image", attachment=True)
    check_out_image = fields.Binary("Check Out Image", attachment=True)

class HrEmp(models.Model):
    _inherit = 'hr.employee'

    def _attendance_action_change(self, geo_information=None):
        res = super(HrEmp, self)._attendance_action_change(geo_information=geo_information)
        image = self._context and self._context.get('img_data')
        if image:
            if not res.check_in_image:
                res.write({'check_in_image': image[image.index(",") + len(","):]})
            else:
                res.write({'check_out_image': image[image.index(",") + len(","):]})
        return res
