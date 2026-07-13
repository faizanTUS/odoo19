/** @odoo-module **/

import { ChannelSelector } from "@mail/discuss/core/web/channel_selector";
import { cleanTerm } from "@mail/utils/common/format";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(ChannelSelector.prototype, {
    async fetchSuggestions() {
        const cleanedTerm = cleanTerm(this.state.value);
        if (!cleanedTerm) {
            this.state.navigableListProps.options = [];
            return;
        }

        if (this.props.category.id === "channels") {
            const domain = [
                ["channel_type", "=", "channel"],
                ["name", "ilike", cleanedTerm],
            ];
            const fields = ["name"];
            const results = await this.sequential(async () => {
                this.state.navigableListProps.isLoading = true;
                const res = await this.orm.searchRead("discuss.channel", domain, fields, {
                    limit: 10,
                });
                this.state.navigableListProps.isLoading = false;
                return res;
            });
            if (!results) {
                this.state.navigableListProps.options = [];
                return;
            }
            const choices = results.map((channel) => ({
                channelId: channel.id,
                classList: "o-discuss-ChannelSelector-suggestion",
                label: channel.name,
            }));
            choices.push({
                channelId: "__create__",
                classList: "o-discuss-ChannelSelector-suggestion",
                label: this.state.value,
            });
            this.state.navigableListProps.options = choices;
            return;
        }

        if (this.props.category.id === "chats") {
            const results = await this.sequential(async () => {
                this.state.navigableListProps.isLoading = true;
                const res = await this.orm.call("res.partner", "im_search", [
                    cleanedTerm,
                    10,
                    this.state.selectedPartners,
                ]);
                this.state.navigableListProps.isLoading = false;
                return res;
            });
            if (!results) {
                this.state.navigableListProps.options = [];
                return;
            }

            // Avoid using suggestionService.sortPartnerSuggestions here because it 
            // might not be ready if im_livechat resolves its store with empty data.
            const suggestions = results.map((data) => {
                this.store.Persona.insert({ ...data, type: "partner" });
                return {
                    classList: "o-discuss-ChannelSelector-suggestion",
                    label: data.name,
                    partner: data,
                };
            });

            const selfName = this.store?.self?.name;
            if (typeof selfName === "string" && selfName.toLowerCase().includes(cleanedTerm.toLowerCase())) {
                suggestions.push({
                    classList: "o-discuss-ChannelSelector-suggestion",
                    label: selfName,
                    partner: this.store.self,
                });
            }

            if (suggestions.length === 0) {
                suggestions.push({
                    classList: "o-discuss-ChannelSelector-suggestion",
                    label: _t("No results found"),
                    unselectable: true,
                });
            }
            this.state.navigableListProps.options = suggestions;
            return;
        }

        this.state.navigableListProps.options = [];
    },
}); 