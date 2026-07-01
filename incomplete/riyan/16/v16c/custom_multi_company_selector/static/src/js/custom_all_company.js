/** @odoo-module **/
import {SwitchCompanyMenu} from "@web/webclient/switch_company_menu/switch_company_menu";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";

patch(SwitchCompanyMenu.prototype, "SwitchAllCompanyMenu", {
    setup() {
        this._super(...arguments);
        this.allCompanyIds = Object.values(this.companyService.availableCompanies).map(
            (x) => x.id
        );
        this.isAllCompaniesSelected = this.allCompanyIds.every((elem) =>
            this.selectedCompanies.includes(elem)
        );
    },

    toggleSelectAllCompanies() {
        if (this.isAllCompaniesSelected) {
            // Deselect all
            this.state.companiesToToggle = this.allCompanyIds;
            this.toggleCompany(this.currentCompany.id);
            this.isAllCompaniesSelected = false;
        } else {
            // Select all individually
            this.state.companiesToToggle = [this.allCompanyIds];
            this.isAllCompaniesSelected = true;
        }

        browser.clearTimeout(this.toggleTimer);
        this.toggleTimer = browser.setTimeout(() => {
            const action = this.isAllCompaniesSelected ? "loginto" : "toggle";
            this.companyService.setCompanies(action, ...this.state.companiesToToggle);
        }, this.constructor.toggleDelay);
    },
});
