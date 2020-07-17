# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrContractType(models.Model):
    _inherit = "hr.contract.type"

    l10n_mx_edi_code = fields.Char(
        'Code', help='Code defined by SAT to this contract type.')


class L10nMxEdiJobRank(models.Model):
    _name = "l10n_mx_edi.job.risk"
    _description = "Used to define the percent of each job risk."

    name = fields.Char(help='Job risk provided by the SAT.')
    code = fields.Char(help='Code assigned by the SAT for this job risk.')
    percentage = fields.Float(help='Percentage for this risk, is used in the '
                              'payroll rules.', digits=(2, 6),)


class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = 'Allow register the loans in each employee (Fonacot)'

    name = fields.Char(
        'Number', help='Number for this record, if comes from Fonacot, use '
        '"No. Credito"', required=True)
    monthly_withhold = fields.Float(
        help='Indicates the amount to withhold in a monthly basis.')
    payment_term = fields.Integer(
        help='Indicates the payment term for this loan.')
    payslip_ids = fields.Many2many(
        'hr.payslip', help='Payslips where this loan is collected.')
    payslips_count = fields.Integer(
        'Number of Payslips', compute='_compute_payslips_count')
    loan_type = fields.Selection([
        ('company', 'Company'),
        ('fonacot', 'Fonacot'),
    ], 'Type', help='Indicates the loan type.')
    employee_id = fields.Many2one(
        'hr.employee', help='Employee for this loan')
    number_fonacot = fields.Char(
        help='If comes from Fonacot, indicate the number.')
    active = fields.Boolean(
        help='If the loan was paid the record will be deactivated.',
        default=True)

    @api.multi
    def _compute_payslips_count(self):
        for loan in self:
            loan.payslips_count = len(loan.payslip_ids.filtered(
                lambda rec: rec.state == 'done'))

    @api.multi
    def action_get_payslips_view(self):
        return {
            'name': _('Loan Payslips'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payslip_ids.filtered(
                lambda rec: rec.state == 'done').ids)],
        }
