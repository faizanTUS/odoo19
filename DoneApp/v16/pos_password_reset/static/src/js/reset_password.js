/**@odoo-module **/
import AbstractAwaitablePopup from "point_of_sale.AbstractAwaitablePopup";
import Registries from "point_of_sale.Registries";
import {isConnectionError} from "point_of_sale.utils";
import {_t} from "web.core";
import {useListener} from "@web/core/utils/hooks";
const {useState, onMounted} = owl;
const {renderToString} = require("@web/core/utils/render");
class ResetPopup extends AbstractAwaitablePopup {
    setup() {
        super.setup();
    }
    async confirm() {
        var pass = $("#password").val();
        var values = {};
        var currentId = this.props.currentId;

        if (pass) {
            values["pin"] = pass;
            values["currentId"] = currentId;
        }

        // Make an RPC call to update the password
        const temp_result = await this.rpc({
            model: "hr.employee",
            method: "custom_method",
            args: [[], values],
        });

        if (temp_result) {
            // Hash and update the password for all employees
            for (let i = 0; i < this.env.pos.employees.length; i++) {
                const user = this.env.pos.employees[i];
                const password = user.pass;
                const hashedPassword = Sha1.hash(pass);
                user.pin = hashedPassword;
            }
            this.showPopup("SuccessfullPopup", {});
        }

        this.env.posbus.trigger("close-popup", {
            popupId: this.props.id,
            response: {
                confirmed: false,
                payload: null,
            },
        });
    }
}

ResetPopup.template = "ResetPopup";
Registries.Component.add(ResetPopup);
