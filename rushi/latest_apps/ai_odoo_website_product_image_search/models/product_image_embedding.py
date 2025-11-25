# Part of Odoo. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models, api
from ..models.product_Image_search import ImageSearchEngine
from odoo.fields import Domain
import logging
_logger = logging.getLogger(__name__)
ImageSearchEngine = ImageSearchEngine()


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    def _search_get_detail(self, website, order, options):
        res = super()._search_get_detail(website, order, options)

        if "product_ids" in options and options["product_ids"]:
            product_ids = options["product_ids"]
            if isinstance(product_ids, int):
                product_ids = [product_ids]
            res["base_domain"] = [Domain.AND([
                res["base_domain"][0],
                [("id", "in", product_ids)],
            ])]

        return res


class ProductImageEmbedding(models.Model):
    _name = 'product.image.embedding'
    _description = 'Product Image Embedding'
    _rec_name = 'name'
    _order = 'id desc'

    published = fields.Boolean('Published', default=False)
    name = fields.Char(string='Name', required=True, help="A short descriptive name for this embedding configuration.")
    model_id = fields.Many2one(comodel_name='ir.model', string='Model', required=True, ondelete='cascade', domain=[('model', 'in', ['product.product', 'product.template'])], default=lambda self: self._default_model_id(), help="Choose whether this embedding is for product templates or variants.")
    model = fields.Char(related='model_id.model', string='Model Technical Name', readonly=True, store=True, help="Technical model name (related field).")
    product_selection = fields.Selection([('all', 'All Products'), ('selected', 'Selected Products')], default='all',
                                         string='Select Product', required=True,
                                         help="Select the option for how you would like to train your model")
    selected_products_ids = fields.Many2many(string="Products", comodel_name='product.template',
                                             help="Select products for training")
    selected_variants_ids = fields.Many2many(string="Variants", comodel_name='product.product',
                                             help="Select variants for training")
    products_limit = fields.Integer(default=1000)
    product_show_limit = fields.Integer(string='Product Show Limit', default=10, help="Limit the number of similar products to display based on embedding.")
    extra_image = fields.Boolean(string='Extra Images', default=False, help="Whether to include additional gallery images for embedding.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('stored', 'Stored')
    ], default="draft", string='State', required=True)
    result_accuracy = fields.Selection([('low', 'Low'), ('standard', 'Standard'), ('high', 'High'), ('exact', 'Exact')],
                                       string='Result Accuracy',
                                       default='standard', required=True,
                                       help="The accuracy of the model's predictions based on the embeddings.")

    @api.model
    def _default_model_id(self):
        return self.env['ir.model'].search([('model', '=', 'product.template')], limit=1)

    def _get_table_name(self):
        table_name = '_'.join(self.name.split()) + f'_{self.id}'
        return table_name

    def tus_action_store_product_image_embeddings(self):
        table_name = self._get_table_name()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id SERIAL PRIMARY KEY,
            product_id INT,
            title TEXT,
            embedding FLOAT8[],
            record_type TEXT
        );
        """
        self.env.cr.execute(create_table_query)

        data_list = self.get_product_data()
        for rec in data_list:
            insert_query = f"""
                INSERT INTO "{table_name}" (product_id, title, embedding, record_type)
                VALUES (%s, %s, %s, %s)
            """
            self.env.cr.execute(insert_query, (
                rec['id'], rec['name'], rec['embedding'], rec.get('record_type', 'product')
            ))
        self.state = 'stored'
        self.published = True

    def tus_action_reset_to_draft(self):
        table_name = self._get_table_name()
        drop_query = f'DROP TABLE IF EXISTS "{table_name}"'
        self.env.cr.execute(drop_query)
        self.state = 'draft'
        self.published = False

    def get_product_data(self):
        data_list = []
        if self.product_selection == 'all':
            products = self.env[self.model].search([], limit=self.products_limit)
        else:
            products = self.selected_products_ids if self.model == 'product.template' else self.selected_variants_ids
        for product in products:
            product_id = product.id
            title = product.name
            image_data = product.image_128 or []
            if image_data:
                try:
                    embedding_array = ImageSearchEngine.compute_image_embedding_from_path(image_data)
                    data_list.append({
                        'id': product_id,
                        'name': title,
                        'embedding': embedding_array.tolist(),
                        'record_type': 'product'
                    })
                except Exception as e:
                    _logger.warning(f"Main image failed for {title}: {e}")

            if self.extra_image:
                image_ids = product.product_template_image_ids if self.model == 'product.template' else product.product_variant_image_ids
                for img in image_ids:
                    if img.image_1920:
                        try:
                            embedding_array = ImageSearchEngine.compute_image_embedding_from_path(img.image_1920)
                            data_list.append({
                                'id': product_id,
                                'name': title,
                                'embedding': embedding_array.tolist(),
                                'record_type': 'extra'
                            })
                        except Exception as e:
                            _logger.warning(f"Extra image failed for {title}: {e}")

        return data_list

