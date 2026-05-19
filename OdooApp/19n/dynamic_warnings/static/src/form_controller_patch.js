/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { onMounted } from "@odoo/owl";


patch(FormRenderer.prototype, {

    setup() {
        super.setup();

        var self = this;

        onMounted(function () {
            self._loadWarnings();
        });
    },

    async _loadWarnings() {
        if (!this.props || !this.props.record) return;
        if (!this.props.record.resId) return;

        const result = await this.env.services.orm.call(
            "dynamic.warning.rule",
            "get_warnings_for_record",
            [this.props.record.resModel, this.props.record.resId]
        );

        this._renderWarnings(result);
    },

    _renderWarnings(warnings) {
        var anchor = document.querySelector(".o_form_sheet_bg");

        if (!anchor) return;

        var existing = document.getElementById("dynamic_warnings_container");
        if (existing) existing.remove();

        if (!warnings || !warnings.length) return;

        var container = document.createElement("div");
        container.id = "dynamic_warnings_container";
        container.className = "mb-3";

        warnings.forEach(function (w) {
            var alert = document.createElement("div");
            alert.className = "alert alert-" + (w.type || "warning");
            alert.textContent = w.message;
            container.appendChild(alert);
        });

        anchor.prepend(container);
    },

});
