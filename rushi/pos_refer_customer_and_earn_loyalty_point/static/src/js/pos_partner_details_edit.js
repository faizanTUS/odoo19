/** @odoo-module */

import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

patch(PartnerDetailsEdit.prototype, {
    setup() {
        debugger;
        super.setup(...arguments);
        this.changes = useState({
            ...this.changes,
            ref_by_code : this.props.partner.ref_by_code || "",
        });
    },
    saveChanges() {
//        here on saveChanges method we can not call super so simplified that we can copy base js code and add our 2 new conditions at run time now our saveChanges method called
        const processedChanges = {};
        for (const [key, value] of Object.entries(this.changes)) {
            if (this.intFields.includes(key)) {
                processedChanges[key] = parseInt(value) || false;
            } else {
                processedChanges[key] = value;
            }
        }
        if (
            processedChanges.state_id &&
            this.pos.states.find((state) => state.id === processedChanges.state_id)
                .country_id[0] !== processedChanges.country_id
        ) {
            processedChanges.state_id = false;
        }

        if ((!this.props.partner.name && !processedChanges.name) || processedChanges.name === "") {
            return this.popup.add(ErrorPopup, {
               title: _t("Please Enter Valid Information"),
                body: _t(
                "A Customer Name Is Required"
            ),
            });
        }

         if ((!this.props.partner.email && !processedChanges.email) || processedChanges.email === "") {
            return this.popup.add(ErrorPopup, {
                title: _t("Please Enter Valid Information"),
                body: _t("A Customer Email Is Required"),
            });
        }
        if ((!this.props.partner.mobile && !processedChanges.mobile) || processedChanges.mobile === "") {
            return this.popup.add(ErrorPopup, {
                title: _t("Please Enter Valid Information"),
                body: _t("A Customer Mobile Is Required"),
            });
        }
        processedChanges.id = this.props.partner.id || false;
        this.props.saveChanges(processedChanges);
    },

});