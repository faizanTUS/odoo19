# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.addons.account_reports.models.account_report import AccountReport as AccountReportMain
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero
import io
# from odoo.tools.misc import xlsxwriter
import xlsxwriter
import markupsafe

class AccountReport(models.Model):
    _inherit = 'account.report'


    def _init_options_buttons(self, options, previous_options=None):
        super()._init_options_buttons(options,previous_options)

        if self.display_name == 'Partner Ledger':
            fold_buttons = [
                {'name': _('fold PDF'), 'sequence': 98, 'action': 'export_file', 'action_param': 'export_to_pdf_fold',
                 'file_export_type': _('fold PDF')},
                {'name': _('fold XLSX'), 'sequence': 99, 'action': 'export_file', 'action_param': 'export_to_xlsx_fold',
                 'file_export_type': _('fold XLSX')}, ]
            options['buttons'].extend(fold_buttons)

    def export_to_pdf_fold(self, options):
        self.ensure_one()
        return self.with_context(fold_export=True).export_to_pdf(options)

    def export_to_xlsx_fold(self, options):
        return self.with_context(fold_export=True).export_to_xlsx(options)

    def _fully_unfold_lines_if_needed(self, lines, options):
        if self._context.get('fold_export'):
            return lines
        return super()._fully_unfold_lines_if_needed(lines, options)


    def _add_totals_below_sections(self, lines, options):
        if self._context.get('fold_export'):
            return lines
        return super()._add_totals_below_sections(lines, options)