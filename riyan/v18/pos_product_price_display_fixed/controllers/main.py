# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PosManifestFix(http.Controller):
    """
    Fix the PWA manifest icon error in POS.

    The default Odoo POS manifest at /pos/web.manifest references
    /web/static/img/odoo-icon-192x192.png which may be missing or
    inaccessible when running POS on a non-standard port, causing:
      "Error while trying to use the following icon from the Manifest:
       http://localhost:XXXX/web/static/img/odoo-icon-192x192.png
       (Download error or resource isn't a valid image)"

    This controller serves a corrected manifest that points to icons
    bundled with this module, which are always available.
    """

    @http.route("/pos/web.manifest", type="http", auth="public", methods=["GET"])
    def pos_manifest_fix(self, **kwargs):
        """Override the POS PWA manifest to use correct icon paths."""
        base_url = request.httprequest.host_url.rstrip("/")

        manifest = {
            "name": "Odoo Point of Sale",
            "short_name": "POS",
            "description": "Odoo Point of Sale Application",
            "start_url": "/pos/ui",
            "display": "fullscreen",
            "background_color": "#714BB4",
            "theme_color": "#714BB4",
            "icons": [
                {
                    "src": f"{base_url}/pos_product_price_display_fixed/static/img/pos-icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": f"{base_url}/pos_product_price_display_fixed/static/img/pos-icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
        }

        return request.make_response(
            json.dumps(manifest),
            headers=[
                ("Content-Type", "application/manifest+json"),
                ("Cache-Control", "no-cache"),
            ],
        )
