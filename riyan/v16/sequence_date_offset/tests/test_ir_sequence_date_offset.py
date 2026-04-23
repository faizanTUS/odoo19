from odoo.tests.common import TransactionCase


class TestIrSequenceDateOffset(TransactionCase):
    def test_default_directives_still_work(self):
        sequence = self.env["ir.sequence"].create(
            {
                "code": "test_sequence_date_offset_default",
                "name": "Test default directives",
                "prefix": "%(year)s/%(month)s/%(day)s/",
                "suffix": "/%(y)s",
            }
        )

        prefix, suffix = sequence._get_prefix_suffix(date="2024-02-29")

        self.assertEqual(prefix, "2024/02/29/")
        self.assertEqual(suffix, "/24")

    def test_offset_directives_are_interpolated(self):
        sequence = self.env["ir.sequence"].create(
            {
                "code": "test_sequence_date_offset_interpolate",
                "name": "Test offset directives",
                "prefix": "INV/%(year+1)s/%(month+1)s/%(day+1)s/",
                "suffix": "%(y)s-%(y+1)s",
            }
        )

        prefix, suffix = sequence._get_prefix_suffix(date="2024-12-31")

        self.assertEqual(prefix, "INV/2025/01/01/")
        self.assertEqual(suffix, "24-25")

    def test_next_by_code_uses_offset_directives(self):
        self.env["ir.sequence"].create(
            {
                "code": "test_sequence_date_offset_next",
                "name": "Test next by code",
                "prefix": "INV/%(year+1)s/%(month+1)s/%(day+1)s/",
                "padding": 4,
            }
        )

        value = (
            self.env["ir.sequence"]
            .with_context(ir_sequence_date="2024-12-31")
            .next_by_code("test_sequence_date_offset_next")
        )

        self.assertEqual(value, "INV/2025/01/01/0001")
