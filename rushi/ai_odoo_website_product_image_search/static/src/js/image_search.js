/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";
import { ImageSearchDialog } from "./image_search_popup";

publicWidget.registry.ImageSearch = publicWidget.Widget.extend({
    selector: '.o_searchbar_form',
    events: {
        'click .o_search_image_button': '_onClickSearchImage',
    },

    init: function () {
        this._super(...arguments);
        this.dialog = this.bindService("dialog");
    },

    _onClickSearchImage: async function (ev) {
        this.dialog.add(ImageSearchDialog);
    },
});
