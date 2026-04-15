#!/usr/bin/env bash
# Usage: run_functional_test.sh /path/to/odoo-bin /path/to/addons1:/path/to/addons2:... [database_name]
set -euo pipefail
ODOO_BIN="${1:?odoo-bin path}"
ADDONS_PATH="${2:?addons path}"
DBNAME="${3:-test_uap_functional}"
echo "Creating database ${DBNAME} and installing mail + document_attachment_universal_preview..."
dropdb "${DBNAME}" 2>/dev/null || true
createdb "${DBNAME}"
"${ODOO_BIN}" -d "${DBNAME}" --addons-path="${ADDONS_PATH}" -i base,mail,document_attachment_universal_preview --stop-after-init --log-level=warn
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running functional verification (ICP, session_info, attachments)..."
printf '%s\n' "exec(open('${SCRIPT_DIR}/uap_functional_verify.py').read())" | "${ODOO_BIN}" shell -d "${DBNAME}" --addons-path="${ADDONS_PATH}" --shell-interface=python --log-level=warn
echo "Done. Database: ${DBNAME}"
