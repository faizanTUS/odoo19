from odoo import _, fields, models
from odoo.exceptions import UserError

from .sequence_date_offset import (
    get_default_interpolation_values,
    get_interpolation_dates,
    get_offset_interpolation_values,
    get_offset_value,
)


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _get_prefix_suffix(self, date=None, date_range=None):
        self.ensure_one()

        interpolation_dates = self._get_interpolation_dates(date=date, date_range=date_range)
        values = self._get_default_interpolation_values(interpolation_dates)
        values.update(self._get_offset_interpolation_values(interpolation_dates))

        try:
            interpolated_prefix = (self.prefix % values) if self.prefix else ""
            interpolated_suffix = (self.suffix % values) if self.suffix else ""
        except (ValueError, TypeError, KeyError):
            raise UserError(_('Invalid prefix or suffix for sequence “%s”', self.name))
        return interpolated_prefix, interpolated_suffix

    def _get_interpolation_dates(self, date=None, date_range=None):
        return get_interpolation_dates(self.env, date=date, date_range=date_range)

    def _get_default_interpolation_values(self, interpolation_dates):
        return get_default_interpolation_values(interpolation_dates)

    def _get_offset_interpolation_values(self, interpolation_dates):
        return get_offset_interpolation_values([self.prefix, self.suffix], interpolation_dates)

    def _get_offset_value(self, base_date, token, offset):
        return get_offset_value(base_date, token, offset)
