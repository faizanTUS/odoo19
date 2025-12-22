/** @odoo-module **/
import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

export const splitViewService = {
    start(env) {
        const state = reactive({
            active: false,
            direction: "vertical",
            ratio: 0.5
        });

        return {
            state,
            setMode(mode) {
                console.log("[SplitService] setMode called:", mode);
                if (mode === "off") {
                    document.body.classList.remove('o_split_active', 'o_split_vertical', 'o_split_horizontal');
                    document.querySelectorAll('.o_split_form_panel').forEach(el => el.remove());
                    state.active = false;
                    env.bus.trigger("split_view_update");
                    return;
                }

                const domActive = document.body.classList.contains('o_split_active');
                const domVertical = document.body.classList.contains('o_split_vertical');
                const domHorizontal = document.body.classList.contains('o_split_horizontal');
                const currentMode = domVertical ? 'vertical' : domHorizontal ? 'horizontal' : null;

                if (domActive && currentMode !== mode) {
                    alert(`Split view is currently in ${currentMode} mode.\n\nPlease click "Split Off" before switching to ${mode} mode.`);
                    return;
                }

                if (!domActive) {
                    state.direction = mode;
                    state.active = true;
                    env.bus.trigger("split_view_update");
                } else {
                }
            },
            toggle() {
                state.active = !state.active;
                env.bus.trigger("split_view_update");
            },
            setRatio(ratio) {
                state.ratio = ratio;
            }
        };
    },
};
registry.category("services").add("splitView", splitViewService);
