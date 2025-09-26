# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models
import io
import xlsxwriter
import markupsafe

class AccountReport(models.Model):
    _inherit = 'account.report'

    filter_analytic_account = None

    def _get_pdf_export_html(self, options, lines, additional_context=None, template=None):
        report_info = self.get_report_information(options)

        # custom_print_templates = report_info['custom_display'].get('pdf_export', {})
        # template = custom_print_templates.get('pdf_export_main', 'account_reports.pdf_export_main')
        custom_print_templates = options['custom_display_config'].get('pdf_export', {})
        template = custom_print_templates.get('pdf_export_main', 'account_reports.pdf_export_main')

        render_values = {
            'report': self,
            'report_title': self.name,
            'options': options,
            'table_start': markupsafe.Markup('<tbody>'),
            'table_end': markupsafe.Markup('''
                </tbody></table>
                <div style="page-break-after: always"></div>
                <table class="o_table table-hover">
            '''),
            'column_headers_render_data': self._get_column_headers_render_data(options),
            'custom_templates': custom_print_templates,
        }
        if additional_context:
            render_values.update(additional_context)

        if options.get('order_column'):
            lines = self.sort_lines(lines, options)

        # if self._context and 'print_mode' in self._context and self._context.get('print_mode') == True:
        new_lines = []
        folded_lines = []
        for i in lines:
            if 'unfolded' in i and i.get('unfolded') == True:
                new_lines.append(i)
            elif i.get('parent_id'):
                new_lines.append(i)
        # if new_lines and self.main_template == 'account_reports.template_partner_ledger_report':
        if new_lines and self.custom_handler_model_name == 'account.partner.ledger.report.handler':
            if options.get('unfolded_lines'):
                lines = new_lines
        # fold_lines giving faulty resut when unfold ALL filter applied on the report
        # fold_lines = [line for line in lines if not line.get('caret_options')]
        # if fold_lines and self.main_template == 'account_reports.template_partner_ledger_report' and not options.get(
        # if fold_lines and self.custom_handler_model_name == 'account.partner.ledger.report.handler' and not options.get(
        #         'unfolded_lines'):
        #     for fol_lines in fold_lines:
        #         folded_lines.append(fol_lines)
        #     lines = folded_lines

        lines = self._format_lines_for_display(lines, options)

        render_values['lines'] = lines

        # Manage footnotes.
        footnotes_to_render = []
        number = 0
        for line in lines:
            # footnotes is not available currenlty in odoo18, but keeping here if comes in other update by odoo18
            footnote_data = report_info.get('footnotes') and report_info.get('footnotes').get(str(line.get('id')))
            if footnote_data:
                number += 1
                line['footnote'] = str(number)
                footnotes_to_render.append({'id': footnote_data['id'], 'number': number, 'text': footnote_data['text']})

        render_values['footnotes'] = footnotes_to_render

        options['css_custom_class'] = options['custom_display_config'].get('css_custom_class', '')

        # Render.
        return self.env['ir.qweb']._render(template, render_values)


    def export_to_xlsx(self, options, response=None):
        def write_with_colspan(sheet, x, y, value, colspan, style):
            if colspan == 1:
                sheet.write(y, x, value, style)
            else:
                sheet.merge_range(y, x, y, x + colspan - 1, value, style)

        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })
        sheet = workbook.add_worksheet(self.name[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        # Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 0
        x_offset = 1  # 1 and not 0 to leave space for the line name
        print_mode_self = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)
        print_options = print_mode_self.get_options(previous_options=options)
        lines = self._filter_out_folded_children(print_mode_self._get_lines(print_options))

        # Add headers.
        # For this, iterate in the same way as done in main_table_header template
        column_headers_render_data = self._get_column_headers_render_data(print_options)
        for header_level_index, header_level in enumerate(print_options['column_headers']):
            for header_to_render in header_level * column_headers_render_data['level_repetitions'][header_level_index]:
                colspan = header_to_render.get('colspan',
                                               column_headers_render_data['level_colspan'][header_level_index])
                write_with_colspan(sheet, x_offset, y_offset, header_to_render.get('name', ''), colspan, title_style)
                x_offset += colspan
            y_offset += 1
            x_offset = 1

        for subheader in column_headers_render_data['custom_subheaders']:
            colspan = subheader.get('colspan', 1)
            write_with_colspan(sheet, x_offset, y_offset, subheader.get('name', ''), colspan, title_style)
            x_offset += colspan
        y_offset += 1
        x_offset = 1

        for column in print_options['columns']:
            colspan = column.get('colspan', 1)
            write_with_colspan(sheet, x_offset, y_offset, column.get('name', ''), colspan, title_style)
            x_offset += colspan
        y_offset += 1

        if print_options.get('order_column'):
            lines = self._sort_lines(lines, print_options)
        new_lines = []
        folded_lines = []
        if self.custom_handler_model_name == 'account.partner.ledger.report.handler':
            for i in lines:
                if 'unfolded' in i and i.get('unfolded') == True:
                    new_lines.append(i)
                elif i.get('parent_id'):
                    new_lines.append(i)
        if new_lines:
            if options.get('unfolded_lines'):
                lines = new_lines
        # fold_lines giving faulty resut when unfold ALL filter applied on the report
        # fold_lines = [line for line in lines if not line.get('caret_options')]
        # if fold_lines and self._name == 'account.partner.ledger' and not options.get('unfolded_lines'):
        #     for fol_lines in fold_lines:
        #         folded_lines.append(fol_lines)
        #     lines = folded_lines

        # Add lines.
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value,
                                         date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return {
            'file_name': self.get_default_report_filename(options, 'xlsx'),
            'file_content': generated_file,
            'file_type': 'xlsx',
        }


