/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { clear } from '@mail/model/model_field_command';
import session from 'web.session';
import { attr, one } from '@mail/model/model_field';

registerPatch({
    name: 'MessageActionList',
    fields: {
        actionDelete: {
            compute() {
                if (session.show_btn) {
                    return this._super();
                }
                return clear();
            }
        },
        actionEdit: {
            compute() {
                if (session.show_btn) {
                    return this._super();
                }
                return clear();
            }
        },
    },

});
