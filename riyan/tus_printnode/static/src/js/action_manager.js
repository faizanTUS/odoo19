///** @odoo-module **/

import {browser} from "@web/core/browser/browser";
import {makeContext} from "@web/core/context";
import {useDebugCategory} from "@web/core/debug/debug_context";
import {download} from "@web/core/network/download";
import {evaluateExpr} from "@web/core/py_js/py";
import {registry} from "@web/core/registry";
import {KeepLast} from "@web/core/utils/concurrency";
import {useBus, useService} from "@web/core/utils/hooks";
import {sprintf} from "@web/core/utils/strings";
//import {cleanDomFromBootstrap} from "@web/legacy/utils";
import {View, ViewNotFoundError} from "@web/views/view";
import { CallbackRecorder } from "@web/search/action_hook";
import {ReportAction} from "@web/webclient/actions/reports/report_action";
import {ActionDialog} from "@web/webclient/actions/action_dialog";
const actionServiceRegistry = registry.category("services");
//const rpc = require("web.rpc");
//import {PdfOptionsModal} from "./PdfOptionsModal";
import {
    Component,
    markup,
    onMounted,
    onWillUnmount,
    onError,
    useChildSubEnv,
    xml,
    reactive,
} from "@odoo/owl";

const actionHandlersRegistry = registry.category("action_handlers");
const actionRegistry = registry.category("actions");
const viewRegistry = registry.category("views");

/** @typedef {number|false} ActionId */
/** @typedef {Object} ActionDescription */
/** @typedef {"current" | "fullscreen" | "new" | "main" | "self" | "inline"} ActionMode */
/** @typedef {string} ActionTag */
/** @typedef {string} ActionXMLId */
/** @typedef {Object} Context */
/** @typedef {Function} CallableFunction */
/** @typedef {string} ViewType */

/** @typedef {ActionId|ActionXMLId|ActionTag|ActionDescription} ActionRequest */

/**
 * @typedef {Object} ActionOptions
 * @property {Context} [additionalContext]
 * @property {boolean} [clearBreadcrumbs]
 * @property {CallableFunction} [onClose]
 * @property {Object} [props]
 * @property {ViewType} [viewType]
 */

export async function clearUncommittedChanges(env) {
    const callbacks = [];
    env.bus.trigger("CLEAR-UNCOMMITTED-CHANGES", callbacks);
    const res = await Promise.all(callbacks.map((fn) => fn()));
    return !res.includes(false);
}

function parseActiveIds(ids) {
    const activeIds = [];
    if (typeof ids === "string") {
        activeIds.push(...ids.split(",").map(Number));
    } else if (typeof ids === "number") {
        activeIds.push(ids);
    }
    return activeIds;
}
//
//// -----------------------------------------------------------------------------
//// Errors
//// -----------------------------------------------------------------------------
//
export class ControllerNotFoundError extends Error {}

export class InvalidButtonParamsError extends Error {}

//// -----------------------------------------------------------------------------
//// ActionManager (Service)
//// -----------------------------------------------------------------------------
//
const CTX_KEY_REGEX =
    /^(?:(?:default_|search_default_|show_).+|.+_view_ref|group_by|group_by_no_leaf|active_id|active_ids|orderedBy)$/;

//// only register this template once for all dynamic classes ControllerComponent
const ControllerComponentTemplate = xml`<t t-component="Component" t-props="props"/>`;

function makeActionManager(env) {
    const keepLast = new KeepLast();
    let id = 0;
    let controllerStack = [];
    let dialogCloseProm;
    let actionCache = {};
    let dialog = null;

    // The state action (or default user action if none) is loaded as soon as possible
    // so that the next "doAction" will have its action ready when needed.
    const actionParams = _getActionParams();
    if (actionParams && typeof actionParams.actionRequest === "number") {
        const {actionRequest, options} = actionParams;
        _loadAction(actionRequest, options.additionalContext);
    }

    env.bus.addEventListener("CLEAR-CACHES", () => {
        actionCache = {};
    });
}
