#!/usr/bin/env bash
#Usage: run_functional_test.sh /home/tus-222/workspace/odoo18/odoo18/odoo-bin /home/tus-222/workspace/odoo18/odoo18/addons /home/tus-222/workspace/odoo18/enterprise ... [20_april_v18]
set -euo pipefail
ODOO_BIN="${1:-/home/tus-225/Workspace/odoo18/odoo/odoo-bin}"
ADDONS_PATH="${2:-/home/tus-225/Workspace/odoo18/odoo/addons,/home/tus-225/Workspace/odoo18/project}"
DBNAME="${3:-document_attachment_universal_preview_18es}"
echo "Creating database ${DBNAME} and installing mail + document_attachment_universal_preview..."
dropdb "${DBNAME}" 2>/dev/null || true
createdb "${DBNAME}"
"${ODOO_BIN}" -d "${DBNAME}" --addons-path="${ADDONS_PATH}" -i base,mail,document_attachment_universal_preview --stop-after-init --log-level=warn
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running functional verification (ICP, session_info, attachments)..."
printf '%s\n' "exec(open('${SCRIPT_DIR}/uap_functional_verify.py').read())" | "${ODOO_BIN}" shell -d "${DBNAME}" --addons-path="${ADDONS_PATH}" --shell-interface=python --log-level=warn
echo "Done. Database: ${DBNAME}"
