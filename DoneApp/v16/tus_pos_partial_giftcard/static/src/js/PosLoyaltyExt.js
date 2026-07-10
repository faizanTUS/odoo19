/** @odoo-module **/
import {Order} from "point_of_sale.models";
import Registries from "point_of_sale.Registries";
import {Gui} from "point_of_sale.Gui";
import core from "web.core";
import session from "web.session";
import {PosLoyaltyCard} from "@pos_loyalty/js/Loyalty";

const _t = core._t;

const PosLoyaltyOrderExt = (Order) =>
    class PosLoyaltyOrderExt extends Order {
        async _activateCode(code) {
            const rule = this.pos.rules.find((rule) => {
                return (
                    rule.mode === "with_code" &&
                    (rule.promo_barcode === code || rule.code === code)
                );
            });
            let claimableRewards = null;
            if (rule) {
                if (this.codeActivatedProgramRules.includes(rule.id)) {
                    return _t("That promo code program has already been activated.");
                }
                this.codeActivatedProgramRules.push(rule.id);
                await this._updateLoyaltyPrograms();
                claimableRewards = this.getClaimableRewards(false, rule.program_id.id);
            } else {
                let scanned = this.codeActivatedCoupons.find(
                    (coupon) => coupon.code === code
                );
                if (
                    this.codeActivatedCoupons.find((coupon) => coupon.code === code) &&
                    scanned.balance === 0
                ) {
                    return _t(
                        "That coupon code has already been scanned and activated."
                    );
                }
                const customer = this.get_partner();
                const {successful, payload} = await this.pos.env.services.rpc({
                    model: "pos.config",
                    method: "use_coupon_code",
                    args: [
                        [this.pos.config.id],
                        code,
                        this.creation_date,
                        customer ? customer.id : false,
                    ],
                    kwargs: {
                        context: session.user_context,
                    },
                });
                if (successful) {
                    var {confirmed, amount: amount} = await Gui.showPopup(
                        "PromoCodePopups",
                        {
                            title: _t("Redeem Amount"),
                            code: code,
                            partner_id: payload.coupon_partner_id
                                ? this.pos.db.get_partner_by_id(
                                      payload.coupon_partner_id
                                  ).name
                                : "",
                            points: payload.points,
                        }
                    );
                    if (confirmed) {
                        const program = this.pos.program_by_id[payload.program_id];
                        const coupon = new PosLoyaltyCard(
                            code,
                            payload.coupon_id,
                            payload.program_id,
                            payload.coupon_partner_id,
                            parseInt(amount)
                        );
                        this.pos.couponCache[coupon.id] = coupon;
                        this.codeActivatedCoupons.push(coupon);
                        await this._updateLoyaltyPrograms();
                        claimableRewards = this.getClaimableRewards(coupon.id);
                    }
                } else {
                    return payload.error_message;
                }
                if (claimableRewards && claimableRewards.length === 1) {
                    if (
                        claimableRewards[0].reward.reward_type !== "product" ||
                        !claimableRewards[0].reward.multi_product
                    ) {
                        this._applyReward(
                            claimableRewards[0].reward,
                            claimableRewards[0].coupon_id
                        );
                        this._updateRewards();
                    }
                }
                return true;
            }
        }
    };

Registries.Model.extend(Order, PosLoyaltyOrderExt);
