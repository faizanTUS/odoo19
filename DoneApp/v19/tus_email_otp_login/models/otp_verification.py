# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models, api


class OtpVerification(models.Model):
    _name = "otp.verification"
    _description = 'Otp Verification'

    otp = fields.Text(string="One-Time Password", help="The one-time password code sent to the user")

    state = fields.Selection([
        ('verified', 'Verified'),
        ('unverified', 'Unverified'),
        ('rejected', 'Rejected'),
        ('expired', 'expired'),
    ], string="Verification State", default="unverified", tracking=True)

    email = fields.Char(
        string="Email Address",
        required=True,
        index=True,
        help="Email address associated with the OTP verification"
    )
    expiry_date = fields.Datetime(string="Expiry Date", help="Date and time when the OTP expires")
    create_date_otp = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
        help="Timestamp when the OTP was created"
    )


    @api.model
    def _cron_cleanup_verified_otp(self) -> None:
        """
        Scheduled task that removes all verified OTP records from the database.
        This method is intended to be run periodically via the cron job.
        """
        verified_records = self.search([('state', '=', 'verified')])
        verified_records.unlink()

