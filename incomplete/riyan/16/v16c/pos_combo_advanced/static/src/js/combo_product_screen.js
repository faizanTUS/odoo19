odoo.define('pos_combo_advanced.ComboProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');

    const ComboProductScreen = (ProductScreen) => class extends ProductScreen {

        async _clickProduct(event) {
            const product = event.detail;

            // If it's a combo product, show our popup first
            if (product.is_combo_product) {
                await this._handleComboProduct(product);
                return;
            }

            // Otherwise normal behavior
            return super._clickProduct(event);
        }

        async _handleComboProduct(product) {
            const { confirmed, payload } = await Gui.showPopup(
                'SelectComboProductsPopup',
                { product }
            );

            if (!confirmed || !payload || payload.length === 0) return;

            const order = this.env.pos.get_order();

            // Build a description string summarising chosen combo items
            // e.g.  "Simple Pen x1, Large Cabinet x5"
            const comboDescription = payload
                .map(item => `${item.product.display_name} x${item.qty}`)
                .join(', ');

            // Add the combo parent product as ONE line with the combo description
            order.add_product(product, {
                quantity: 1,
                // 'description' appended to product name in parentheses via get_full_product_name()
                description: comboDescription,
                merge: false,   // never merge with existing lines
            });
        }
    };

    Registries.Component.extend(ProductScreen, ComboProductScreen);
    return ComboProductScreen;
});