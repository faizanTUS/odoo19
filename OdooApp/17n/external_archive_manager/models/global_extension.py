# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _
from .archive_mixin import ExternalArchiveMixin


class BaseModelExternalArchive(models.AbstractModel):
    _inherit = "base"

    # Explicitly assign mixin methods to make them available globally on all models
    _archive_config_for_model = ExternalArchiveMixin._archive_config_for_model
    _active_db_config = ExternalArchiveMixin._active_db_config
    _odoo_db_uuid = ExternalArchiveMixin._odoo_db_uuid

    action_external_offload = ExternalArchiveMixin.action_external_offload
    action_external_retrieve = ExternalArchiveMixin.action_external_retrieve
    action_external_delete = ExternalArchiveMixin.action_external_delete

    _external_offload_one = ExternalArchiveMixin._external_offload_one
    _external_retrieve_one = ExternalArchiveMixin._external_retrieve_one
    _external_delete_one = ExternalArchiveMixin._external_delete_one