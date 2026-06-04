# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo.exceptions import UserError
from odoo.tools.mimetypes import guess_mimetype
from odoo import api
import base64
import logging
import re
from copy import deepcopy
from io import BytesIO
from pypdf.generic import DictionaryObject, NameObject, NumberObject, FloatObject, ContentStream


from odoo import fields, models
from pypdf import PdfReader, PdfWriter, Transformation

_logger = logging.getLogger(__name__)
# PDF libraries (best-effort). This module should not crash if they are missing.
try:
    try:
        from pypdf import PdfReader, PdfWriter, Transformation
        from pypdf.errors import PdfReadError

        PYPDF_AVAILABLE = True
        USE_PYPDF = True
    except ImportError:
        from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter  # type: ignore
        from PyPDF2.utils import PdfReadError  # type: ignore

        PYPDF_AVAILABLE = True
        USE_PYPDF = False
except ImportError:
    PYPDF_AVAILABLE = False
    USE_PYPDF = False
    _logger.warning("PyPDF2/pypdf not found. Report PDF template merging will be skipped.")


try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    _logger.warning("Pillow not found. Image templates cannot be converted to PDF.")


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _resolve(self, obj):
        """Safely resolve pypdf IndirectObject to its actual object."""
        try:
            return obj.get_object()
        except Exception:
            return obj

    pdf_template = fields.Binary(
        string="PDF Template",
        help=(
            "Upload a PDF (or image) template to use as background, pre-printed layout, "
            "or watermark for QWeb PDF reports."
        ),
    )
    pdf_template_filename = fields.Char(string="PDF Template Filename")
    watermark_width_percent = fields.Float(
        string="Watermark Width (%)",
        default=40.0,
        help="Width of the watermark as percentage of page width",
    )
    watermark_opacity = fields.Float(
        string="Watermark Opacity",
        default=0.08,
        help="Opacity between 0 and 1",
    )
    watermark_position = fields.Selection(
        [
            ("center", "Center"),
            ("top", "Top Center"),
            ("bottom", "Bottom Center"),
        ],
        default="center",
    )
    template_type = fields.Selection(
        [
            ("background", "Background"),
            ("pre_printed", "Pre-Printed Layout"),
            ("watermark", "Watermark"),
        ],
        string="Template Type",
        default="background",
        help=(
            "Background: template under report content. "
            "Pre-Printed Layout: template under report content (same merging behavior). "
            "Watermark: template above report content."
        ),
    )

    # -------------------------------------------------------------------------
    # HTML rendering hook — strip footer/layout before PDF conversion
    # -------------------------------------------------------------------------

    def _render_qweb_html(self, *args, **kwargs):
        """
        Override to strip footer and header layout elements from the HTML
        before wkhtmltopdf processes it, when template_type = 'background'.
        This is the most reliable approach — no QWeb template xpath needed.
        """
        html_content, content_type = super()._render_qweb_html(*args, **kwargs)

        # Determine the report record
        report = self
        if not report or len(report) != 1:
            report_ref = args[0] if (args and isinstance(args[0], str)) else None
            report = self._resolve_report_record(report_ref)

        if (
            report
            and len(report) == 1
            and report.pdf_template
            and report.template_type == "background"
        ):
            html_content = self._strip_layout_from_html(html_content)

        return html_content, content_type

    def _strip_layout_from_html(self, html_content):
        """
        Remove header and footer blocks from the rendered HTML.
        Odoo wraps report content inside a structure like:
          <div class="header">...</div>
          <div class="article">...</div>   ← keep this
          <div class="footer">...</div>

        We strip header and footer divs so the PDF has no layout chrome —
        the background PDF template provides the letterhead/footer visually.
        """
        try:
            # Try lxml first (fastest, most accurate)
            try:
                from lxml import etree, html as lhtml
                tree = lhtml.fromstring(html_content if isinstance(html_content, str) else html_content.decode('utf-8', errors='replace'))

                # Remove all elements that are header or footer divs at any level
                # Odoo uses class="header", class="footer", class="header o_report_layout_..."
                for tag in tree.xpath('//*[contains(@class,"header") or contains(@class,"footer")]'):
                    # Only remove top-level layout wrappers, not content inside articles
                    parent = tag.getparent()
                    if parent is not None:
                        parent.remove(tag)

                result = lhtml.tostring(tree, encoding='unicode')
                return result.encode('utf-8') if isinstance(html_content, bytes) else result

            except ImportError:
                pass

            # Fallback: regex-based stripping (less precise but works)
            content_str = html_content if isinstance(html_content, str) else html_content.decode('utf-8', errors='replace')

            # Remove <div class="header ...">...</div> blocks
            content_str = re.sub(
                r'<div[^>]+class=["\'][^"\']*\bheader\b[^"\']*["\'][^>]*>.*?</div>',
                '',
                content_str,
                flags=re.DOTALL | re.IGNORECASE,
            )
            # Remove <div class="footer ...">...</div> blocks
            content_str = re.sub(
                r'<div[^>]+class=["\'][^"\']*\bfooter\b[^"\']*["\'][^>]*>.*?</div>',
                '',
                content_str,
                flags=re.DOTALL | re.IGNORECASE,
            )

            return content_str.encode('utf-8') if isinstance(html_content, bytes) else content_str

        except Exception:
            _logger.exception("Failed to strip layout from HTML for background template. Returning original HTML.")
            return html_content

    # -------------------------------------------------------------------------
    # Core hook
    # -------------------------------------------------------------------------

    def _render_qweb_pdf(self, *args, **kwargs):
        """Render QWeb PDF and merge template if configured."""

        report_ref = args[0] if (args and isinstance(args[0], str)) else None
        report = self
        if not report or len(report) != 1:
            report = self._resolve_report_record(report_ref)

        pdf_content, content_type = super(IrActionsReport, report)._render_qweb_pdf(*args, **kwargs)

        if content_type != "pdf":
            return pdf_content, content_type

        if not report or len(report) != 1 or not report.pdf_template:
            return pdf_content, content_type

        if not PYPDF_AVAILABLE:
            _logger.warning(
                "PDF library not available. Skipping template merge for report %s.",
                report.display_name,
            )
            return pdf_content, content_type

        try:
            template_data = base64.b64decode(report.pdf_template)
            template_pdf = report._convert_to_pdf_if_needed(
                template_data, report.pdf_template_filename
            )
            if not template_pdf:
                return pdf_content, content_type

            if report.template_type == "watermark":
                merged = report._apply_watermark_template(pdf_content, template_pdf)
            else:
                merged = report._apply_background_template(pdf_content, template_pdf)
            return merged, content_type
        except Exception:
            _logger.exception(
                "Failed to merge PDF template for report %s. Returning original output.",
                report.display_name,
            )
            return pdf_content, content_type

    def _resolve_report_record(self, report_ref):
        """Resolve ir.actions.report record from a report reference string."""
        Report = self.env["ir.actions.report"]
        if not report_ref:
            return Report.browse()

        if "." in report_ref:
            rec = self.env.ref(report_ref, raise_if_not_found=False)
            if rec and rec._name == "ir.actions.report":
                return rec

        if hasattr(Report, "_get_report_from_name"):
            try:
                rec = Report._get_report_from_name(report_ref)
                if rec:
                    return rec
            except Exception:
                pass

        return Report.search([("report_name", "=", report_ref)], limit=1)

    # -------------------------------------------------------------------------
    # Template ingestion
    # -------------------------------------------------------------------------

    def _convert_to_pdf_if_needed(self, template_data, filename=None):
        try:
            PdfReader(BytesIO(template_data))
            return template_data
        except Exception:
            pass

        if not PIL_AVAILABLE:
            return None

        try:
            img = Image.open(BytesIO(template_data))

            if img.mode in ("RGBA", "LA") or ("transparency" in img.info):
                img = img.convert("RGBA")
                white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                img = Image.alpha_composite(white_bg, img).convert("RGB")
            else:
                img = img.convert("RGB")

            out = BytesIO()
            # Keep behavior: 1-page PDF where page size = image size.
            # Your watermark scaling/position code will size/position it on A4 anyway.
            img.save(out, format="PDF", resolution=300)
            return out.getvalue()

        except Exception:
            _logger.exception("Failed to convert image template to PDF. filename=%s", filename)
            return None

    # -------------------------------------------------------------------------
    # PDF merge helpers
    # -------------------------------------------------------------------------

    def _pypdf_scale_page_to(self, page, target_width, target_height):
        """Scale a pypdf PageObject to exactly match the target dimensions."""
        if not USE_PYPDF:
            return page
        try:
            src_w = float(page.mediabox.width)
            src_h = float(page.mediabox.height)
            if not src_w or not src_h:
                return page

            sx = float(target_width) / src_w
            sy = float(target_height) / src_h
            page.add_transformation(Transformation().scale(sx, sy))

            # Normalize mediabox so merge coordinates align
            page.mediabox.lower_left = (0, 0)
            page.mediabox.upper_right = (float(target_width), float(target_height))
            return page
        except Exception:
            return page

    def _apply_background_template(self, report_pdf, template_pdf):
        """Template under report content."""
        try:
            report_reader = PdfReader(BytesIO(report_pdf))
            template_reader = PdfReader(BytesIO(template_pdf))
            if not getattr(template_reader, "pages", None):
                return report_pdf

            template_page = template_reader.pages[0]
            writer = PdfWriter()

            for report_page in report_reader.pages:
                if USE_PYPDF:
                    w = float(report_page.mediabox.width)
                    h = float(report_page.mediabox.height)
                    new_page = writer.add_blank_page(width=w, height=h)

                    t = self._pypdf_scale_page_to(deepcopy(template_page), w, h)
                    new_page.merge_page(t)
                    new_page.merge_page(report_page)
                else:
                    # Best-effort on PyPDF2 (no scaling support in this code path)
                    w = float(report_page.mediaBox.getWidth())
                    h = float(report_page.mediaBox.getHeight())
                    new_page = writer.addBlankPage(w, h)
                    new_page.mergePage(template_page)
                    new_page.mergePage(report_page)

            out = BytesIO()
            writer.write(out)
            return out.getvalue()
        except Exception:
            _logger.exception("Error applying background template")
            return report_pdf

    def _apply_watermark_template(self, report_pdf, template_pdf):
        try:
            report_reader = PdfReader(BytesIO(report_pdf))
            template_reader = PdfReader(BytesIO(template_pdf))
            if not template_reader.pages:
                return report_pdf

            template_page = template_reader.pages[0]
            writer = PdfWriter()

            opacity = float(self.watermark_opacity or 0.08)
            opacity = max(0.01, min(opacity, 1.0))

            width_pct = float(self.watermark_width_percent or 40.0) / 100.0
            width_pct = max(0.05, min(width_pct, 1.0))

            position = self.watermark_position or "center"

            for report_page in report_reader.pages:
                w = float(report_page.mediabox.width)
                h = float(report_page.mediabox.height)

                new_page = writer.add_blank_page(width=w, height=h)
                new_page.merge_page(report_page)

                wm = deepcopy(template_page)

                # --- Scale watermark to width %
                src_w = float(wm.mediabox.width) or 1.0
                src_h = float(wm.mediabox.height) or 1.0

                target_w = w * width_pct
                scale = target_w / src_w
                target_h = src_h * scale



                if position == "top":
                    tx = (w - target_w) / 2.0
                    ty = h - target_h - 40.0
                elif position == "bottom":
                    tx = (w - target_w) / 2.0
                    ty = 40.0
                else:
                    tx = (w - target_w) / 2.0
                    ty = (h - target_h) / 2.0

                wm.add_transformation(
                    Transformation().scale(scale, scale).translate(tx, ty)
                )

                # IMPORTANT: prevent clipping
                wm.mediabox.lower_left = (0, 0)
                wm.mediabox.upper_right = (w, h)
                wm.cropbox = wm.mediabox
                wm.trimbox = wm.mediabox

                # --- Apply opacity using ExtGState + ContentStream
                res = wm.get("/Resources") or DictionaryObject()
                res = self._resolve(res)
                if not isinstance(res, DictionaryObject):
                    res = DictionaryObject()

                extg = res.get("/ExtGState") or DictionaryObject()
                extg = self._resolve(extg)
                if not isinstance(extg, DictionaryObject):
                    extg = DictionaryObject()

                gs_name = NameObject("/GS_WATERMARK")
                gs = DictionaryObject()
                gs[NameObject("/Type")] = NameObject("/ExtGState")
                gs[NameObject("/ca")] = FloatObject(opacity)
                gs[NameObject("/CA")] = FloatObject(opacity)

                extg[gs_name] = gs
                res[NameObject("/ExtGState")] = extg
                wm[NameObject("/Resources")] = res

                contents = wm.get_contents()
                cs = ContentStream(contents, template_reader)

                # Wrap operations with q/gs/Q so opacity applies only to watermark drawing
                cs.operations.insert(0, ([], b"q"))
                cs.operations.insert(1, ([gs_name], b"gs"))
                cs.operations.append(([], b"Q"))

                wm[NameObject("/Contents")] = writer._add_object(cs)

                # Merge watermark on top
                new_page.merge_page(wm)

            out = BytesIO()
            writer.write(out)
            return out.getvalue()

        except Exception:
            _logger.exception("Error applying watermark template")
            return report_pdf

    @api.constrains("pdf_template", "template_type")
    def _check_watermark_format(self):
        for rec in self.filtered(lambda r: r.template_type == "watermark" and r.pdf_template):
            mimetype = guess_mimetype(base64.b64decode(rec.pdf_template))
            allowed = {"image/jpeg", "image/png"}
            if mimetype not in allowed:
                raise UserError(
                    "When 'Template Type' is 'Watermark' only JPG/JPEG and PNG images are allowed."
                )

from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    report_id = fields.Many2one(
        "ir.actions.report",
        string="Report",
    )

    hide_report_layout = fields.Boolean(
        compute="_compute_hide_report_layout",
        store=False,
    )

    @api.depends("report_id.template_type")
    def _compute_hide_report_layout(self):
        for rec in self:
            rec.hide_report_layout = (
                rec.report_id
                and rec.report_id.template_type == "background"
            )

