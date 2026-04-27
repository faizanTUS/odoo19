/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, "bulk_attachments_zip_download.ListController" ,{
    getActionMenuItems() {
        const menus = super.getActionMenuItems();
        const other = [...(menus.other || [])];
        if (
            (this.nbSelected || this.isDomainSelected) &&
            !this.props.context?.disable_bulk_attachment_zip
        ) {
            other.push({
                key: "bulk_attach_zip",
                description: _t("Download all files"),
                callback: () => this.onBulkAttachmentZip(),
            });
        }
        return Object.assign({}, menus, { other });
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
