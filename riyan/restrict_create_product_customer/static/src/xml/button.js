/** @odoo-module **/

import { registry } from "@web/core/registry";
//import { ListRenderer } from "@web/views/list/list_renderer";
import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";
import { listView } from "@web/views/list/list_view";
import { ListController } from '@web/views/list/list_controller';
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { FormController } from '@web/views/form/form_controller';
import { formView } from "@web/views/form/form_view";


export class ButtonListController extends ListController {

    static template = "restrict_create_product_customer.ButtonListRenderer";
//    static components = {
//        ...ListRenderer.components
//    };

    setup() {
        debugger
        super.setup();
        onWillStart(async () => {
            this.hasAccess = await user.hasGroup("restrict_create_product_customer.group_product_create");
        });
        console.log(" ============>", this.hasAccess)
    }
}

export const ButtonListView = {
    ...listView,
    Controller: ButtonListController,
};

export class ButtonKanbanController extends KanbanController {

    static template = "restrict_create_product_customer.ButtonKanbanController";
//    static components = {
//        ...ListRenderer.components
//    };

    setup() {
        super.setup();
        onWillStart(async () => {
            this.hasAccess = await user.hasGroup("restrict_create_product_customer.group_product_create");
        });
    }
}

export const ButtonKanbanView = {
    ...kanbanView,
    Controller: ButtonKanbanController,
};


registry.category("views").add("button_list_view", ButtonListView);
registry.category("views").add("button_kanban_view", ButtonKanbanView);


export class ButtonFormController extends FormController {

    static template = "restrict_create_product_customer.ButtonFormRenderer";
//    static components = {
//        ...ListRenderer.components
//    };

    setup() {
        super.setup();
        onWillStart(async () => {
            this.hasAccess = await user.hasGroup("restrict_create_product_customer.group_product_create");
        });
    }
}

export const ButtonFormView = {
    ...formView,
    Controller: ButtonFormController,
};

registry.category("views").add("button_form_view", ButtonFormView);