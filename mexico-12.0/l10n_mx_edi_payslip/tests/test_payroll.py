# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import unittest
import time
from datetime import datetime, timedelta
from calendar import monthrange

from lxml import etree, objectify

import odoo

from .common import PayrollTransactionCase


class HRPayroll(PayrollTransactionCase):

    def test_001_xml_structure(self):
        """Use XML expected to verify that is equal to generated. And SAT
        status"""
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        payroll.l10n_mx_edi_update_sat_status()
        self.assertEquals(payroll.l10n_mx_edi_sat_status, 'not_found')
        xml = payroll.l10n_mx_edi_get_xml_etree()
        self.xml_expected.attrib['Fecha'] = xml.attrib['Fecha']
        self.xml_expected.attrib['Folio'] = xml.attrib['Folio']
        self.xml_expected.attrib['Sello'] = xml.attrib['Sello']
        node_payroll = payroll.l10n_mx_edi_get_payroll_etree(xml)
        node_expected = payroll.l10n_mx_edi_get_payroll_etree(
            self.xml_expected)
        self.assertTrue(node_payroll, 'Complement to payroll not added.')
        node_expected.Receptor.attrib['FechaInicioRelLaboral'] = node_payroll.Receptor.attrib['FechaInicioRelLaboral']  # noqa
        node_expected.attrib['FechaFinalPago'] = node_payroll.attrib['FechaFinalPago']  # noqa
        node_expected.attrib['FechaInicialPago'] = node_payroll.attrib['FechaInicialPago']  # noqa
        node_expected.attrib['FechaPago'] = node_payroll.attrib['FechaPago']
        node_expected.Receptor.attrib[u'Antig\xfcedad'] = node_payroll.Receptor.attrib[u'Antig\xfcedad']  # noqa

        # Replace node TimbreFiscalDigital
        tfd_expected = self.payslip_obj.l10n_mx_edi_get_tfd_etree(
            self.xml_expected)
        tfd_xml = objectify.fromstring(etree.tostring(
            self.payslip_obj.l10n_mx_edi_get_tfd_etree(xml)))
        self.xml_expected.Complemento.replace(tfd_expected, tfd_xml)
        self.assertEqualXML(xml, self.xml_expected)

    def test_002_perception_022(self):
        """When perception code have 022, the payroll have node
        SeparacionIndemnizacion."""
        self.struct = self.env.ref(
            'l10n_mx_edi_payslip.payroll_structure_data_03')
        payroll = self.create_payroll()
        date = payroll.l10n_mx_edi_payment_date - timedelta(days=380)
        self.contract.write({
            'date_start': date,
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_003_perception_039(self):
        """When perception code have 039, the payroll have node
        JubilacionPensionRetiro."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'pe_039',
                'name': u'Jubilaciones, pensiones o haberes de retiro',
                'amount': 1000.0,
                'contract_id': self.contract.id,
            })],
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_004_other_payment_002(self):
        """When other payment have the code 002, this must have node
        SubsidioAlEmpleo."""
        payroll = self.create_payroll()
        # Contract with a low salary that requires subsidy
        self.contract.wage = 5000
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        self.contract.wage = 74000
        payroll = self.create_payroll()
        payroll.write({
            'date_from': '%s-%s-16' % (
                time.strftime('%Y'), time.strftime('%m')),
            'date_to': '%s-%s-%s' % (
                time.strftime('%Y'), time.strftime('%m'),
                monthrange(payroll.date_to.year, payroll.date_to.month)[1])
        })
        payroll.action_payslip_done()
        self.assertEqual(payroll.l10n_mx_edi_pac_status, 'signed',
                         payroll.message_ids.mapped('body'))
        xml = payroll.l10n_mx_edi_get_xml_etree()
        payroll = payroll.l10n_mx_edi_get_payroll_etree(xml)
        de_107 = False
        for line in payroll.Deducciones.Deduccion:
            if line.get('Clave') == '107':
                de_107 = True
                break
        self.assertTrue(de_107, 'Deduction 107 not found.')

    def test_005_other_payment_004(self):
        """When other payment have the code 004, this must have node
        CompensacionSaldosAFavor."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'op_004',
                'name': u'Aplicación de saldo a favor por compensación anual.',
                'amount': 500.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_balance_favor': 500.0,
            'l10n_mx_edi_comp_year': (datetime.today()).year - 1,
            'l10n_mx_edi_remaining': 500.0,
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_006_perception_045(self):
        """When one perception have the code 045, this must have node
        AccionesOTitulos,."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'pe_045',
                'name': u'Ingresos en acciones o títulos valor que representan bienes',  # noqa
                'amount': 500.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_action_title_ids': [(0, 0, {
                'category_id': self.cat_excempt.id,
                'market_value': 100.0,
                'price_granted': 100.0,
            })]
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    @unittest.skip('Check PDF Format')
    def test_007_print_pdf(self):
        """Verify that PDF is generated"""
        # TODO: check this test
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        report = odoo.report.render_report(
            self.cr, self.uid, payroll.ids, 'hr_payroll.report_payslip',
            {'model': 'hr.payslip'}, context=self.env.context)
        self.assertTrue(report, 'Report not generated.')

    def test_008_cancel_xml(self):
        """Verify that XML is cancelled"""
        payroll = self.create_payroll()
        payroll.action_payslip_cancel()
        payroll.action_payslip_draft()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        payroll._compute_cfdi_values()
        payroll.action_payslip_cancel()
        self.assertTrue(
            payroll.l10n_mx_edi_pac_status in ['cancelled', 'to_cancel'],
            payroll.message_ids.mapped('body'))

    @unittest.skip('Check PDF Format')
    def test_009_send_payroll_mail(self):
        """Verify that XML is attach on wizard that send mail"""
        # TODO: check this test
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        mail_data = payroll.action_payroll_sent()
        template = mail_data.get('context', {}).get('default_template_id', [])
        template = self.env['mail.template'].browse(template)
        mail = template.generate_email(payroll.ids)
        self.assertEquals(len(mail[payroll.id].get('attachments')), 2,
                          'Documents not attached')

    def test_010_batches(self):
        """Verify payroll information and confirm payslips from batches"""
        date = (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        payslip_run = self.payslip_run_obj.create({
            'name': 'Payslip VX',
            'l10n_mx_edi_payment_date': date,
        })
        self.wizard_batch.create({
            'employee_ids': [(6, 0, self.employee.ids)]
        }).with_context(active_id=payslip_run.id).compute_sheet()
        self.assertEquals(
            payslip_run.slip_ids.l10n_mx_edi_payment_date.strftime('%Y-%m-%d'),
            date, 'Payment date not assigned in the payroll created.')
        payslip_in_batch = self.create_payroll()
        payslip_in_batch.payslip_run_id = payslip_run
        payslip_run.action_payslips_done()
        self.assertEquals(payslip_in_batch.l10n_mx_edi_pac_status, 'signed',
                          payslip_in_batch.message_ids.mapped('body'))

    def test_011_aguinaldo(self):
        """When in payslip has a perception of Christmas bonuses (Aguinaldo)"""
        self.struct = self.env.ref(
            'l10n_mx_edi_payslip.payroll_structure_data_02')
        payroll = self.create_payroll()
        date = payroll.l10n_mx_edi_payment_date - timedelta(days=380)
        self.contract.write({
            'date_start': date,
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        xml = payroll.l10n_mx_edi_get_xml_etree()
        node_payroll = payroll.l10n_mx_edi_get_payroll_etree(xml)
        self.assertEquals(
            '11000.00', node_payroll.get('TotalPercepciones', ''))

    def test_012_onchange_employee(self):
        """check if the company_id is set with onchange_employee"""
        company2 = self.env['res.company'].sudo().create({'name': 'Company2'})
        company3 = self.env['res.company'].sudo().create({'name': 'Company3'})
        self.employee.company_id = company2
        self.contract.company_id = company3
        payroll = self.create_payroll()
        payroll.onchange_employee()
        # payroll company is the same that employee
        self.assertEquals(payroll.company_id, company2,
                          'Company is not the employee company')
        self.employee.company_id = False
        payroll.onchange_employee()
        # payroll company is the same that contract
        self.assertEquals(payroll.company_id, company3,
                          'Company is not the contract company')
        self.contract.company_id = False
        payroll.onchange_employee()
        # payroll company is the default company
        self.assertEquals(payroll.company_id,
                          self.env['res.company']._company_default_get(),
                          'Company is not the default company')

    def test_013_resign_process(self):
        """Tests the re-sign process (recovery a previously signed xml)
        """
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEqual(payroll.l10n_mx_edi_pac_status, 'signed',
                         payroll.message_ids.mapped('body'))
        payroll.l10n_mx_edi_pac_status = 'retry'
        payroll.l10n_mx_edi_update_pac_status()
        for _x in range(10):
            if payroll.l10n_mx_edi_pac_status == 'signed':
                break
            time.sleep(2)
            payroll.l10n_mx_edi_retrieve_last_attachment().unlink()
            payroll.l10n_mx_edi_update_pac_status()
        self.assertEqual(payroll.l10n_mx_edi_pac_status, 'signed',
                         payroll.message_ids.mapped('body'))
        xml_attachs = payroll.l10n_mx_edi_retrieve_attachments()
        self.assertEqual(len(xml_attachs), 2)
        xml_1 = objectify.fromstring(base64.b64decode(xml_attachs[0].datas))
        xml_2 = objectify.fromstring(base64.b64decode(xml_attachs[1].datas))
        self.assertEqualXML(xml_1, xml_2)

    def test_014_assimilated(self):
        """Tests case when the employee is assimilated"""
        payroll = self.create_payroll()
        payroll.employee_id.l10n_mx_edi_is_assimilated = True
        payroll.employee_id.address_home_id.property_account_position_id = self.env.ref(
            'l10n_mx_edi_payslip.account_fiscal_position_09_emp')
        payroll.contract_id.type_id = self.env.ref('l10n_mx_edi_payslip.hr_contract_type_99')
        payroll.action_payslip_done()
        self.assertEqual(payroll.l10n_mx_edi_pac_status, 'signed',
                         payroll.message_ids.mapped('body'))

    def test_015_inabilities(self):
        """Ensure that inabilities are created"""
        leaves = self.env['hr.leave'].search([('employee_id', '=', self.employee.id)])
        leaves.action_refuse()
        leaves.action_draft()
        leaves.unlink()
        leave = self.env['hr.leave'].sudo().create({
            'name': 'Maternidad',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.env.ref('l10n_mx_edi_payslip.mexican_maternity').id,
            'date_from': '%s-%s-01' % (time.strftime('%Y'), time.strftime('%m')),
            'date_to': '%s-%s-03' % (time.strftime('%Y'), time.strftime('%m')),
            'number_of_days': 3,
        })
        leave.sudo().action_approve()
        self.contract.state = 'open'
        payroll = self.create_payroll()
        payroll.worked_days_line_ids.unlink()
        data = payroll.onchange_employee_id(
            payroll.date_from, payroll.date_to, payroll.employee_id.id, payroll.contract_id.id)
        payroll.write({'worked_days_line_ids': [(0, 0, x) for x in data['value'].get('worked_days_line_ids')]})
        payroll.action_payslip_done()
        xml = payroll.l10n_mx_edi_get_xml_etree()
        self.assertEqual(
            '03', payroll.l10n_mx_edi_get_payroll_etree(xml).Incapacidades.Incapacidad.get('TipoIncapacidad'),
            'Inability not added.')

    def test_016_inabilities(self):
        """Ensure that inabilities are created"""
        leaves = self.env['hr.leave'].search([('employee_id', '=', self.employee.id)])
        leaves.action_refuse()
        leaves.action_draft()
        leaves.unlink()
        leave = self.env['hr.leave'].sudo().create({
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.env.ref('l10n_mx_edi_payslip.mexican_riesgo_de_trabajo').id,
            'date_from': '%s-%s-01' % (time.strftime('%Y'), time.strftime('%m')),
            'date_to': '%s-%s-03' % (time.strftime('%Y'), time.strftime('%m')),
            'number_of_days': 3,
        })
        leave.action_approve()
        payroll = self.create_payroll()
        self.contract.state = 'open'
        payroll = self.create_payroll()
        payroll.worked_days_line_ids.unlink()
        data = payroll.onchange_employee_id(
            payroll.date_from, payroll.date_to, payroll.employee_id.id, payroll.contract_id.id)
        payroll.write({'worked_days_line_ids': [(0, 0, x) for x in data['value'].get('worked_days_line_ids')]})
        payroll.action_payslip_done()
        xml = payroll.l10n_mx_edi_get_xml_etree()
        self.assertEqual(
            '01', payroll.l10n_mx_edi_get_payroll_etree(xml).Incapacidades.Incapacidad.get('TipoIncapacidad'),
            'Inability not added.')

    def test_017_inabilities(self):
        """Ensure that inability for 'Enfermedad General' created"""
        leaves = self.env['hr.leave'].search([('employee_id', '=', self.employee.id)])
        leaves.action_refuse()
        leaves.action_draft()
        leaves.unlink()
        leave = self.env['hr.leave'].sudo().create({
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.env.ref('l10n_mx_edi_payslip.mexican_enfermedad_general').id,
            'date_from': '%s-%s-01' % (time.strftime('%Y'), time.strftime('%m')),
            'date_to': '%s-%s-07' % (time.strftime('%Y'), time.strftime('%m')),
            'number_of_days': 7,
        })
        leave.action_approve()
        payroll = self.create_payroll()
        self.contract.state = 'open'
        payroll = self.create_payroll()
        payroll.worked_days_line_ids.unlink()
        data = payroll.onchange_employee_id(
            payroll.date_from, payroll.date_to, payroll.employee_id.id, payroll.contract_id.id)
        payroll.write({'worked_days_line_ids': [(0, 0, x) for x in data['value'].get('worked_days_line_ids')]})
        payroll.action_payslip_done()
        xml = payroll.l10n_mx_edi_get_xml_etree()
        self.assertEqual(
            '02', payroll.l10n_mx_edi_get_payroll_etree(xml).Incapacidades.Incapacidad.get('TipoIncapacidad'),
            'Inability not added.')

    def test_018_inabilities(self):
        """Ensure that inability for 'Hijos con Cancer' is created"""
        leaves = self.env['hr.leave'].search([('employee_id', '=', self.employee.id)])
        leaves.action_refuse()
        leaves.action_draft()
        leaves.unlink()
        leave = self.env['hr.leave'].sudo().create({
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.env.ref('l10n_mx_edi_payslip.mexican_licencia_padres_hijo_cancer').id,
            'date_from': '%s-%s-01' % (time.strftime('%Y'), time.strftime('%m')),
            'date_to': '%s-%s-03' % (time.strftime('%Y'), time.strftime('%m')),
            'number_of_days': 3,
        })
        leave.action_approve()
        payroll = self.create_payroll()
        self.contract.state = 'open'
        payroll = self.create_payroll()
        payroll.worked_days_line_ids.unlink()
        data = payroll.onchange_employee_id(
            payroll.date_from, payroll.date_to, payroll.employee_id.id, payroll.contract_id.id)
        payroll.write({'worked_days_line_ids': [(0, 0, x) for x in data['value'].get('worked_days_line_ids')]})
        payroll.action_payslip_done()
        xml = payroll.l10n_mx_edi_get_xml_etree()
        self.assertEqual(
            '04', payroll.l10n_mx_edi_get_payroll_etree(xml).Incapacidades.Incapacidad.get('TipoIncapacidad'),
            'Inability not added.')
