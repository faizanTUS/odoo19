/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, onMounted, toRaw, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { RAW_SYMBOL } from "@point_of_sale/app/models/related_models/utils";

export class ResetPopup extends Component {
    static template = "pos_password_reset.ResetPopup";
    static components = { Dialog };
    static props = {
        employee: Object,
        close: Function,
        confirmText: { type: String, optional: true },
        cancelText: { type: String, optional: true },
    };
    static defaultProps = {
        confirmText: _t("Confirm"),
        cancelText: _t("Discard"),
    };

    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.inputRef = useRef("password");
        onMounted(() => this.inputRef.el?.focus());
    }

    async onClickConfirmButton() {
        const pass = (this.inputRef.el?.value || "").trim();
        if (!pass) {
            this.notification.add(_t("Please enter a new password."), { type: "warning" });
            return;
        }
        if (!/^\d+$/.test(pass)) {
            this.notification.add(_t("PIN must only contain digits."), { type: "warning" });
            return;
        }

        const hashedPin = await this.orm.call("hr.employee", "pos_reset_pin", [
            [this.props.employee.id],
            pass,
        ]);
        // `_pin` is an extra field: read-only on the record, stored in raw data.
        toRaw(this.props.employee)[RAW_SYMBOL]._pin = hashedPin;

        this.props.close();
        this.dialog.add(AlertDialog, {
            title: _t("Success"),
            body: _t("Password updated successfully!"),
        });
    }

    close() {
        this.props.close();
    }
}
