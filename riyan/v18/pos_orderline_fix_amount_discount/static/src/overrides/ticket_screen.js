/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { omit } from "@web/core/utils/objects";


patch(TicketScreen.prototype, {

    _getToRefundDetail(orderline) {
        let res = super._getToRefundDetail(...arguments)
        res.orderline.discount_amount = orderline.discount_amount
        omit(res.orderline, 'price')
        return res
    },

    _prepareRefundOrderlineOptions(toRefundDetail) {
        let res = super._prepareRefundOrderlineOptions(...arguments)
        const { qty, orderline } = toRefundDetail;
        res.discount_amount = orderline.discount_amount
        omit(res, 'price')
        return res
    },

});
