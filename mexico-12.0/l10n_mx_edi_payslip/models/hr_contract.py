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
    _inherit = ['mail.thread']
    _description = 'Allow register the loans in each employee (Fonacot)'

    name = fields.Char(
        'Number', help='Number for this record, if comes from Fonacot, use '
        '"No. Credito"', required=True, track_visibility='onchange')
    monthly_withhold = fields.Float(
        help='Indicates the amount to withhold in a monthly basis.', track_visibility='onchange')
    payment_term = fields.Integer(
        help='Indicates the payment term for this loan.', track_visibility='onchange')
    payslip_ids = fields.Many2many(
        'hr.payslip', help='Payslips where this loan is collected.')
    payslips_count = fields.Integer(
        'Number of Payslips', compute='_compute_payslips_count')
    loan_type = fields.Selection([
        ('internal', 'Internal Discount'),
        ('company', 'Company'),
        ('fonacot', 'Fonacot'),
    ], 'Type', help='Indicates the loan type.', track_visibility='onchange', required=True)
    employee_id = fields.Many2one(
        'hr.employee', help='Employee for this loan', track_visibility='onchange')
    number_fonacot = fields.Char(
        help='If comes from Fonacot, indicate the number.', track_visibility='onchange')
    active = fields.Boolean(
        help='If the loan was paid the record will be deactivated.',
        default=True, track_visibility='onchange')

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


class L10nMxEdiEmployerRegistration(models.Model):
    _name = 'l10n_mx_edi.employer.registration'
    _description = 'Allow define all the employer registration from the company'
    _inherit = ['mail.thread']

    name = fields.Char(
        help='Value to set in the "RegistroPatronal" attribute.')
    job_risk_id = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.', required=True)
