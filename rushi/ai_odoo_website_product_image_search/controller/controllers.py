# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
import json
import base64
from ..models.product_Image_search import ImageSearchEngine


class ImageSearchController(http.Controller):

    @http.route('/image_search/', type='http', auth='public', methods=['POST'], csrf=False)
    def search_product(self, **kwargs):
        image_file = request.httprequest.files.get('image')
        if image_file:
            image_data = image_file.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            published_mapping = request.env['product.image.embedding'].sudo().search([('published', '=', True)],
                                                                                     order='id desc', limit=1)
            if published_mapping.result_accuracy == 'low':
                max_threshold = 0.7
            elif published_mapping.result_accuracy == 'standard':
                max_threshold = 0.5
            elif published_mapping.result_accuracy == 'high':
                max_threshold = 0.4
            else:
                max_threshold = 0.3
            if not published_mapping:
                return {'error': 'No trained model available'}

            table_name = published_mapping._get_table_name()

            engine = ImageSearchEngine()
            response = engine.predict_with_python_similarity(
                image_data=image_b64,
                top_n=published_mapping.product_show_limit,
                max_distance_threshold=max_threshold,
                table_name=table_name
            )
            if response.get('status') == 'success':
                if response.get('status') == 'success' and response.get('closest_products'):
                    product_ids = [r.get('product_id') for r in response['closest_products'] if r.get('product_id')]
                    return json.dumps({'product_ids': product_ids})

            if response.get('status') == 'success' and not response.get('closest_products'):
                return json.dumps({'product_ids': []})

            return json.dumps({'error': 'Image processing failed or no similar product found.'})
