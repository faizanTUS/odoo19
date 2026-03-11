/** @odoo-module **/

import { RewardButton } from "@pos_loyalty/app/control_buttons/reward_button/reward_button";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(RewardButton.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    async _applyReward(reward, coupon_id, potentialQty) {
        const order = this.pos.get_order();
        order.disabledRewards.delete(reward.id);

        const args = {};
        if (reward.reward_type === "product" && reward.multi_product) {
            const productsList = reward.reward_product_ids.map((product_id) => ({
                id: product_id,
                label: this.pos.db.get_product_by_id(product_id).display_name,
                item: product_id,
            }));
            const { confirmed, payload: selectedProduct } = await this.popup.add(SelectionPopup, {
                title: _t("Please select a product for this reward"),
                list: productsList,
            });
            if (!confirmed) {
                return false;
            }
            args["product"] = selectedProduct;
        }
        if (
            (reward.reward_type == "product" && reward.program_id.applies_on !== "both") ||
            (reward.program_id.applies_on == "both" && potentialQty)
        ) {

            this.pos.addProductToCurrentOrder(
                args["product"] || reward.reward_product_ids[0],
                { quantity: potentialQty || 1, is_birthday: true }
            );
            return true;
        } else {
            const result = order._applyReward(reward, coupon_id, args);
            if (result !== true) {
                // Returned an error
                this.notification.add(result);
            }
            order._updateRewards();
            return result;
        }
    },
    /**
     * @override
     */
    async click() {
        const rewards = this._getPotentialRewards();
        debugger;
        var partner = this.pos.get_order().get_partner(); // E.g., 'Platinum'
        if (rewards.length >= 1) {
            if(partner && partner.membership_level){
                var filtered_rewards = rewards.filter((reward) => {
                    return !reward.reward.membership_level || reward.reward.membership_level === partner.membership_level;
                });
//                var filtered_rewards = rewards.filter((reward) => reward.reward.membership_level === partner.membership_level);
                var rewardsList = filtered_rewards.map((reward) => ({
                    id: reward.reward.id,
                    label: reward.reward.description,
                    description: reward.reward.program_id.name,
                    item: reward,
                }));
            } else{
                var filtered_rewards = rewards.filter((reward) => {
                    return !reward.reward.membership_level;
                });
                var rewardsList = filtered_rewards.map((reward) => ({
                    id: reward.reward.id,
                    label: reward.reward.description,
                    description: reward.reward.program_id.name,
                    item: reward,
                }));
            }
            if (rewards.length >= 1) {
                const { confirmed, payload: selectedReward } = await this.popup.add(SelectionPopup, {
                    title: _t("Please select a reward"),
                    list: rewardsList,
                });
                if (confirmed) {
                    debugger;
                    return this._applyReward(
                        selectedReward.reward,
                        selectedReward.coupon_id,
                        selectedReward.potentialQty
                    );
                }
            }
        }
        return false;
    },
});
