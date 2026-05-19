# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
import base64
import face_recognition
import numpy as np
from io import BytesIO
from PIL import Image
import logging

_logger = logging.getLogger(__name__)


class HREmployee(models.Model):
    _inherit = "hr.employee"

    face_encoding = fields.Binary("Face Encoding", help="Serialized face encoding for recognition")

    @api.model
    def create(self, vals):
        """Generate face encoding when employee is created with image"""
        employee = super(HREmployee, self).create(vals)
        if employee.image_1920:
            employee._generate_face_encoding()
        return employee

    def write(self, vals):
        """Generate face encoding when employee image is updated"""
        result = super(HREmployee, self).write(vals)
        if 'image_1920' in vals and vals['image_1920']:
            for employee in self:
                employee._generate_face_encoding()
        return result

    def _generate_face_encoding(self):
        """Generate face encoding from employee image"""
        for emp in self:
            if emp.image_1920:
                try:
                    _logger.info(f"Generating face encoding for {emp.name}")
                    img_data = base64.b64decode(emp.image_1920)
                    img = np.array(Image.open(BytesIO(img_data)))
                    encodings = face_recognition.face_encodings(img)

                    if encodings:
                        emp.face_encoding = base64.b64encode(encodings[0].tobytes())
                        _logger.info(f"✅ Face encoding generated for {emp.name}")
                    else:
                        _logger.warning(f"❌ No face detected in image for {emp.name}")
                        emp.face_encoding = False

                except Exception as e:
                    _logger.error(f"❌ Error generating face encoding for {emp.name}: {e}")
                    emp.face_encoding = False

    def generate_face_encoding_manual(self):
        """Manual method to generate face encodings"""
        generated_count = 0
        for emp in self:
            if emp.image_1920:
                emp._generate_face_encoding()
                if emp.face_encoding:
                    generated_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Face encodings generated for {generated_count} employees',
                'type': 'success',
                'sticky': False,
            }
        }
