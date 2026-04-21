/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, {
    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems();
        items.bulk_attach_zip = {
            isAvailable: () =>
                this.hasSelectedRecords &&
                !this.props.context?.disable_bulk_attachment_zip,
            sequence: 15,
            icon: "fa fa-download",
            description: _t("Download all files"),
            callback: () => this.onBulkAttachmentZip(),
        };
        return items;
    },

    async onBulkAttachmentZip() {
        const activeIds = await this.model.root.getResIds(true);
        if (!activeIds.length) {
            return;
        }
        await this.actionService.doAction(
            "bulk_attachments_zip_download.action_bulk_attachments_zip_wizard",
            {
                additionalContext: {
                    active_model: this.props.resModel,
                    active_ids: activeIds,
                },
            }
        );
    },
});
