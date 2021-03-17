# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    l10n_mx_edi_structure_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    @api.multi
    def compute_sheet(self):
        """Inherit method to assign payment date in payslip created"""
        ctx = {'force_salary_rule_id': self.l10n_mx_edi_structure_id.id}
        res = super(HrPayslipEmployees, self.with_context(**ctx)).compute_sheet()
        payslip_obj = self.env['hr.payslip']
        active_id = self.env.context.get('active_id')
        payslips = payslip_obj.search([('payslip_run_id', '=', active_id)])
        [run_data] = self.env['hr.payslip.run'].browse(active_id).read(
            ['l10n_mx_edi_payment_date']) if active_id else []
        payslips.write({
            'l10n_mx_edi_payment_date': run_data.get(
                'l10n_mx_edi_payment_date', False),
            'number': payslips[0].payslip_run_id.name,
        })
        if self.l10n_mx_edi_structure_id:
            for payslip in payslips:
                company_id = (payslip.company_id or payslip.employee_id.company_id or
                              payslip.contract_id.company_id or payslip.company_id._company_default_get()).id
                inputs = payslip.with_context(**ctx).get_inputs(
                    payslip.contract_id, payslip.date_from, payslip.date_to)
                input_line_ids = [(0, 0, x) for x in inputs]
                payslip.write({'struct_id': self.l10n_mx_edi_structure_id.id,
                               'input_line_ids': [(5, 0, 0)] + input_line_ids,
                               'company_id': company_id,
                               })
        payslips.l10n_mx_edi_update_extras()
        return res
