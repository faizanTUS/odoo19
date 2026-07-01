odoo.define('pos_combo_advanced.custom_orderline', function(require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    // No need to extend PosGlobalState at all!
    // pos_combo_options is already inside each product object.

    const CustomOrderline = (Orderline) => class extends Orderline {

        get isComboProduct() {
            return this.props.line.get_product().is_combo_product || false;
        }

        get comboLines() {
            const product = this.props.line.get_product();
            // Use pos_combo_options injected directly on the product
            return product.pos_combo_options || [];
        }
    };

    Registries.Component.extend(Orderline, CustomOrderline);
    return CustomOrderline;
});