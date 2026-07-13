/* @odoo-module */

import { ChannelSelector } from "@mail/discuss/core/web/channel_selector";
import { patch } from "@web/core/utils/patch";
import { cleanTerm } from "@mail/utils/common/format";
import { _t } from "@web/core/l10n/translation";

patch(ChannelSelector.prototype, {
    async fetchSuggestions() {
        const cleanedTerm = cleanTerm(this.state.value);
        if (cleanedTerm) {
            if (this.props.category.id === "channels") {
                const domain = [
                    ["parent_channel_id", "=", false],
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
                const choices = results.map((channel) => {
                    return {
                        channelId: channel.id,
                        classList: "o-discuss-ChannelSelector-suggestion",
                        label: channel.name,
                    };
                });
                choices.push({
                    channelId: "__create__",
                    classList: "o-discuss-ChannelSelector-suggestion",
                    label: this.state.value,
                });
                this.state.navigableListProps.options = choices;
                return;
            }
            if (this.props.category.id === "chats") {
                const data = await this.sequential(async () => {
                    this.state.navigableListProps.isLoading = true;
                    const data = await this.orm.call("res.partner", "im_search", [
                        cleanedTerm,
                        10,
                        this.state.selectedPartners,
                    ]);
                    this.state.navigableListProps.isLoading = false;
                    return data;
                });
                if (!data) {
                    this.state.navigableListProps.options = [];
                    return;
                }
                const { Persona: partners = [] } = this.store.insert(data);
                const suggestions = this.suggestionService
                    .sortPartnerSuggestions(partners, cleanedTerm)
                    .map((suggestion) => {
                        return {
                            classList: "o-discuss-ChannelSelector-suggestion",
                            label: suggestion.name,
                            partner: suggestion,
                        };
                    });
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
        }
        this.state.navigableListProps.options = [];
        return;
    }
});

