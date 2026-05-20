# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
from datetime import date
from odoo.tools import html_sanitize


class ResPartner(models.Model):
    _inherit = "res.partner"

    ageing_last_alert_date = fields.Date(
        string="Last Ageing Alert Date",
        help="Last date when an ageing alert activity was created for this partner.",
    )
    ageing_last_priority = fields.Selection(
        [
            ("critical", "Critical"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        string="Last Ageing Priority",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ageing_min_overdue_amount = fields.Monetary(
        string="Min Overdue Amount for Alert",
        default=0.0,
        help="Minimum total overdue amount per partner to trigger an alert.",
    )
    ageing_alert_cooldown_days = fields.Integer(
        string="Alert Cooldown (Days)",
        default=3,
        help="Minimum number of days between alerts for the same partner.",
    )
    ageing_enable_vendor = fields.Boolean(
        string="Enable Vendor Ageing Alerts",
        default=True,
    )
    ageing_enable_customer = fields.Boolean(
        string="Enable Customer Ageing Alerts",
        default=True,
    )

    ageing_critical_amount = fields.Monetary(
        string="Critical Min Amount",
        default=500000,
    )
    ageing_critical_days = fields.Integer(
        string="Critical Min Days Overdue",
        default=60,
    )

    ageing_high_amount = fields.Monetary(
        string="High Min Amount",
        default=200000,
    )
    ageing_high_days = fields.Integer(
        string="High Min Days Overdue",
        default=45,
    )

    ageing_medium_amount = fields.Monetary(
        string="Medium Min Amount",
        default=50000,
    )
    ageing_medium_days = fields.Integer(
        string="Medium Min Days Overdue",
        default=30,
    )


    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )

    def set_values(self):
        super().set_values()
        Param = self.env["ir.config_parameter"].sudo()
        Param.set_param("ageing_alerts.min_overdue_amount", self.ageing_min_overdue_amount)
        Param.set_param("ageing_alerts.alert_cooldown_days", self.ageing_alert_cooldown_days)
        Param.set_param("ageing_alerts.enable_vendor", self.ageing_enable_vendor)
        Param.set_param("ageing_alerts.enable_customer", self.ageing_enable_customer)

        Param.set_param("ageing_alerts.critical_amount", self.ageing_critical_amount)
        Param.set_param("ageing_alerts.critical_days", self.ageing_critical_days)
        Param.set_param("ageing_alerts.high_amount", self.ageing_high_amount)
        Param.set_param("ageing_alerts.high_days", self.ageing_high_days)
        Param.set_param("ageing_alerts.medium_amount", self.ageing_medium_amount)
        Param.set_param("ageing_alerts.medium_days", self.ageing_medium_days)


    @api.model
    def get_values(self):
        res = super().get_values()
        Param = self.env["ir.config_parameter"].sudo()
        res.update(
            ageing_min_overdue_amount=float(
                Param.get_param("ageing_alerts.min_overdue_amount", "0.0")
            ),
            ageing_alert_cooldown_days=int(
                Param.get_param("ageing_alerts.alert_cooldown_days", "3")
            ),
            ageing_enable_vendor=Param.get_param("ageing_alerts.enable_vendor"),
            ageing_enable_customer=Param.get_param("ageing_alerts.enable_customer"),
            
            ageing_critical_amount=float(Param.get_param("ageing_alerts.critical_amount", "500000")),
            ageing_critical_days=int(Param.get_param("ageing_alerts.critical_days", "60")),
            ageing_high_amount=float(Param.get_param("ageing_alerts.high_amount", "200000")),
            ageing_high_days=int(Param.get_param("ageing_alerts.high_days", "45")),
            ageing_medium_amount=float(Param.get_param("ageing_alerts.medium_amount", "50000")),
            ageing_medium_days=int(Param.get_param("ageing_alerts.medium_days", "30")),

        )
        return res


class AccountAgeingAlertRunner(models.TransientModel):
    _name = "account.ageing.alert.runner"
    _description = "Account Ageing Alert Runner"

    @api.model
    def run_daily_ageing_alert(self):
        today = date.today()
        Param = self.env["ir.config_parameter"].sudo()

        min_amount = float(Param.get_param("ageing_alerts.min_overdue_amount", "0.0"))
        cooldown_days = int(Param.get_param("ageing_alerts.alert_cooldown_days", "3"))
        enable_vendor = Param.get_param("ageing_alerts.enable_vendor")
        enable_customer = Param.get_param("ageing_alerts.enable_customer")

        domain_move = [
            ("state", "=", "posted"),
            ("payment_state", "in", ("not_paid", "partial")),
            ("invoice_date_due", "!=", False),
        ]

        move_types = []
        if enable_customer:
            move_types.extend(["out_invoice", "out_refund"])
        if enable_vendor:
            move_types.extend(["in_invoice", "in_refund"])

        if not move_types:
            return

        domain_move.append(("move_type", "in", move_types))
        moves = self.env["account.move"].search(domain_move)

        # Group by partner AND type
        partner_data = {}

        for move in moves:
            partner = move.partner_id
            if not partner:
                continue

            # Determine correct partner_type for THIS move
            move_type = (
                "customer"
                if move.move_type in ("out_invoice", "out_refund")
                else "vendor"
            )

            key = (partner, move_type)  # Separate bucket for each type

            if key not in partner_data:
                partner_data[key] = {
                    "moves": [],
                    "total_overdue": 0.0,
                    "max_days_overdue": 0,
                    "partner_type": move_type,
                    "partner": partner,
                }

            partner_data[key]["moves"].append(move)
            partner_data[key]["total_overdue"] += move.amount_residual

            if move.days_overdue > partner_data[key]["max_days_overdue"]:
                partner_data[key]["max_days_overdue"] = move.days_overdue

        # Process each partner+type bucket separately
        for key, data in partner_data.items():
            partner = data["partner"]
            total_overdue = data["total_overdue"]

            if total_overdue <= 0 or total_overdue < min_amount:
                continue

            # Cooldown check (per partner)
            if partner.ageing_last_alert_date:
                diff = today - partner.ageing_last_alert_date
                if diff.days < cooldown_days:
                    continue

            ai_result = self._call_ai_for_partner_ageing(partner, data)

            priority = ai_result.get("priority", "medium").lower()
            note = ai_result.get("message", "")

            # Map to activity summary
            priority_label = priority.capitalize()
            summary = f"Ageing Alert ({priority_label}) - {partner.name}"

            # Assign responsible user: partner's assigned user or current user
            responsible = partner.user_id or self.env.user

            # Create activity
            self.env["mail.activity"].create(
                {
                    "res_model_id": self.env.ref("base.model_res_partner").id,
                    "res_id": partner.id,
                    "user_id": responsible.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "summary": summary,
                    "note": note,
                    "date_deadline": today,
                }
            )

            # Update last alert info
            partner.write(
                {
                    "ageing_last_alert_date": today,
                    "ageing_last_priority": priority
                        if priority in ("critical", "high", "medium", "low")
                        else "medium",
                }
            )

    def _call_ai_for_partner_ageing(self, partner, data):
        """Hook to integrate with any AI/LLM provider.

        You can override this method in a custom module or extend it to call
        an external API.

        For now, we implement a smart-but-rule-based fallback.
        """
        total = data["total_overdue"]
        days = data["max_days_overdue"]
        partner_type = data["partner_type"]

        Param = self.env["ir.config_parameter"].sudo()

        critical_amount = float(Param.get_param("ageing_alerts.critical_amount", "500000"))
        critical_days = int(Param.get_param("ageing_alerts.critical_days", "60"))

        high_amount = float(Param.get_param("ageing_alerts.high_amount", "200000"))
        high_days = int(Param.get_param("ageing_alerts.high_days", "45"))

        medium_amount = float(Param.get_param("ageing_alerts.medium_amount", "50000"))
        medium_days = int(Param.get_param("ageing_alerts.medium_days", "30"))

        # Updated dynamic rule engine
        if total >= critical_amount and days >= critical_days:
            priority = "critical"
        elif total >= high_amount and days >= high_days:
            priority = "high"
        elif total >= medium_amount and days >= medium_days:
            priority = "medium"
        else:
            priority = "low"


        html_message = html_sanitize(f"""
            <p><b>Partner <span style='font-size:25px;'>&#8594;</span></b> {partner.display_name}</p>
            <p style="margin-top: -15px;"><b>Type <span style='font-size:25px;'>&#8594;</span></b> {partner_type.capitalize()}</p>
            <p style="margin-top: -15px;"><b>Total overdue amount <span style='font-size:25px;'>&#8594;</span></b> {total:.2f}</p>
            <p style="margin-top: -15px;"><b>Oldest overdue (days) <span style='font-size:25px;'>&#8594;</span></b> {days}</p>
            <p style="margin-top: -15px;"><b>Suggested Action <span style='font-size:25px;'>&#8594;</span></b></p>
        """)

        if priority == "critical":
            html_message += html_sanitize("<p>- Immediate follow-up required. Consider phone call and written commitment.</p>")
        elif priority == "high":
            html_message += html_sanitize("<p>- Follow-up within 24 hours. Send reminder and confirm payment timeline.</p>")
        elif priority == "medium":
            html_message += html_sanitize("<p>- Send polite reminder email and monitor response.</p>")
        else:
            html_message += html_sanitize("<p>- Include in the next normal reminder cycle.</p>")

        return {
            "priority": priority,
            "message": html_message,
        }
