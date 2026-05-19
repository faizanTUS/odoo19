# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import base64
import io
import re
import zipfile
import logging
_logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ImportError:
    Image = None

from odoo import api, fields, models, _
from odoo.exceptions import UserError


def _slugify(text):
    text = text or ""
    text = text.strip()
    text = re.sub(r"[\\/*?\"<>|:]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text or "employee"


class EmployeeImageExportWizard(models.TransientModel):
    _name = "employee.image.export.wizard"
    _description = "Employee Image Export Wizard"

    # Selection mode
    selection_mode = fields.Selection(
        [
            ("context", "Selected records in list view"),
            ("domain", "Domain filter"),
            ("all", "All employees"),
        ],
        string="Employee Selection Mode",
        default="context",
        required=True,
    )

    employee_domain = fields.Char(
        string="Employee Domain",
        help="Domain on hr.employee. Example: [('department_id.name', '=', 'Sales')]",
    )

    include_archived = fields.Boolean(
        string="Include Archived Employees",
        default=False,
    )

    # Naming
    naming_mode = fields.Selection(
        [
            ("name", "Employee Name"),
            ("identification", "Identification Number"),
            ("id", "Record ID"),
            ("custom", "Custom Pattern"),
        ],
        string="Naming Mode",
        default="name",
        required=True,
    )

    custom_pattern = fields.Char(
        string="Custom Filename Pattern",
        help="Use placeholders: {name}, {id}, {identification_id}, {work_email}, {work_phone}. "
             "Extension will be added automatically.",
    )

    # Image options
    image_field = fields.Selection(
        [
            ("image_1920", "Main Image (image_1920)"),
            ("image_1024", "Medium (image_1024)"),
            ("image_512", "Small (image_512)"),
            ("image_256", "Very Small (image_256)"),
        ],
        string="Image Field",
        default="image_1920",
        required=True,
    )

    resize_enabled = fields.Boolean(string="Resize Images")
    resize_width = fields.Integer(string="Width (px)", default=0)
    resize_height = fields.Integer(string="Height (px)", default=0)
    keep_ratio = fields.Boolean(string="Keep Aspect Ratio", default=True)

    output_format = fields.Selection(
        [
            ("original", "Keep Original"),
            ("PNG", "PNG"),
            ("JPEG", "JPEG"),
        ],
        string="Output Format",
        default="original",
        required=True,
    )

    # Result
    zip_file = fields.Binary(string="Zip File", readonly=True)
    zip_filename = fields.Char(string="File Name", readonly=True, default="employee_images_export.zip")
    state = fields.Selection(
        [("draft", "Draft"), ("generated", "Generated")],
        default="draft",
        readonly=True,
    )

    def _get_employees(self):
        self.ensure_one()
        Employee = self.env["hr.employee"].sudo()

        domain = []
        if self.include_archived:
            domain.append(('active', 'in', (False, True)))
        if not self.include_archived:
            domain.append(("active", "=", True))

        if self.selection_mode == "context":
            active_ids = self.env.context.get("active_ids") or []
            if not active_ids:
                raise UserError(_("No employees selected in list view."))
            domain.append(("id", "in", active_ids))

        elif self.selection_mode == "domain":
            if not self.employee_domain:
                raise UserError(_("Please define a domain for employee selection."))
            try:
                extra_domain = eval(self.employee_domain, {"__builtins__": None}, {})
                if not isinstance(extra_domain, (list, tuple)):
                    raise ValueError
            except Exception:
                raise UserError(_("Invalid domain expression. Please check the syntax."))
            domain += extra_domain

        elif self.selection_mode == "all":
            # only domain is active / archived
            pass

        employees = Employee.search(domain)
        if not employees:
            raise UserError(_("No employees found for the given criteria."))
        return employees

    def _build_filename(self, employee, ext):
        self.ensure_one()
        mode = self.naming_mode

        if mode == "name":
            base = employee.name or "employee"
        elif mode == "identification":
            base = employee.identification_id or str(employee.id)
        elif mode == "id":
            base = str(employee.id)
        else:
            # custom pattern
            pattern = self.custom_pattern or "{name}_{id}"
            base = pattern.format(
                name=employee.name or "",
                id=employee.id,
                identification_id=employee.identification_id or "",
                work_email=employee.work_email or "",
                work_phone=employee.work_phone or "",
            )

        base = _slugify(base)
        return f"{base}.{ext.lower()}"

    def _process_image(self, raw_bytes):
        """
        Safely process the raw image bytes.
        Converts, resizes, and returns (processed_bytes, extension).
        Ensures no PIL crash occurs.
        """
        from PIL import Image
        import io

        try:
            # Try opening the image safely
            img = Image.open(io.BytesIO(raw_bytes))
            img.load()  # Force PIL to validate image
        except Exception as e:
            _logger.warning("Invalid image skipped: %s", e)
            return None, None

        # Convert to RGB if required
        if img.mode not in ("RGB", "RGBA"):
            try:
                img = img.convert("RGB")
            except Exception as e:
                _logger.warning("Failed to convert image mode: %s", e)
                return None, None

        # Resize if enabled
        if self.resize_enabled and self.resize_width and self.resize_height:
            try:
                if self.keep_ratio:
                    img.thumbnail((self.resize_width, self.resize_height))
                else:
                    img = img.resize((self.resize_width, self.resize_height))
            except Exception as e:
                _logger.warning("Image resize error: %s", e)
                return None, None

        # Determine output format
        output_format = (self.output_format or "original").lower()

        if output_format == "original":
            ext = img.format.lower() if img.format else "jpg"
            img_format = img.format or "JPEG"
        else:
            ext = output_format
            img_format = output_format.upper()

        # Save final processed image
        try:
            buffer = io.BytesIO()
            img.save(buffer, format=img_format)
            return buffer.getvalue(), ext
        except Exception as e:
            _logger.warning("Image saving failed: %s", e)
            return None, None

    def action_generate_zip(self):
        self.ensure_one()
        employees = self._get_employees()

        image_field = self.image_field or "image_1920"
        zip_buffer = io.BytesIO()
        file_count = 0

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for emp in employees:
                image = emp[image_field]

                if not image:
                    continue  # Skip employees without images

                # Decode safely
                try:
                    raw_bytes = base64.b64decode(image)
                except Exception as e:
                    _logger.warning("Base64 decode failed for employee %s: %s", emp.id, e)
                    continue

                # Process image
                processed_bytes, ext = self._process_image(raw_bytes)
                if not processed_bytes or not ext:
                    continue  # Skip invalid or unprocessable images

                # Build file name
                filename = self._build_filename(emp, ext)

                # Add file to zip
                try:
                    zf.writestr(filename, processed_bytes)
                    file_count += 1
                except Exception as e:
                    _logger.warning("Failed writing %s: %s", filename, e)

        if file_count == 0:
            raise UserError(_("No employee images found or all images were invalid."))

        # Write ZIP to wizard fields
        zip_value = zip_buffer.getvalue()
        self.write({
            "zip_file": base64.b64encode(zip_value),
            "zip_filename": "employee_images_export.zip",
            "state": "generated",
        })

        # Create log entry
        params_summary = (
            f"selection_mode={self.selection_mode}, "
            f"include_archived={self.include_archived}, "
            f"image_field={self.image_field}, "
            f"resize_enabled={self.resize_enabled}, "
            f"resize_width={self.resize_width}, "
            f"resize_height={self.resize_height}, "
            f"keep_ratio={self.keep_ratio}, "
            f"output_format={self.output_format}, "
            f"naming_mode={self.naming_mode}"
        )

        self.env["employee.image.export.log"].sudo().create({
            "name": "Employee image export",
            "employee_count": len(employees),
            "file_size": len(zip_value),
            "params_summary": params_summary,
        })

        return {
            "name": _("Export Employee Images"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }


    def action_download(self):
        self.ensure_one()
        if not self.zip_file:
            raise UserError(_("No zip file generated yet."))
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content?model=%s&id=%s&field=zip_file&filename=%s&download=true"
                   % (self._name, self.id, self.zip_filename or "employee_images_export.zip"),
            "target": "self",
        }
