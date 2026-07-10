/** @odoo-module **/
import { SwitchCompanyMenu } from "@web/webclient/switch_company_menu/switch_company_menu";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { onWillUnmount } from "@odoo/owl";

patch(SwitchCompanyMenu.prototype, {
    setup() {
        super.setup(...arguments);

        this.state = this.state || {};
        this.state.isAllCompaniesSelected = false;

        this.previousCompanyIds = JSON.stringify(this.getActiveCompanyIds());

        this.intervalId = setInterval(() => {
            this.checkForCompanyChanges();
        }, 1000);

        this.updateSelectionState();

        onWillUnmount(() => {
            if (this.intervalId) {
                clearInterval(this.intervalId);
            }
        });
    },

    getActiveCompanyIds() {
        return user.context.allowed_company_ids ||
               user.activeCompanies ||
               [];
    },

    getAllCompanyIds() {
        return Object.values(user.allowedCompanies || {}).map(x => x.id);
    },

    checkForCompanyChanges() {
        const currentCompanyIds = JSON.stringify(this.getActiveCompanyIds());
        if (currentCompanyIds !== this.previousCompanyIds) {
            this.previousCompanyIds = currentCompanyIds;
            this.updateSelectionState();
        }
    },

    updateSelectionState() {
        this.allCompanyIds = this.getAllCompanyIds();
        const activeCompanyIds = this.getActiveCompanyIds();

        this.state.isAllCompaniesSelected = this.allCompanyIds.length > 0 &&
            this.allCompanyIds.every(elem => activeCompanyIds.includes(elem));
    },

    async toggleSelectAllCompanies() {
        const newSelectionState = !this.state.isAllCompaniesSelected;
        const selectedCompanyIds = newSelectionState ? [...this.allCompanyIds] : [];

        this.state.isAllCompaniesSelected = newSelectionState;

        try {
            await user.activateCompanies(selectedCompanyIds, {
                includeChildCompanies: false,
                reload: true,
            });

            this.previousCompanyIds = JSON.stringify(this.getActiveCompanyIds());
        } catch (error) {
            console.error("Error activating companies:", error);
            this.updateSelectionState();
        }
    },
});
