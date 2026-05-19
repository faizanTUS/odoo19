/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";


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

    init: function () {
        this._super.apply(this, arguments);
        this.notification = this.bindService("notification");
    },

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
        // Get product template ID from data attribute
        this.productTemplateId = this.$el.data('productTemplateId') || this.$el.closest('[data-product-template-id]').data('productTemplateId');
        this.priceUpdateTimeout = null;
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
        if (!colorId) {
            return;
        }
        if ($target.hasClass('active')) {
            this._hideColorSection(colorId);
        } else {
            this._showColorSection(colorId);
        }
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
            const value = parseFloat(this.value);
            const variantId = parseInt(this.dataset.variantId);
            if (variantId && value > 0) {
                lines.push({
                    product_id: variantId,
                    quantity: value,
                });
            }
        });
        return lines;
    },

    async _onSubmit(ev) {
        ev.preventDefault();
        const lines = this._collectLines();
        if (!lines.length) {
            this.notification.add(_t("Enter at least one quantity before adding to cart."), { type: 'warning' });
            return;
        }
        this._toggleProcessing(true);
        await rpc("/shop/cart/update_multi", { lines }).then((result) => {
            this._toggleProcessing(false);
            this._onSuccess(result);
        }).catch(() => {
            this._toggleProcessing(false);
            this.notification.add(_t("Could not update the cart. Please try again."), { type: 'warning' });
        });
    },

    _onClear(ev) {
        ev.preventDefault();
        this._getAllInputs().val(0);
        this._updatePricesAndTotal();
    },

    _onSuccess(result) {
        this._getAllInputs().val(0);
        this._updatePricesAndTotal();
        if (result && Object.prototype.hasOwnProperty.call(result, 'cart_quantity')) {
            this._updateMiniCart(result.cart_quantity);
        }
        this.notification.add(_t("Your selections were added to the cart."), { type: 'success' });
    },

    _updateMiniCart(quantity) {
        if (!this.$miniCartQty.length) {
            return;
        }
        this.$miniCartQty
            .toggleClass('d-none', !quantity)
            .text(quantity);
    },

    _toggleProcessing(state) {
        this.$submitBtn.prop('disabled', state);
        this.$submitBtn.toggleClass('disabled', state);
    },

    _onQtyChange(ev) {
        this._updatePricesAndTotal();
    },

    async _updatePricesAndTotal() {
        if (!this.$totalAmount.length || !this.productTemplateId) {
            this._updateTotal();
            return;
        }

        // Collect current quantities
        const quantities = {};
        const allInputs = this._getAllInputs();
        allInputs.each(function () {
            const variantId = parseInt(this.dataset.variantId);
            const qty = parseFloat(this.value) || 0;
            if (variantId && qty > 0) {
                quantities[variantId] = qty;
            }
        });

        const quantityKeys = Object.keys(quantities);
        if (!quantityKeys.length) {
            this._updateTotal();
            return;
        }

        const requestId = ++this._priceRequestId;
        try {
            const priceData = await rpc("/shop/matrix/get_prices", {
                product_template_id: this.productTemplateId,
                quantities: quantities,
            });

            if (requestId !== this._priceRequestId) {
                return;
            }

            this._getAllInputs().each(function () {
                const variantId = parseInt(this.dataset.variantId);
                if (variantId && priceData[variantId]) {
                    const newUnitPrice = priceData[variantId].unit_price;
                    $(this).data('unitPrice', newUnitPrice);
                    $(this).attr('data-unit-price', newUnitPrice);
                }
            });
        } catch (error) {
            if (requestId === this._priceRequestId) {
                console.error('Error fetching prices:', error);
            }
            return;
        }

        if (requestId === this._priceRequestId) {
            this._updateTotal();
        }
    },

    _updateTotal() {
        if (!this.$totalAmount.length) {
            return;
        }
        let total = 0;
        this._getAllInputs().each(function () {
            const qty = parseFloat(this.value) || 0;
            const unitPrice = parseFloat($(this).data('unitPrice')) || parseFloat(this.dataset.unitPrice) || 0;
            if (qty > 0 && !isNaN(unitPrice)) {
                total += qty * unitPrice;
            }
        });
        this._renderTotal(total);
    },

    _renderTotal(amount) {
        const decimals = this.currencyInfo.decimalPlaces;
        const formatter = new Intl.NumberFormat(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        });
        const formatted = formatter.format(amount || 0);
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
        if (!$section.length) {
            return;
        }
        $section.removeClass('d-none');
        this.$colorOptions.filter(`[data-color-id="${colorId}"]`).addClass('active');
    },

    _hideColorSection(colorId) {
        const $section = this.$colorSections.filter(`[data-color-id="${colorId}"]`);
        if (!$section.length) {
            return;
        }
        $section.find('.o_matrix_qty_input').val(0);
        $section.addClass('d-none');
        this.$colorOptions.filter(`[data-color-id="${colorId}"]`).removeClass('active');
    },

    _refreshPlaceholder() {
        const hasVisible = this.$colorSections.filter(':not(.d-none)').length > 0;
        this.$selectionPlaceholder.toggleClass('d-none', hasVisible);
    },

    _getAllInputs() {
        return this.$('.o_matrix_qty_input');
    },
});

