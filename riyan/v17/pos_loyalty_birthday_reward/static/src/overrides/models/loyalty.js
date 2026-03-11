/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
let pointsForProgramsCountedRules = {};


patch(Order.prototype, {

    async _updatePrograms() {
        const changesPerProgram = {};
        const programsToCheck = new Set();
        // By default include all programs that are considered 'applicable'
        for (const program of this.pos.programs) {
            if (this._programIsApplicable(program)) {
                programsToCheck.add(program.id);
            }
        }
        for (const pe of Object.values(this.couponPointChanges)) {
            if (!changesPerProgram[pe.program_id]) {
                changesPerProgram[pe.program_id] = [];
                programsToCheck.add(pe.program_id);
            }
            changesPerProgram[pe.program_id].push(pe);
        }
        for (const coupon of this.codeActivatedCoupons) {
            programsToCheck.add(coupon.program_id);
        }
        const programs = [...programsToCheck].map((programId) => this.pos.program_by_id[programId]);
        const pointsAddedPerProgram = this.pointsForPrograms(programs);
        for (const program of this.pos.programs) {
            // Future programs may split their points per unit paid (gift cards for example), consider a non applicable program to give no points
            const pointsAdded = this._programIsApplicable(program)
                ? pointsAddedPerProgram[program.id]
                : [];
            // For programs that apply to both (loyalty) we always add a change of 0 points, if there is none, since it makes it easier to
            //  track for claimable rewards, and makes sure to load the partner's loyalty card.
            if (program.is_nominative && !pointsAdded.length && this.get_partner()) {
                pointsAdded.push({ points: 0 });
            }
            const oldChanges = changesPerProgram[program.id] || [];
            // Update point changes for those that exist
            for (let idx = 0; idx < Math.min(pointsAdded.length, oldChanges.length); idx++) {
                Object.assign(oldChanges[idx], pointsAdded[idx]);
            }
            if (pointsAdded.length < oldChanges.length) {
                const removedIds = oldChanges.map((pe) => pe.coupon_id);
                this.couponPointChanges = Object.fromEntries(
                    Object.entries(this.couponPointChanges).filter(([k, pe]) => {
                        return !removedIds.includes(pe.coupon_id);
                    })
                );
            } else if (pointsAdded.length > oldChanges.length) {
                for (const pa of pointsAdded.splice(oldChanges.length)) {
                    const coupon = await this._couponForProgram(program);
                    this.couponPointChanges[coupon.id] = {
                        points: pa.points,
                        program_id: program.id,
                        coupon_id: coupon.id,
                        barcode: pa.barcode,
                        appliedRules: pointsForProgramsCountedRules[program.id],
                        giftCardId: pa.giftCardId
                    };
                }
            }
        }
        // Also remove coupons from codeActivatedCoupons if their program applies_on current orders and the program does not give any points
        this.codeActivatedCoupons = this.codeActivatedCoupons.filter((coupon) => {
            const program = this.pos.program_by_id[coupon.program_id];
            if (
                program.applies_on === "current" &&
                pointsAddedPerProgram[program.id].length === 0
            ) {
                return false;
            }
            return true;
        });
    },
    pointsForPrograms(programs) {
        pointsForProgramsCountedRules = {};
        const orderLines = this.get_orderlines().filter((line) => !line.refunded_orderline_id);
        const linesPerRule = {};
        debugger;
        const order = this
        const partner = this.get_partner()
        for (const line of orderLines) {
            const reward = line.reward_id ? this.pos.reward_by_id[line.reward_id] : undefined;
            const isDiscount = reward && reward.reward_type === "discount";
            const rewardProgram = reward && reward.program_id;
            // Skip lines for automatic discounts.
            if (isDiscount && rewardProgram.trigger === "auto") {
                continue;
            }
            for (const program of programs) {
                // Skip lines for the current program's discounts.
                if (isDiscount && rewardProgram.id === program.id) {
                    continue;
                }
                for (const rule of program.rules) {
                    // Skip lines to which the rule doesn't apply.
                    if (rule.any_product || rule.valid_product_ids.has(line.get_product().id)) {
                        if (!linesPerRule[rule.id]) {
                            linesPerRule[rule.id] = [];
                        }
                        linesPerRule[rule.id].push(line);
                    }
                }
            }
        }
        const result = {};
        for (const program of programs) {
            let points = 0;
            const splitPoints = [];
            let loyal_rules = program.rules
            debugger;
            if(this.get_partner()) {
                loyal_rules = loyal_rules.filter((loyal_rule) => !loyal_rule.membership_level || loyal_rule.membership_level == this.get_partner().membership_level)
            }
            for (const rule of loyal_rules) {
                if (
                    rule.mode === "with_code" &&
                    !this.codeActivatedProgramRules.includes(rule.id)
                ) {
                    continue;
                }
                const linesForRule = linesPerRule[rule.id] ? linesPerRule[rule.id] : [];
                const amountWithTax = linesForRule.reduce(
                    (sum, line) => sum + line.get_price_with_tax(),
                    0
                );
                const amountWithoutTax = linesForRule.reduce(
                    (sum, line) => sum + line.get_price_without_tax(),
                    0
                );
                const amountCheck =
                    (rule.minimum_amount_tax_mode === "incl" && amountWithTax) || amountWithoutTax;
                if (rule.minimum_amount > amountCheck) {
                    continue;
                }
                let totalProductQty = 0;
                // Only count points for paid lines.
                const qtyPerProduct = {};
                let orderedProductPaid = 0;
                for (const line of orderLines) {
                    if (
                        ((!line.reward_product_id &&
                            (rule.any_product ||
                                rule.valid_product_ids.has(line.get_product().id))) ||
                            (line.reward_product_id &&
                                (rule.any_product ||
                                    rule.valid_product_ids.has(line.reward_product_id)))) &&
                        !line.ignoreLoyaltyPoints({ program })
                    ) {
                        // We only count reward products from the same program to avoid unwanted feedback loops
                        if (line.is_reward_line) {
                            const reward = this.pos.reward_by_id[line.reward_id];
                            if ((program.id === reward.program_id.id) || ['gift_card', 'ewallet'].includes(reward.program_id.program_type)) {
                                continue;
                            }
                        }
                        const lineQty = line.reward_product_id
                            ? -line.get_quantity()
                            : line.get_quantity();
                        if (qtyPerProduct[line.reward_product_id || line.get_product().id]) {
                            qtyPerProduct[line.reward_product_id || line.get_product().id] +=
                                lineQty;
                        } else {
                            qtyPerProduct[line.reward_product_id || line.get_product().id] =
                                lineQty;
                        }
                        orderedProductPaid += line.get_price_with_tax();
                        if (!line.is_reward_line || !line.is_birthday) {
                            totalProductQty += lineQty;
                        }
                    }
                }
                if (totalProductQty < rule.minimum_qty) {
                    // Should also count the points from negative quantities.
                    // For example, when refunding an ewallet payment. See TicketScreen override in this addon.
                    continue;
                }
                if (!(program.id in pointsForProgramsCountedRules)) {
                    pointsForProgramsCountedRules[program.id] = [];
                }
                pointsForProgramsCountedRules[program.id].push(rule.id);
                if (
                    program.applies_on === "future" &&
                    rule.reward_point_split &&
                    rule.reward_point_mode !== "order"
                ) {
                    // In this case we count the points per rule
                    if (rule.reward_point_mode === "unit") {
                        splitPoints.push(
                            ...Array.apply(null, Array(totalProductQty)).map((_) => {
                                return { points: rule.reward_point_amount };
                            })
                        );
                    } else if (rule.reward_point_mode === "money") {
                        for (const line of orderLines) {
                            if (
                                line.is_reward_line ||
                                !rule.valid_product_ids.has(line.get_product().id) ||
                                line.get_quantity() <= 0 ||
                                line.ignoreLoyaltyPoints({ program })
                            ) {
                                continue;
                            }
                            const pointsPerUnit = roundPrecision(
                                (rule.reward_point_amount * line.get_price_with_tax()) /
                                    line.get_quantity(),
                                0.01
                            );
                            if (pointsPerUnit > 0) {
                                splitPoints.push(
                                    ...Array.apply(null, Array(line.get_quantity())).map(() => {
                                        if (line.giftBarcode && line.get_quantity() == 1) {
                                            return {
                                                points: pointsPerUnit,
                                                barcode: line.giftBarcode,
                                                giftCardId: line.giftCardId,
                                            };
                                        }
                                        return { points: pointsPerUnit };
                                    })
                                );
                            }
                        }
                    }
                } else {
                    // In this case we add on to the global point count
                    if (rule.reward_point_mode === "order") {
                        points += rule.reward_point_amount;
                    } else if (rule.reward_point_mode === "money") {
                        // NOTE: unlike in sale_loyalty this performs a round half-up instead of round down
                        points += roundPrecision(
                            rule.reward_point_amount * orderedProductPaid,
                            0.01
                        );
                    } else if (rule.reward_point_mode === "unit") {
                        points += rule.reward_point_amount * totalProductQty;
                    }
                }
            }
            const res = points || program.program_type === "coupons" ? [{ points }] : [];
            if (splitPoints.length) {
                res.push(...splitPoints);
            }
            result[program.id] = res;
        }
        return result;
    },
    _getPointsCorrection(program) {
        const rewardLines = this.orderlines.filter((line) => line.is_reward_line);
        let res = 0;
         let loyal_rules = program.rules
            debugger;
            if(this.get_partner()) {
                loyal_rules = loyal_rules.filter((loyal_rule) => !loyal_rule.membership_level || loyal_rule.membership_level == this.get_partner().membership_level)
            }
        for (const rule of loyal_rules) {
            for (const line of rewardLines) {
                const reward = this.pos.reward_by_id[line.reward_id];
                if (this._validForPointsCorrection(reward, line, rule)) {
                    if (rule.reward_point_mode === "money") {
                        res -= roundPrecision(
                            rule.reward_point_amount * line.get_price_with_tax(),
                            0.01
                        );
                    } else if (rule.reward_point_mode === "unit") {
                        res += rule.reward_point_amount * line.get_quantity();
                    }
                }
            }
        }
        return res;
    },
});
