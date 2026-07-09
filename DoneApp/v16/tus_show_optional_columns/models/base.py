from lxml import etree

from odoo import api, models


class Model(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """get_view([view_id | view_type='form'])

        Get the detailed composition of the requested view like model, view architecture

        :param int view_id: id of the view or None
        :param str view_type: type of the view to return if view_id is None ('form', 'tree', ...)
        :param dict options: boolean options to return additional features:
            - bool mobile: true if the web client is currently using the responsive mobile view
            (to use kanban views instead of list views for x2many fields)
        :return: composition of the requested view (including inherited views and extensions)
        :rtype: dict
        :raise AttributeError:

            * if the inherited view has unknown position to work with other than 'before', 'after', 'inside', 'replace'
            * if some tag other than 'position' is found in parent view

        :raise Invalid ArchitectureError: if there is view type other than form, tree, calendar, search etc... defined on the structure
        """
        self.check_access_rights("read")

        result = super().get_view(view_id, view_type, **options)
        is_optional_view = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("tus_show_optional_fields.is_optional_view", False)
        )
        if view_type == "tree" and is_optional_view:
            node = etree.fromstring(result["arch"])
            node.xpath("//tree")[0].set("is_optional_view", is_optional_view)
            result["arch"] = etree.tostring(node, encoding="unicode").replace("\t", "")
        return result
