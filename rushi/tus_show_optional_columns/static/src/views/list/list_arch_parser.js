/** @odoo-module **/

import {ListArchParser} from "@web/views/list/list_arch_parser";
import {patch} from "@web/core/utils/patch";
import { visitXML } from "@web/core/utils/xml";

patch(ListArchParser.prototype,  {
    parse(arch, models, modelName) {
        var is_optional_view = false;
        visitXML(arch, (node) => {
            if (node.tagName === "list") {
                is_optional_view = node.getAttribute("is_optional_view") || false;
            }
        });
        const result = super.parse(...arguments)
        if(result.columns.length) {
            result.columns.map(function (column) {
                if (!column.optional && is_optional_view) {
                    column.optional = "show";
                }
            })
        }
        return result;
    },
});
