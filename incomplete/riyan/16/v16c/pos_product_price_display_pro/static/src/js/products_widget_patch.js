odoo.define('pos_product_price_display_pro.ProductItem', function(require) {
    'use strict';

    const ProductItem = require('point_of_sale.ProductItem');
    const Registries = require('point_of_sale.Registries');

    const PriceDisplayProductItem = (ProductItem) => class extends ProductItem {

        get price() {
            const pos = this.env.pos;
            const product = this.props.product;

            if (pos.config.display_product_price_on_card === false) {
                return '';
            }

            // get_display_price already returns correct tax-included/excluded
            // price based on POS config — no manual tax calculation needed
            const basePrice = product.get_display_price(this.pricelist, 1);
            const formatted = pos.format_currency(basePrice, 'Product Price');

            if (product.to_weight) {
                return `${formatted}/${pos.units_by_id[product.uom_id[0]].name}`;
            }
            return formatted;
        }

        get priceLabel() {
            const pos = this.env.pos;
            if (!pos?.config) return '';
            if (pos.config.display_product_price_on_card === false) return '';
            return pos.config.iface_tax_included === 'total'
                ? pos.env._t('With Tax')
                : pos.env._t('Without Tax');
        }
    };

    Registries.Component.extend(ProductItem, PriceDisplayProductItem);
    return PriceDisplayProductItem;
});