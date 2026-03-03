/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
//import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosStore } from "@point_of_sale/app/services/pos_store";

//import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { ClosePosPopup } from "@point_of_sale/app/components/popups/closing_popup/closing_popup";

import { ConnectionLostError } from "@web/core/network/rpc";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { parseFloat } from "@web/views/fields/parsers";
import { deduceUrl } from "@point_of_sale/utils";

/**
 * FIX: Blink / reload-loop when closing POS session.
 *
 * Root cause:
 *   closeSession() and closingSessionNotification() call location.reload()
 *   which reloads /pos/ui → server redirects → blink loop.
 *
 * Fix:
 *   Navigate directly to the Odoo backend instead of reloading.
 *   Since window.location.reload is read-only, we fully override the
 *   methods that call it.
 */

patch(PosStore.prototype, {
    redirectToBackend() {
        const menuId =
            typeof odoo !== "undefined" &&
            (
                odoo.pos_backend_menu_id ||
                odoo.__session_info__?.pos_backend_menu_id ||
                odoo.session_info?.pos_backend_menu_id
            );

        if (menuId) {
            window.location.href = `/odoo?menu_id=${menuId}`;
        } else {
            window.location.href = "/odoo/action-point_of_sale.action_client_pos_menu";
        }
    },

    async closingSessionNotification(data) {
        if (data.login_number == odoo.login_number) {
            return;
        }

        try {
            const paidOrderNotSynced = this.models["pos.order"].filter(
                (order) => order.state === "paid" && order.id !== "number"
            );
            this.addPendingOrder(paidOrderNotSynced.map((o) => o.id));
            await this.syncAllOrders({ throw: true });

            this.dialog.add(AlertDialog, {
                title: _t("Closing Session"),
                body: _t("The session is being closed by another user. You will be redirected."),
            });
        } catch {
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t(
                    "An error occurred while closing the session. Unsynced orders will be available in the next session."
                ),
            });
        } finally {
            const orders = this.models["pos.order"].filter((o) => typeof o.id === "number");
            for (const order of orders) {
                if (!order.finalized) {
                    order.state = "cancel";
                }
            }
        }

        // FIX: redirect to backend instead of location.reload()
        setTimeout(() => {
            this.redirectToBackend();
        }, 3000);
    },
});

patch(ClosePosPopup.prototype, {
    async closeSession() {
        this.pos._resetConnectedCashier();
        if (this.pos.config.customer_display_type === "proxy") {
            const proxyIP = this.pos.getDisplayDeviceIP();
            fetch(`${deduceUrl(proxyIP)}/hw_proxy/customer_facing_display`, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ params: { action: "close" } }),
            }).catch(() => {
                console.log("Failed to send data to customer display");
            });
        }

//        const syncSuccess = await this.pos.push_orders_with_closing_popup();
//        if (!syncSuccess) {
//            return;
//        }
        if (this.pos.config.cash_control) {
            const response = await this.pos.data.call(
                "pos.session",
                "post_closing_cash_details",
                [this.pos.session.id],
                {
                    counted_cash: parseFloat(
                        this.state.payments[this.props.default_cash_details.id].counted
                    ),
                }
            );
            if (!response.successful) {
                return this.handleClosingError(response);
            }
        }

        try {
            await this.pos.data.call("pos.session", "update_closing_control_state_session", [
                this.pos.session.id,
                this.state.notes,
            ]);
        } catch (error) {
            if (!error.data && error.data.message !== "This session is already closed.") {
                throw error;
            }
        }

        try {
            const bankPaymentMethodDiffPairs = this.props.non_cash_payment_methods
                .filter((pm) => pm.type == "bank")
                .map((pm) => [pm.id, this.getDifference(pm.id)]);
            const response = await this.pos.data.call(
                "pos.session",
                "close_session_from_ui",
                [this.pos.session.id, bankPaymentMethodDiffPairs],
                {
                    context: {
                        login_number: odoo.login_number,
                    },
                }
            );
            if (!response.successful) {
                return this.handleClosingError(response);
            }
            localStorage.removeItem(`pos.session.${odoo.pos_config_id}`);
            // FIX: redirect to backend instead of location.reload()
            this.pos.redirectToBackend();
        } catch (error) {
            if (error instanceof ConnectionLostError) {
                throw error;
            } else {
                await this.handleClosingControlError();
            }
        }
    },
});
