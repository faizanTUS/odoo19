# -*- coding: utf-8 -*-
"""Optional rich demo data when the module is installed with demo assets."""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mod = env["ir.module.module"].search([("name", "=", "petty_cash_management")], limit=1)
    if not mod or not mod.demo:
        return
    try:
        _create_demo_scenario(env)
    except Exception as exc:
        _logger.warning("Petty Cash demo scenario skipped: %s", exc)


def _create_demo_scenario(env):
    company = env.ref("base.main_company", raise_if_not_found=False) or env.company
    cash_journal = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "cash")], limit=1
    )
    bank_journal = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
    )
    if not cash_journal or not cash_journal.default_account_id:
        return
    expense_account = env["account.account"].search(
        [
            ("company_ids", "in", company.id),
            ("account_type", "=", "expense"),
            ("deprecated", "=", False),
        ],
        limit=1,
    )
    policy = env.ref("petty_cash_management.demo_petty_cash_policy_standard", raise_if_not_found=False)
    cat_office = env.ref("petty_cash_management.demo_petty_cash_category_office", raise_if_not_found=False)
    if cat_office and expense_account and not cat_office.expense_account_id:
        cat_office.expense_account_id = expense_account

    admin = env.ref("base.user_admin")
    fund = env["petty.cash.fund"].create(
        {
            "name": "Main Office Petty Cash (Demo)",
            "code": "PC-MAIN",
            "company_id": company.id,
            "manager_id": admin.id,
            "policy_id": policy.id if policy else False,
            "journal_id": cash_journal.id,
            "petty_cash_account_id": cash_journal.default_account_id.id,
            "default_expense_account_id": expense_account.id if expense_account else False,
            "source_bank_journal_id": bank_journal.id if bank_journal else False,
            "min_balance": 150.0,
            "replenishment_target_amount": 500.0,
            "auto_replenish": True,
        }
    )
    env["petty.cash.approval.rule"].create(
        [
            {
                "name": "Tier 1 — Line manager",
                "fund_id": fund.id,
                "sequence": 10,
                "amount_from": 0.0,
                "amount_to": 150.0,
                "approver_id": admin.id,
            },
            {
                "name": "Tier 2 — Finance (demo)",
                "fund_id": fund.id,
                "sequence": 20,
                "amount_from": 150.01,
                "amount_to": 999999.0,
                "approver_id": admin.id,
            },
        ]
    )
    employee = env["hr.employee"].search([("company_id", "=", company.id)], limit=1)
    if employee and cat_office:
        env["petty.cash.voucher"].create(
            {
                "fund_id": fund.id,
                "employee_id": employee.id,
                "user_id": admin.id,
                "category_id": cat_office.id,
                "amount": 45.0,
                "description": "Demo: coffee and supplies for client visit.",
            }
        )
