odoo.define("pos_password_reset", function (require) {
    "use strict";

    const SelectionPopup = require("point_of_sale.SelectionPopup");
    const Registries = require("point_of_sale.Registries");

    const SelectionPopupTus = (SelectionPopup) =>
        class extends SelectionPopup {
            resetbutton(ev) {
                var button = event.target;
                if (
                    $(button).hasClass("btn-reset") ||
                    $(button).closest(".btn-reset").length
                ) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    this.showPopup("ResetPopup", {currentId: ev.currentTarget.id});
                }
            }
        };

    Registries.Component.extend(SelectionPopup, SelectionPopupTus);

    return SelectionPopup;
});
