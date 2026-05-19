# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

# CSS values must use single-quoted names for multi-word fonts so the value
# is safely embeddable inside a double-quoted HTML style="..." attribute:
#   <div style="font-family:'Courier New', Courier, monospace;">   ✓
# Double-quoted variants break the HTML attribute boundary, and Markup.format()
# would escape them to &quot; which many email-client CSS parsers reject.

FONT_FAMILIES = [
    ('Arial, Helvetica, sans-serif', 'Arial'),
    ('Verdana, Geneva, sans-serif', 'Verdana'),
    ('Tahoma, Geneva, sans-serif', 'Tahoma'),
    ("'Trebuchet MS', Tahoma, sans-serif", 'Trebuchet MS'),
    ('Georgia, Times, serif', 'Georgia'),
    ("'Times New Roman', Times, serif", 'Times New Roman'),
    ("'Courier New', Courier, monospace", 'Courier New'),
    ('Calibri, Candara, Segoe, Optima, sans-serif', 'Calibri'),
    ("'Palatino Linotype', 'Book Antiqua', Palatino, serif", 'Palatino'),
]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mail_font_family = fields.Selection(
        selection=FONT_FAMILIES,
        string='Default Email Font Family',
        help='Font family applied to the message composer, log note, and mail template body editor.',
        config_parameter='mail_font_config.font_family',
    )
