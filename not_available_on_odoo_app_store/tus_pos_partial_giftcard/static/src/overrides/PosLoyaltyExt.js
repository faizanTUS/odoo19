import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { _t } from "@web/core/l10n/translation";
import { PromoCodePopups } from "@tus_pos_partial_giftcard/app/PromoCodePopups";
// import { LoyaltyCard } from "@pos_loyalty/overrides/models/loyalty_card";
// import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
// import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { TextInputPopup } from "@point_of_sale/app/components/popups/text_input_popup/text_input_popup";

// Todo: no need for the patch in pos_store file fetchCoupons() patch, in odoo18 POS cart reset when reloaded, if odoo modifies something in future then we need this patch.

patch(PosStore.prototype, {
    async activateCode(code) {
        const order = this.getOrder();
        const rule = this.models["loyalty.rule"].find((rule) => {
            return rule.mode === "with_code" && (rule.promo_barcode === code || rule.code === code);
        });
        let claimableRewards = null;
        let coupon = null;
        if (rule) {
            const date_order = DateTime.fromSQL(order.date_order);
            if (
                rule.program_id.date_from &&
                date_order < rule.program_id.date_from.startOf("day")
            ) {
                return _t("That promo code program is not yet valid.");
            }
            if (rule.program_id.date_to && date_order > rule.program_id.date_to.endOf("day")) {
                return _t("That promo code program is expired.");
            }
            const program_pricelists = rule.program_id.pricelist_ids;
            if (
                program_pricelists.length > 0 &&
                (!order.pricelist_id || !program_pricelists.includes(order.pricelist_id.id))
            ) {
                return _t("That promo code program requires a specific pricelist.");
            }
            if (order.uiState.codeActivatedProgramRules.includes(rule.id)) {
                return _t("That promo code program has already been activated.");
            }
            order.uiState.codeActivatedProgramRules.push(rule.id);
            await this.orderUpdateLoyaltyPrograms();
            claimableRewards = order.getClaimableRewards(false, rule.program_id.id);
        } else {
            if (order._code_activated_coupon_ids.find((coupon) => coupon.code === code)) {
                return _t("That coupon code has already been scanned and activated.");
            }
            const customerId = order.getPartner() ? order.getPartner().id : false;
            const { successful, payload } = await this.data.call("pos.config", "use_coupon_code", [
                [this.config.id],
                code,
                order.date_order,
                customerId,
                order.pricelist_id ? order.pricelist_id.id : false,
            ]);
            if (successful) {
                // Log the result to inspect it
                const result = await makeAwaitable(this.dialog, PromoCodePopups, {
                    title: _t("Redeem Amount"),
                    placeholder: _t("Enter amount to Redeem"),
                    code: code,
                    partner_id: order.getPartner() ? order.getPartner().name : '',
                    points: payload.points,
                });

                console.log("CouponCode result:", result);

                // Check if result is undefined or if the user has discarded the popup
                if (!result) {
                    return _t("coupon amount redemption was cancelled.");
                }

                // Destructure with default values to avoid errors if result is undefined
                var { confirmed, amount } = result || {}; // Default to empty object if undefined

                if (confirmed && amount) {
                    coupon = this.models["loyalty.card"].create({
                        id: payload.coupon_id,
                        code: code,
                        program_id: this.models["loyalty.program"].get(payload.program_id),
                        partner_id: this.models["res.partner"].get(payload.partner_id),
                        points: parseInt(amount),
                        // TODO JCB: make the expiration_date work.
                    });
                    order.update({ _code_activated_coupon_ids: [["link", coupon]] });
                    await this.orderUpdateLoyaltyPrograms();
                    claimableRewards = order.getClaimableRewards(coupon.id);
                } else {
                    return _t("please try again.");
                }
            } else {
                return payload.error_message;
            }
        }

        if (claimableRewards && claimableRewards.length === 1) {
            if (
                claimableRewards[0].reward.reward_type !== "product" ||
                !claimableRewards[0].reward.multi_product
            ) {
                order._applyReward(claimableRewards[0].reward, claimableRewards[0].coupon_id);
                this.updateRewards();
            }
        }
        if (!rule && order.lines.length === 0 && coupon) {
            return _t(
                "Gift Card: %s\nBalance: %s",
                code,
                this.env.utils.formatCurrency(coupon.points)
            );
        }
        return true;
    }
});