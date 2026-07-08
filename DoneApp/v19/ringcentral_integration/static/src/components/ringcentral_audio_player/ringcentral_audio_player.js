/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class RingCentralAudioPlayer extends Component {
    static template = "ringcentral_integration.RingCentralAudioPlayer";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            hasError: false,
            errorMessage: null,
        });
    }

    get hasRecording() {
        return Boolean(this.props.record.data[this.props.name]);
    }

    get callHistoryId() {
        return this.props.record.resId || this.props.record.data.id || null;
    }

    get playbackUrl() {
        if (!this.callHistoryId) {
            return null;
        }
        return `/ringcentral/recording/${this.callHistoryId}`;
    }

    get downloadUrl() {
        if (!this.playbackUrl) {
            return null;
        }
        return `${this.playbackUrl}?download=1`;
    }

    onAudioError() {
        this.state.hasError = true;
        this.state.errorMessage = _t(
            "The recording could not be streamed in the browser. Use the link below to open or download it."
        );
    }
}

registry.category("fields").add("ringcentral_audio_player", {
    component: RingCentralAudioPlayer,
    supportedTypes: ["char"],
});
