/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { useService } from "@web/core/utils/hooks";

publicWidget.registry.PortalSaleQtyEdit = publicWidget.Widget.extend({
    selector: "#sales_order_table",
    events: {
        "change .js_portal_so_qty": "_onChangeQty",
        "click .js_portal_so_delete": "_onClickDelete",

    },
    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    /**
     * Read order + token from the table data attributes
     */
    _getContext: function () {
        const $table = this.$el;
        return {
            orderId: $table.data("order-id"),
            token: $table.data("token"),
        };
    },

    /**
     * On quantity change, call JSON route and then redirect
     */
    _onChangeQty: async function (ev) {
        ev.preventDefault();
        debugger;
        const $input = $(ev.currentTarget);
        const lineId = $input.data("line-id");
        const qty = $input.val();

        const ctx = this._getContext();
        if (!ctx.orderId || !lineId) {
            console.error("Missing orderId or lineId in portal SO table.");
            return;
        }

        try {
            const result = await this.rpc(`/my/orders/${ctx.orderId}/update_line_qty`, {
                line_id: lineId,
                quantity: qty,
                access_token: ctx.token,
            });

            if (!result || !result.success) {
                console.error("Error updating qty from portal:", result && result.error);
                return;
            }

            // redirect back to the portal order page
            if (result.redirect_url) {
                window.location.href = result.redirect_url;
            } else {
                window.location.reload();
            }
        } catch (error) {
            console.error("RPC error while updating qty:", error);
        }
    },

    _onClickDelete: async function (ev) {
        ev.preventDefault();

        const $btn = $(ev.currentTarget);
        const lineId = $btn.data("line-id");

        const ctx = this._getContext();
        if (!ctx.orderId || !lineId) {
            console.error("Missing orderId or lineId in portal SO table (delete).");
            return;
        }

        // Optional: confirmation
        if (!confirm("Remove this line from the quotation?")) {
            return;
        }

        try {
            const result = await this.rpc(`/my/orders/${ctx.orderId}/delete_line`, {
                line_id: lineId,
                access_token: ctx.token,
            });

            if (!result || !result.success) {
                console.error("Error deleting line from portal:", result && result.error);
                return;
            }

            if (result.redirect_url) {
                window.location.href = result.redirect_url;
            } else {
                window.location.reload();
            }
        } catch (error) {
            console.error("RPC error while deleting line:", error);
        }
    },

});

export default publicWidget.registry.PortalSaleQtyEdit;