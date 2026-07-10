/** @odoo-module **/
import { SwitchCompanyMenu } from "@web/webclient/switch_company_menu/switch_company_menu";
import { patch } from "@web/core/utils/patch";

patch(SwitchCompanyMenu.prototype, {
    setup() {
        super.setup(...arguments);

        this.updateSelectionState();
    },

    getActiveCompanyIds() {
        return this.companyService.activeCompanyIds;
    },

    getAllCompanyIds() {
        return Object.values(this.companyService.allowedCompanies).map((company) => company.id);
    },

    updateSelectionState() {
        this.allCompanyIds = this.getAllCompanyIds();
        const activeCompanyIds = this.getActiveCompanyIds();

        this.isAllCompaniesSelected = this.allCompanyIds.length > 0 &&
            this.allCompanyIds.every((companyId) => activeCompanyIds.includes(companyId));
    },

    toggleSelectAllCompanies() {
        this.updateSelectionState();
        const companyIds = this.isAllCompaniesSelected ? [] : this.allCompanyIds;
        this.companyService.setCompanies(companyIds, false);
    },
});
