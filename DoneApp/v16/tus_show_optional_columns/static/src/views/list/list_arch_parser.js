/** @odoo-module **/

import {ListArchParser} from "@web/views/list/list_arch_parser";
import {patch} from "@web/core/utils/patch";

patch(ListArchParser.prototype, "list_arch_parser_optional_show", {
    parse(arch, models, modelName) {
        var is_optional_view = false;
        this.visitXML(arch, (node) => {
            if (node.tagName === "tree") {
                is_optional_view = node.getAttribute("is_optional_view") || false;
            }
        });
        const result = this._super.apply(this, arguments);
        _.map(result.columns || [], function (column) {
            if (!column.optional && is_optional_view) {
                column.optional = "show";
            }
        });
        return result;
    },
});
