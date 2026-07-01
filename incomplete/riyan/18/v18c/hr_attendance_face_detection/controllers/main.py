# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import numpy as np
import face_recognition
import requests
from odoo import http, fields, api
from odoo.http import request
import base64
from io import BytesIO
from PIL import Image
import math
import logging

_logger = logging.getLogger(__name__)


class FaceAttendanceController(http.Controller):

    def calculate_distance_meters(self, lat1, lon1, lat2, lon2):
        """Calculate the Haversine distance between two points in meters.
        
        :param lat1: Latitude of first point
        :param lon1: Longitude of first point
        :param lat2: Latitude of second point
        :param lon2: Longitude of second point
        :return: Distance in meters
        """
        if not all([lat1, lon1, lat2, lon2]):
            return None
        
        R = 6371000  # Radius of Earth in meters
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) * math.sin(dlat / 2) +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) * math.sin(dlon / 2)
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def get_address_from_coords(self, lat, lng):
        """Enhanced geocoding with proper error handling"""
        if not lat or not lng:
            return "Location not provided"

        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
            headers = {"User-Agent": "OdooFaceAttendance/1.0"}
            res = requests.get(url, headers=headers, timeout=10)

            if res.status_code == 200:
                data = res.json()
                return data.get("display_name", "Address not found")
            else:
                _logger.warning(f"Geocoding API returned status {res.status_code}")
                return "Address lookup failed"

        except requests.exceptions.Timeout:
            _logger.error("Geocoding request timed out")
            return "Address lookup timed out"
        except Exception as e:
            _logger.error(f"Geocoding error: {str(e)}")
            return "Address lookup error"

    @http.route('/face_recognition', type='http', auth='user', website=True)
    def face_recognition_page(self):
        return request.render('hr_attendance_face_detection.face_recognition_page')

    @http.route('/face_recognition/check', type='json', auth='user', methods=['POST'], csrf=False)
    def check_in_out(self, image_data, latitude=None, longitude=None):
        try:
            _logger.info(f"Face recognition request from user {request.env.user.name}")

            company = request.env.user.company_id.sudo()
            allowed_locations = company.multi_location_ids

            if allowed_locations:  # if any locations configured → enforce check
                if not latitude or not longitude:
                    return {
                        "success": False,
                        "msg": "❌ Location (latitude & longitude) is required when geofencing is enabled"
                    }

                location_valid = False
                closest_distance = float('inf')
                closest_name = ""

                for loc in allowed_locations:
                    dist = self.calculate_distance_meters(
                        loc.face_attendance_latitude,
                        loc.face_attendance_longitude,
                        latitude,
                        longitude
                    )

                    if dist is not None and dist <= loc.face_attendance_radius:
                        location_valid = True
                        break

                    # Keep track of closest for better error message
                    if dist is not None and dist < closest_distance:
                        closest_distance = dist
                        closest_name = loc.name

                if not location_valid:
                    msg = "❌ You are not within any allowed attendance area."
                    if closest_distance != float('inf'):
                        msg += f"\nClosest location: {closest_name} ({closest_distance:.0f}m away)"
                    return {"success": False, "msg": msg}

            if not image_data:
                return {"success": False, "msg": "❌ No image data received"}

            if not image_data.startswith('data:image'):
                return {"success": False, "msg": "❌ Invalid image format"}

            # Decode uploaded image with proper error handling
            try:
                img_data = base64.b64decode(image_data.split(",")[1])
                img = np.array(Image.open(BytesIO(img_data)))

                # Validate image
                if img.size == 0:
                    return {"success": False, "msg": "❌ Empty image received"}

            except Exception as e:
                _logger.error(f"Image decoding error: {str(e)}")
                return {"success": False, "msg": "❌ Failed to process image"}

            # Extract face encodings with better error handling
            try:
                captured_encodings = face_recognition.face_encodings(img)
                if not captured_encodings:
                    return {"success": False, "msg": "❌ No face detected in image"}

                captured_encoding = captured_encodings[0]
                _logger.info("Face encoding extracted successfully")

            except Exception as e:
                _logger.error(f"Face encoding error: {str(e)}")
                return {"success": False, "msg": "❌ Face detection failed"}

            # Search for employees with face encodings
            employees = request.env['hr.employee'].sudo().search([
                ('face_encoding', '!=', False),
                ('active', '=', True)
            ])

            if not employees:
                return {"success": False, "msg": "❌ No employees with face encodings found"}

            # Compare faces with enhanced matching
            matched_employee = None
            best_match_distance = float('inf')

            for emp in employees:
                try:
                    # Decode stored face encoding
                    emp_encoding = np.frombuffer(
                        base64.b64decode(emp.face_encoding),
                        dtype=np.float64
                    )

                    # Calculate face distance (lower is better match)
                    face_distances = face_recognition.face_distance([emp_encoding], captured_encoding)
                    distance = face_distances[0]

                    # Use stricter tolerance and track best match
                    if distance < 0.5 and distance < best_match_distance:  # Stricter tolerance
                        best_match_distance = distance
                        matched_employee = emp

                except Exception as e:
                    _logger.error(f"Face comparison error for employee {emp.name}: {str(e)}")
                    continue

            if not matched_employee:
                return {"success": False, "msg": "⚠️ No matching employee found"}

            # Process attendance with database transaction
            try:
                with request.env.cr.savepoint():
                    # now = fields.Datetime.now()
                    now_utc = fields.Datetime.now()
                    now_user = fields.Datetime.context_timestamp(request.env.user, now_utc)
                    att_model = request.env['hr.attendance'].sudo()

                    # Get the last attendance record
                    last_att = att_model.search([
                        ('employee_id', '=', matched_employee.id)
                    ], limit=1, order='check_in desc')

                    # Get address (non-blocking)
                    address = self.get_address_from_coords(latitude, longitude)

                    # Determine if this is check-in or check-out
                    if last_att and not last_att.check_out:
                        # Check out
                        last_att.write({
                            'check_out': now_utc,
                            'check_out_latitude': latitude,
                            'check_out_longitude': longitude,
                            'check_out_address': address,
                        })

                        _logger.info(f"Check-out recorded for {matched_employee.name}")

                        return {
                            "success": True,
                            "msg": f"✅ Checked Out at {now_user.strftime('%H:%M')}",
                            "employee_name": matched_employee.name,
                            "location": address,
                            "action": "check_out"
                        }
                    else:
                        # Check in
                        att_record = att_model.create({
                            'employee_id': matched_employee.id,
                            'check_in': now_utc,
                            'check_in_latitude': latitude,
                            'check_in_longitude': longitude,
                            'check_in_address': address,
                        })

                        _logger.info(f"Check-in recorded for {matched_employee.name} (ID: {att_record.id})")

                        return {
                            "success": True,
                            "msg": f"✅ Checked In at {now_user.strftime('%H:%M')}",
                            "employee_name": matched_employee.name,
                            "location": address,
                            "action": "check_in"
                        }

            except Exception as e:
                _logger.error(f"Database error during attendance recording: {str(e)}")
                return {"success": False, "msg": "❌ Failed to record attendance"}

        except Exception as e:
            _logger.error(f"Unexpected error in face recognition: {str(e)}")
            return {"success": False, "msg": "❌ System error occurred"}
