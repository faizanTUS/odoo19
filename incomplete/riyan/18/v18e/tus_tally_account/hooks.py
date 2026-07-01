# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
def post_init_hook(env):
    # Set tally_wise_reporting=True and account_type='income' on Closing Stock (p2123)
    # when the account exists via chart metadata (e.g. account.1_p2123)
    closing_stock_account = env.ref(
        'account.%s_p2123' % env.company.id,
        raise_if_not_found=False
    )
    if closing_stock_account and closing_stock_account._name == 'account.account':
        closing_stock_account.with_company(env.company).write({
            'tally_wise_reporting': True,
            'account_type': 'income',
        })

    ReportLine = env['account.report.line']

    pl_report = env.ref(
        'l10n_in_reports.profit_and_loss',
        raise_if_not_found=False
    )

    if not pl_report:
        return

    closing_stock_tag = env.ref(
        'l10n_in.account_tag_closing_stock',
        raise_if_not_found=False
    )
    closing_stock_tag_id = closing_stock_tag.id if closing_stock_tag else None

    pl_lines = ReportLine.search([
        ('report_id', '=', pl_report.id)
    ])
    if pl_lines:
        pl_lines.unlink()

    report_lines_data = [
        {
            'name': 'Net Profit',
            'code': 'NEP_IN',
            'hierarchy_level': 0,
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'aggregation',
                'formula': "OPINC_IN.balance + OIN_IN.balance + CLS_IN.balance - OPS_IN.balance - COS_IN.balance - EXP_IN.balance - DEP_IN.balance",
                'subformula': False,
                'date_scope': 'strict_range',
                'green_on_positive': True,
            })],
        },

        {
            'name': 'Closing Stock',
            'code': 'CLS_IN',
            'hierarchy_level': 0,
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': f"[('account_id.account_type', '=', 'income'), ('account_id.tag_ids', '=', {closing_stock_tag_id}), ('account_id.tally_wise_reporting', '=', True)]",
                'subformula': '-sum',
                'date_scope': 'from_beginning',
            })],
        },

        {
            'name': 'Income',
            'code': 'INC_IN',
            'hierarchy_level': 0,
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'aggregation',
                'formula': "OPINC_IN.balance + OIN_IN.balance",
                'subformula': False,
                'date_scope': 'strict_range',
                'green_on_positive': True,
            })],
        },

        {
            'name': 'Gross Profit',
            'code': 'GRP_IN',
            'hierarchy_level': 3,
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'aggregation',
                'formula': "OPINC_IN.balance - COS_IN.balance",
                'subformula': False,
                'date_scope': 'strict_range',
                'green_on_positive': True,
            })],
        },

        {
            'name': 'Operating Income',
            'code': 'OPINC_IN',
            'hierarchy_level': 5,
            'foldable': True,
            'user_groupby': 'account_id',
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': "[('account_id.account_type', '=', 'income'), ('account_id.tally_wise_reporting', '=', False)]",
                'subformula': '-sum',
                'date_scope': 'strict_range',
                'green_on_positive': True,
            })],
        },

        {
            'name': 'Cost of Revenue',
            'code': 'COS_IN',
            'hierarchy_level': 5,
            'foldable': True,
            'user_groupby': 'account_id',
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': "[('account_id.account_type', '=', 'expense_direct_cost')]",
                'subformula': 'sum',
                'date_scope': 'strict_range',
            })],
        },

        {
            'name': 'Other Income',
            'code': 'OIN_IN',
            'hierarchy_level': 3,
            'foldable': True,
            'user_groupby': 'account_id',
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': "[('account_id.account_type', '=', 'income_other')]",
                'subformula': '-sum',
                'date_scope': 'strict_range',
                'green_on_positive': True,
            })],
        },

        {
            'name': 'Opening Stock',
            'code': 'OPS_IN',
            'hierarchy_level': 0,
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': f"[('account_id.account_type', '=', 'income'), ('account_id.tag_ids', '=', {closing_stock_tag_id}), ('account_id.tally_wise_reporting', '=', True)]",
                'subformula': '-sum',
                'date_scope': 'to_beginning_of_period',
            })],
        },

        {
            'name': 'Expenses',
            'code': 'LEX_IN',
            'hierarchy_level': 0,
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'aggregation',
                'formula': "EXP_IN.balance + DEP_IN.balance",
                'subformula': False,
                'date_scope': 'strict_range',
            })],
        },

        {
            'name': 'Expenses',
            'code': 'EXP_IN',
            'hierarchy_level': 3,
            'foldable': True,
            'user_groupby': 'account_id',
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': "[('account_id.account_type', '=', 'expense')]",
                'subformula': 'sum',
                'date_scope': 'strict_range',
            })],
        },

        {
            'name': 'Depreciation',
            'code': 'DEP_IN',
            'hierarchy_level': 3,
            'foldable': True,
            'user_groupby': 'account_id',
            'sequence': 0,
            'expression_ids': [(0, 0, {
                'label': 'balance',
                'engine': 'domain',
                'formula': "[('account_id.account_type', '=', 'expense_depreciation')]",
                'subformula': 'sum',
                'date_scope': 'strict_range',
            })],
        },

    ]

    for line in report_lines_data:
        ReportLine.create({
            'name': line['name'],
            'code': line['code'],
            'report_id': pl_report.id,
            'hierarchy_level': line['hierarchy_level'],
            'sequence': line['sequence'],
            'expression_ids': line['expression_ids'],
            'foldable': line.get('foldable', False),
            'user_groupby': line.get('user_groupby'),
        })
