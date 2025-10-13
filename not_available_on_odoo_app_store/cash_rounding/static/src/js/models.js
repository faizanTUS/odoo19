import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosStore } from "@point_of_sale/app/services/pos_store";

patch(PosStore.prototype, {

    async processServerData() {
        await super.processServerData(...arguments);
        this.cash_rounding_list = this.data.records['account.cash.rounding']
    },
});

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        this.cash_rounding_list = this.cash_rounding_list
    },

    export_for_printing(){
        const json = super.export_for_printing(...arguments);
        json.cash_rounding_list =  this.cash_rounding_list;
        return json;
    },

});
