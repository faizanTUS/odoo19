/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { onMounted } from "@odoo/owl";

console.log("[DW] JS loaded");

patch(FormRenderer.prototype, "dynamic_warnings.FormRendererPatch", {

    setup() {
        this._super(...arguments);

        const self = this;

        onMounted(function () {
            self._loadWarnings();
        });
    },

    async _loadWarnings() {

        if (!this.props || !this.props.record) return;
        if (!this.props.record.resId) return;

        console.log("[DW] Fetching warnings");

        const result = await this.env.services.orm.call(
            "dynamic.warning.rule",
            "get_warnings_for_record",
            [this.props.record.resModel, this.props.record.resId]
        );

        console.log("[DW] Result:", result);

        this._renderWarnings(result);
    },

    _renderWarnings(warnings) {

        console.log("[DW] Render called");

        const anchor = document.querySelector(".o_form_sheet_bg");

        console.log("[DW] Anchor:", anchor);

        if (!anchor) return;

        const existing = document.getElementById("dynamic_warnings_container");
        if (existing) existing.remove();

        if (!warnings || !warnings.length) return;

        const container = document.createElement("div");
        container.id = "dynamic_warnings_container";
        container.className = "mb-3";

        warnings.forEach(function (w) {

            const alert = document.createElement("div");
            alert.className = "alert alert-" + (w.type || "warning");
            alert.textContent = w.message;

            container.appendChild(alert);
        });

        anchor.prepend(container);
    },

});