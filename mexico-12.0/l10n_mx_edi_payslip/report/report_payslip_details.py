# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class PayslipDetailsReport(models.AbstractModel):
    _inherit = 'report.hr_payroll.report_payslipdetails'

    def get_details_by_rule_category(self, payslip_lines):
        return super(PayslipDetailsReport, self).get_details_by_rule_category(
            payslip_lines.filtered('amount'))
