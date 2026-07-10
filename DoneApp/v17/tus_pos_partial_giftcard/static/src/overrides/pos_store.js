/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { PosLoyaltyCard } from "@pos_loyalty/overrides/models/loyalty";

const COUPON_CACHE_MAX_SIZE = 4096;

patch(PosStore.prototype, {
     async fetchCoupons(domain, limit = 1) {
        const result = await this.env.services.orm.searchRead(
            "loyalty.card",
            domain,
            ["id", "points", "code", "partner_id", "program_id", "expiration_date"],
            { limit }
        );
        if (Object.keys(this.couponCache).length + result.length > COUPON_CACHE_MAX_SIZE) {
            this.couponCache = {};
            this.partnerId2CouponIds = {};
            // Make sure that the current order has no invalid data.
            if (this.selectedOrder) {
                this.selectedOrder.invalidCoupons = true;
            }
        }
        const couponList = [];
        for (const dbCoupon of result) {
            var points_cost = this.selectedOrder.orderlines.filter(x => x.coupon_id === dbCoupon.id).map(x => x.points_cost)
            var sum = dbCoupon.points
            if (points_cost.length){
                sum = points_cost.reduce((a, b) => a + b, 0);
            }
            const coupon = new PosLoyaltyCard(
                dbCoupon.code,
                dbCoupon.id,
                dbCoupon.program_id[0],
                dbCoupon.partner_id[0],
                sum,
                dbCoupon.expiration_date
            );
            this.couponCache[coupon.id] = coupon;
            this.partnerId2CouponIds[coupon.partner_id] =
                this.partnerId2CouponIds[coupon.partner_id] || new Set();
            this.partnerId2CouponIds[coupon.partner_id].add(coupon.id);
            couponList.push(coupon);
        }
        return couponList;
    },
});