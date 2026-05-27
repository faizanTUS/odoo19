# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models


class HrInReportWizardFleetAssignment(models.TransientModel):
    _name = "hr.in.report.wizard.fleet.assign"
    _description = "Vehicle assignment & cost slice"
    _inherit = ["hr.in.report.wizard.mixin"]
    _report_requires_hrms_manager = True

    def _pdf_report_xmlid(self):
        return "IndiaHrReportscommunity.action_report_fleet_assign"

    def _get_dataset(self):
        self.ensure_one()
        dom = [("company_id", "in", self.company_ids.ids)]
        vehicles = self.env["fleet.vehicle"].search(dom, order="license_plate")
        self._enforce_row_cap(len(vehicles))
        cols = [
            ("name", "Vehicle"),
            ("license", "License plate"),
            ("model", "Model"),
            ("driver", "Driver"),
            ("company", "Company"),
            ("acquisition", "Acquisition date"),
            ("odometer", "Odometer"),
        ]
        rows = []
        for v in vehicles:
            drv = getattr(v, "driver_employee_id", None) or getattr(v, "driver_id", None)
            drv_name = drv.name if drv else ""
            rows.append(
                {
                    "name": v.name or "",
                    "license": v.license_plate or "",
                    "model": v.model_id.name if v.model_id else "",
                    "driver": drv_name,
                    "company": v.company_id.name or "",
                    "acquisition": v.acquisition_date or "",
                    "odometer": v.odometer or "",
                }
            )
        return {
            "title": "Vehicle assignment & cost slice",
            "filename": "in_fleet_assignment_cost",
            "sheet_name": "fleet",
            "columns": cols,
            "rows": rows,
        }
