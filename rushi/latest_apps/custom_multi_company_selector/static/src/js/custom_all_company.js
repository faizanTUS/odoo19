/** @odoo-module **/
import {
    SwitchCompanyItem,
    SwitchCompanyMenu,
} from "@web/webclient/switch_company_menu/switch_company_menu";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";

patch(SwitchCompanyMenu.prototype, {
    setup() {
        super.setup(...arguments);
        this.allCompanyIds = user.allowedCompanies.map((x) => x.id);
        this.isAllCompaniesSelected = this.allCompanyIds.every((elem) =>
            user.activeCompanies.map((x) => x.id).includes(elem)
        );
    },

    toggleSelectAllCompanies() {
        this.isAllCompaniesSelected = !this.isAllCompaniesSelected;
        this.selectedAllCompaniesIds = this.isAllCompaniesSelected
            ? [...this.allCompanyIds]
            : [];
        user.activateCompanies(this.selectedAllCompaniesIds);
    },
});
