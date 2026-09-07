odoo.define("pos_password_reset.SuccessfullPopup", function (require) {
    "use strict";
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const {_lt} = require("@web/core/l10n/translation");

    class SuccessfullPopup extends AbstractAwaitablePopup {
        async confirm() {
            super.confirm();
        }
    }

    SuccessfullPopup.template = "SuccessfullPopup";
    SuccessfullPopup.defaultProps = {
        confirmText: _lt("Ok"),
        title: _lt("Success"),
    };
    Registries.Component.add(SuccessfullPopup);
    return SuccessfullPopup;
});
