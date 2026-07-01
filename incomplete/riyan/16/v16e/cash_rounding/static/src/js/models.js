odoo.define('cash_rounding.models', function(require) {
	"use strict";

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const CashRoundingGlobalState = (PosGlobalState) => class CashRoundingGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.cash_rounding_list = loadedData['account.cash.rounding'];
        }
    }
    Registries.Model.extend(PosGlobalState, CashRoundingGlobalState);

    const cash_rounding_cust = (Order) => class cash_rounding_cust extends Order {
        init_from_JSON(json){
			super.init_from_JSON(...arguments);
            this.cash_rounding_list = json.cash_rounding_list;
		}

        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.cash_rounding_list = this.cash_rounding_list;
            return json
        }
        export_for_printing(){
			const json = super.export_for_printing(...arguments);
			json.cash_rounding_list =  this.cash_rounding_list;
			return json;
		}
    }
    Registries.Model.extend(Order, cash_rounding_cust);
});
