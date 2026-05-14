/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class SplitDropdown extends Component {
    static template = "odoo_split_view.SplitDropdown";
    static props = {};

    setup() {
        this.split = useService("splitView");
        this.st = useState(this.split.state);
    }

    get icon() {
        if (document.body.classList.contains('o_split_vertical')) return "fa-columns";
        if (document.body.classList.contains('o_split_horizontal')) return "fa-pause fa-rotate-90";
        return "fa-square-o";
    }

    handleSelectOff() {
        this.split.setMode('off');
        setTimeout(() => {
            const rightPanel = document.getElementById('right_panel');
            if (rightPanel) {
                rightPanel.remove();
            }

            document.body.classList.remove(
                'o_split_active',
                'o_split_vertical',
                'o_split_horizontal'
            );

            document.querySelectorAll('.o_split_selected').forEach(r => r.classList.remove('o_split_selected'));
        }, 200);
    }

    handleSelectVertical() {
        if (document.body.classList.contains('o_split_horizontal')) {
            alert("Horizontal split is active.\n\nPlease click 'Split Off' before switching to vertical mode.");
            return;
        }
        this.split.setMode('vertical');
    }

    handleSelectHorizontal() {
        if (document.body.classList.contains('o_split_vertical')) {
            alert("Vertical split is active.\n\nPlease click 'Split Off' before switching to horizontal mode.");
            return;
        }
        this.split.setMode('horizontal');
    }
}
registry.category("systray").add("SplitDropdown", { Component: SplitDropdown }, { sequence: 10 });
