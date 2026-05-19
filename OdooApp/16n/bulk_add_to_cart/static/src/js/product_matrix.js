/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import rpc from "web.rpc";
import core from "web.core";

const _t = core._t;

publicWidget.registry.ProductMatrix = publicWidget.Widget.extend({
    selector: '.o_color_size_matrix',
    events: {
        'click .o_matrix_show_colors_btn': '_onToggleColorPalette',
        'click .o_matrix_color_option': '_onPickColor',
        'click .o_matrix_remove_color_btn': '_onRemoveColor',
        'click .o_matrix_submit_btn': '_onSubmit',
        'click .o_matrix_clear_btn': '_onClear',
        'change .o_matrix_qty_input': '_onQtyChange',
    },

    /*  ----  NO init()  ----  */

    start() {
        this.$submitBtn = this.$('.o_matrix_submit_btn');
        this.$miniCartQty = $('.my_cart_quantity');
        this.$colorPalette = this.$('.o_matrix_color_palette');
        this.$colorOptions = this.$('.o_matrix_color_option');
        this.$sectionsWrapper = this.$('.o_matrix_color_sections');
        this.$colorSections = this.$('.o_matrix_color_section');
        this.$selectionPlaceholder = this.$('.o_matrix_selection_placeholder');
        this.$totalAmount = this.$('.o_matrix_total_amount');
        this.currencyInfo = {
            symbol: this.$totalAmount.data('currencySymbol') || '',
            position: this.$totalAmount.data('currencyPosition') || 'after',
            decimalPlaces: parseInt(this.$totalAmount.data('decimalPlaces')) || 2,
        };
        this.productTemplateId = this.$el.data('productTemplateId') ||
                                 this.$el.closest('[data-product-template-id]').data('productTemplateId');
        this._priceRequestId = 0;
        this._refreshPlaceholder();
        this._updatePricesAndTotal();
        return this._super(...arguments);
    },

    _onToggleColorPalette(ev) {
        ev.preventDefault();
        this.$colorPalette.toggleClass('d-none');
    },

    _onPickColor(ev) {
        ev.preventDefault();
        const $target = $(ev.currentTarget);
        const colorId = $target.data('colorId');
        if (!colorId) return;
        $target.hasClass('active') ? this._hideColorSection(colorId)
                                   : this._showColorSection(colorId);
        this._refreshPlaceholder();
        this._updatePricesAndTotal();
    },

    _onRemoveColor(ev) {
        ev.preventDefault();
        const colorId = $(ev.currentTarget).data('colorId');
        this._hideColorSection(colorId);
        this._refreshPlaceholder();
        this._updatePricesAndTotal();
    },

    _collectLines() {
        const lines = [];
        this._getAllInputs().each(function () {
            const qty = parseFloat(this.value);
            const variantId = parseInt(this.dataset.variantId);
            if (variantId && qty > 0) {
                lines.push({ product_id: variantId, quantity: qty });
            }
        });
        return lines;
    },

    async _onSubmit(ev) {
        ev.preventDefault();
        const lines = this._collectLines();
        if (!lines.length) {
            this.displayNotification({ message: _t("Enter at least one quantity before adding to cart."), type: 'info' });
            return;
        }
        this._toggleProcessing(true);
        try {
            const result = await rpc.query({
                route: '/shop/cart/update_multi',
                params: { lines },
            });
            this._toggleProcessing(false);
            this._onSuccess(result);
        } catch (err) {
            this._toggleProcessing(false);
            this.displayNotification({ message: _t("Could not update the cart. Please try again."), type: 'warning' });
        }
    },

    _onClear(ev) {
        ev.preventDefault();
        this._getAllInputs().val(0);
        this._updatePricesAndTotal();
        this.displayNotification({ message: _t("The selected quantity has been cleared."), type: 'warning' });

    },

    _onSuccess(result) {
        this._getAllInputs().val(0);
        this._updatePricesAndTotal();
        if (result && Object.prototype.hasOwnProperty.call(result, 'cart_quantity')) {
            this._updateMiniCart(result.cart_quantity);
        }
        this.displayNotification({ message: _t("Your selections were added to the cart."), type: 'success' });
    },

    _updateMiniCart(quantity) {
        if (!this.$miniCartQty.length) return;
        this.$miniCartQty.toggleClass('d-none', !quantity).text(quantity);
    },

    _toggleProcessing(state) {
        this.$submitBtn.prop('disabled', state).toggleClass('disabled', state);
    },

    _onQtyChange() { this._updatePricesAndTotal(); },

    async _updatePricesAndTotal() {
        if (!this.$totalAmount.length || !this.productTemplateId) {
            this._updateTotal(); return;
        }
        const quantities = {};
        this._getAllInputs().each(function () {
            const variantId = parseInt(this.dataset.variantId);
            const qty = parseFloat(this.value) || 0;
            if (variantId && qty > 0) quantities[variantId] = qty;
        });
        if (!Object.keys(quantities).length) { this._updateTotal(); return; }

        const requestId = ++this._priceRequestId;
        try {
            const priceData = await rpc.query({
                route: '/shop/matrix/get_prices',
                params: { product_template_id: this.productTemplateId, quantities },
            });
            if (requestId !== this._priceRequestId) return;

            this._getAllInputs().each(function () {
                const variantId = parseInt(this.dataset.variantId);
                if (variantId && priceData[variantId]) {
                    const unitPrice = priceData[variantId].unit_price;
                    $(this).data('unitPrice', unitPrice).attr('data-unit-price', unitPrice);
                }
            });
        } catch (e) {
            if (requestId === this._priceRequestId) console.error('Error fetching prices:', e);
            return;
        }
        if (requestId === this._priceRequestId) this._updateTotal();
    },

    _updateTotal() {
        if (!this.$totalAmount.length) return;
        let total = 0;
        this._getAllInputs().each(function () {
            const qty  = parseFloat(this.value) || 0;
            const unit = parseFloat($(this).data('unitPrice')) || parseFloat(this.dataset.unitPrice) || 0;
            if (qty > 0 && !isNaN(unit)) total += qty * unit;
        });
        this._renderTotal(total);
    },

    _renderTotal(amount) {
        const decimals = this.currencyInfo.decimalPlaces;
        const formatted = new Intl.NumberFormat(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        }).format(amount || 0);
        const symbol = this.currencyInfo.symbol;
        const position = this.currencyInfo.position;
        this.$totalAmount.text(
            position === 'before'
                ? `${symbol}${symbol ? ' ' : ''}${formatted}`.trim()
                : `${formatted}${symbol ? ' ' : ''}${symbol}`.trim()
        );
    },

    _showColorSection(colorId) {
        const $section = this.$colorSections.filter(`[data-color-id="${colorId}"]`);
        if (!$section.length) return;
        $section.removeClass('d-none');
        this.$colorOptions.filter(`[data-color-id="${colorId}"]`).addClass('active');
    },

    _hideColorSection(colorId) {
        const $section = this.$colorSections.filter(`[data-color-id="${colorId}"]`);
        if (!$section.length) return;
        $section.find('.o_matrix_qty_input').val(0);
        $section.addClass('d-none');
        this.$colorOptions.filter(`[data-color-id="${colorId}"]`).removeClass('active');
    },

    _refreshPlaceholder() {
        const hasVisible = this.$colorSections.filter(':not(.d-none)').length > 0;
        this.$selectionPlaceholder.toggleClass('d-none', hasVisible);
    },

    _getAllInputs() { return this.$('.o_matrix_qty_input'); },
});