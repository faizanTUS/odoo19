/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { useService } from "@web/core/utils/hooks";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import { useRef } from "@odoo/owl";
import { FormCompiler } from "@web/views/form/form_compiler";
import { append, createElement, extractAttributes, setAttributes } from "@web/core/utils/xml";

FormViewDialog.defaultProps.contentClass = "o_wa_meta_dialog";
patch(ListRenderer.prototype,{
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
    },
    onDiscussCellClicked(record, ev) {
        this.dialogService.add(FormViewDialog, {
            resModel: record.resModel,
            resId: record.resId,
            title: record.data["name"],
            preventEdit: true,
            preventCreate: true,
            context: {
                abcd: true,
            },
        });
    },
});
patch(FormController.prototype,{
     async save(params){
        this.props.saveRecord = false
        super.save(...arguments)
     }
});

patch(FormCompiler.prototype, {
    compile(node, params) {
        const res = super.compile(node, params);
        const chatterContainerHookXml = res.querySelector(".o-mail-Form-chatter");
        if (!chatterContainerHookXml) {
            return res; // no chatter, keep the result as it is
        }
        const webClientViewAttachmentViewHookXml = res.querySelector(".o_attachment_preview");
        const hasPreview = !!webClientViewAttachmentViewHookXml;
        let { ["t-if"]: tIf } = extractAttributes(chatterContainerHookXml, ["t-if"]);
//        passing here blank tIf -> to avoid this condition as shown below from base
//        setAttributes(chatterContainerHookXml, { "t-if": "!__comp__.env.inDialog" });
        tIf = ''
        setAttributes(chatterContainerHookXml, {
            "t-if": `${
                tIf ? tIf : "true"
            } and (!["COMBO", "NONE"].includes(__comp__.mailLayout(${hasPreview})))`, // opposite of sheetBgChatterContainerHookXml
            "t-attf-class": `{{ ["SIDE_CHATTER", "EXTERNAL_COMBO_XXL"].includes(__comp__.mailLayout(${hasPreview})) ? "o-aside w-print-100" : "mt-4 mt-md-0" }}`,
        });
        return res;
    }
});