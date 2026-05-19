odoo.define('pos_combo_advanced.ComboProductItem', function (require) {
    'use strict';

    const ProductItem = require('point_of_sale.ProductItem');
    const Registries = require('point_of_sale.Registries');

    const ComboProductItem = (ProductItem) => class extends ProductItem {
        get isComboProduct() {
            return this.props.product.is_combo_product || false;
        }
    };

    Registries.Component.extend(ProductItem, ComboProductItem);
    return ComboProductItem;
});
