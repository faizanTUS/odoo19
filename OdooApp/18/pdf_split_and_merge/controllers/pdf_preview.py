# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Shared PDF page preview helpers for JSON controller responses."""
import base64
import io

from PIL import Image


def page_jpeg_data_url(page, dpi=120, jpeg_quality=85):
    """Render a PyMuPDF page to a JPEG data URL for browser previews.

    :param page: fitz.Page
    :return: tuple (data_url, width_px, height_px)
    """
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    img_bytes = io.BytesIO()
    Image.frombytes("RGB", [pix.width, pix.height], pix.samples).save(
        img_bytes, format="JPEG", quality=jpeg_quality
    )
    b64 = base64.b64encode(img_bytes.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}", pix.width, pix.height
