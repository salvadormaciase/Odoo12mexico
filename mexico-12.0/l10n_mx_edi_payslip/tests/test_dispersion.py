
from datetime import datetime, timedelta

from .common import PayrollTransactionCase
from odoo.exceptions import UserError


class TestPayrollDispersion(PayrollTransactionCase):

    def setUp(self):
        super(TestPayrollDispersion, self).setUp()
        self.uid = self.env.ref('l10n_mx_edi_payslip.payroll_mx_manager')
        self.payslip_obj = self.env['hr.payslip']
        self.payslip_run_obj = self.env['hr.payslip.run']
        self.employee = self.env.ref('hr.employee_qdp')
        self.contract = self.env.ref('hr_payroll.hr_contract_gilles_gravie')
        self.contract.compute_integrated_salary()
        self.struct = self.env.ref('l10n_mx_edi_payslip.payroll_structure_data_01')

        self.date = datetime.today() + timedelta(days=5)
        self.payslip_run = self.payslip_run_obj.create({
            'name': 'Payslip VX',
            'l10n_mx_edi_payment_date': self.date.strftime('%Y-%m-%d'),
        })
        self.payroll = self.create_payroll()
        self.payroll.compute_sheet()
        self.payroll.payslip_run_id = self.payslip_run
        self.dispersion_group = self.env.ref('l10n_mx_edi_payslip.l10n_mx_edi_allow_print_payslip_dispertion', False)
        self.dispersion_group.sudo().write({'users': [(6, 0, [self.env.user.id, 1])]})

    def test_001_payslip_dispersion(self):
        """Test BBVA text and permissions"""
        self.employee.bank_account_id.bank_id = self.env.ref('l10n_mx_edi_bank.acc_bank_012_BBVA_BANCOMER')
        report_name = self.payslip_run._get_payslips_dispersion_report_name("BBVA BANCOMER")
        self.assertEqual(report_name, 'BBVA_BANCOMER_%s_Payslip_VX' % self.date.strftime('%d_%m_%Y'),
                         'Wrong payslip dispersion file name')

        # Check permissions just with the group can perform the dispersion text
        # remove permission group to perform the test
        self.dispersion_group.sudo().write({'users': [(5, 0, 0)]})
        msg = "Only Managers with the group 'Allow to Print Payslip Dispersion' can generate payslip dispersion files"
        with self.assertRaises(UserError, msg=msg):
            self.payslip_run._get_payslips_dispersions()

        # Give back permission and finish test normal flow
        self.dispersion_group.sudo().write({'users': [(6, 0, [self.env.user.id, 1])]})
        dispersion_text = self.payslip_run._generate_bbva_dispersion(self.payroll)
        # Preparing amount
        amount = self.payroll.line_ids.filtered(lambda s: s.code == "NetSalary").total
        amount = str(amount).replace('.', '').zfill(15)
        self.assertEqual(
            dispersion_text,
            '000000001                991234567890          %s'
            'Marc Demo                               001001\n' % amount,
            'Wrong payslip dispersion template')

    def test_002_santander(self):
        """Test Sandander Text Generation. For now, dummy, change it when santander is supported"""
        self.employee.bank_account_id.bank_id = self.env.ref('l10n_mx_edi_bank.acc_bank_014_SANTANDER')
        report_name = self.payslip_run._get_payslips_dispersion_report_name("SANTANDER")
        self.assertEqual(report_name, 'SANTANDER_%s_Payslip_VX' % self.date.strftime('%d_%m_%Y'),
                         'Wrong payslip dispersion file name')

        dispersion_text = self.payslip_run._generate_santander_dispersion(self.payroll)
        # Preparing amount
        amount = self.payroll.line_ids.filtered(lambda s: s.code == "NetSalary").total
        amount = str(amount).replace('.', '').zfill(15)
        self.assertEqual(
            dispersion_text,
            '000000001                991234567890          %s'
            'Marc Demo                               001001\n' % amount,
            'Wrong payslip dispersion template')
