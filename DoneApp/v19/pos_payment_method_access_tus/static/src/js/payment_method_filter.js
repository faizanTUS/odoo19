/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { onWillStart } from "@odoo/owl";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onWillStart(async () => {
            try {
                const result = await this.env.services.orm.call(
                    "pos.payment.method",
                    "get_allowed_payment_method_ids",
                    [],
                    {}
                );
                const currentUserId = result.current_user_id;
                const userIdsMap = result.user_ids_map;
                this.payment_methods_from_config = this.payment_methods_from_config.filter((method) => {
                    const userIds = userIdsMap[method.id] || [];
                    if (userIds.length === 0) return true;
                    return userIds.includes(currentUserId);
                });
            } catch (e) {
                // Error handled silently
            }
        });
    },
});