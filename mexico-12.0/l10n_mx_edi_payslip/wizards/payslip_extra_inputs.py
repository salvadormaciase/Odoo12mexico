# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class L10nMXHrPayslipExtras(models.TransientModel):
    _name = 'l10n_mx_edi.hr.payslip.extras'
    _description = 'Input and detail to write in the payslips related.'

    @api.model
    def default_get(self, fields_list):
        rec = super(L10nMXHrPayslipExtras, self).default_get(fields_list)
        slips = []
        for slip in self.env['hr.payslip'].browse(self._context.get('active_ids')).filtered(
                lambda p: p.state == 'draft'):
            slips.append((0, 0, {
                'payslip_id': slip.id, 'employee_id': slip.employee_id.id}))
        rec['slip_ids'] = slips
        return rec

    input_id = fields.Many2one(
        'hr.rule.input', 'Input to define in the payslips',
        help='This input will be added in all the payslips related.', required=True)
    slip_ids = fields.Many2many(
        'l10n_mx_edi.hr.payslip.extras.line', 'l10n_mx_edi_slip_extras', 'extra_id', 'slip_id',
        string='Slips', help='Indicate the amount to assign in each payslip.')

    def action_assign_extra(self):
        """Assign the extra input on the payslips"""
        for slip in self.slip_ids.filtered('amount'):
            line = slip.payslip_id.input_line_ids.filtered(lambda l: l.code == self.input_id.code)
            if line:
                line.amount = slip.amount
                slip.payslip_id.compute_sheet()
                continue
            slip.payslip_id.input_line_ids = [(0, 0, {
                'name': slip.detail or self.input_id.name,
                'amount': slip.amount,
                'code': self.input_id.code,
                'contract_id': slip.payslip_id.contract_id.id,
            })]
            slip.payslip_id.compute_sheet()


class L10nMXHrPayslipExtrasLine(models.Model):
    _name = 'l10n_mx_edi.hr.payslip.extras.line'
    _description = 'Detail to each input'

    payslip_id = fields.Many2one(
        'hr.payslip', 'Slip', help='Slip to add the extra input.', required=True)
    employee_id = fields.Many2one(
        'hr.employee', related='payslip_id.employee_id', help='Employee in the slip.')
    amount = fields.Float(
        help='Amount to assign on each payslip.\nNote: If the input could be taxed/exempt, only is need define the '
        'amount total.')
    detail = fields.Char(help='Indicate the detail for this input.\nExample: Commission SO1234')
