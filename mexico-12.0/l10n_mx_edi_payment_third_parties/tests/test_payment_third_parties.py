import base64
import os

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class TestPaymentThirdParties(InvoiceTransactionCase):
    def setUp(self):
        super(TestPaymentThirdParties, self).setUp()
        self.payment_obj = self.env['account.payment']
        self.payment_term = self.env.ref('account.account_payment_term')
        self.account = self.env['account.account'].search(
            [('name', '=', 'Bank')], limit=1)
        self.company.partner_id.property_account_position_id = \
            self.fiscal_position
        self.bank_journal = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        self.xml_expected_str = misc.file_open(os.path.join(
            'l10n_mx_edi_payment_third_parties', 'tests',
            'expected_payment.xml')).read().encode('UTF-8')

    def test_payment_third_parties(self):
        """Create invoice for third + Odoo invoice, and are both paid"""
        # Invoice from third
        xml_str = misc.file_open(os.path.join(
            'l10n_mx_edi_payment_third_parties', 'tests', 'bill.xml'
        )).read().encode('UTF-8')
        res = self.env['attach.xmls.wizard'].with_context(
            l10n_mx_edi_invoice_type='out',
            l10n_mx_edi_cfdi_third=True).check_xml({
                'bill.xml': base64.b64encode(xml_str).decode('UTF-8')})
        invoices = res.get('invoices', {})
        inv_id = invoices.get('bill.xml', {}).get('invoice_id', False)
        self.assertTrue(inv_id, "Error: Invoice creation")

        # Odoo invoice
        invoice = self.create_invoice()
        invoice.write({
            'number': 'INV/2018/1000',
            'payment_term_id': self.payment_term.id,
            'currency_id': self.mxn.id,
        })
        invoice.invoice_line_ids.write({
            'quantity': 1.0,
            'price_unit': 150000.00,
            'invoice_line_tax_ids': [(6, 0, [])]
        })
        invoice.compute_taxes()
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        payment = self.payment_obj.create({
            'name': 'CUST.IN/2018/999',
            'currency_id': self.mxn.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'payment_date': invoice.date,
            'l10n_mx_edi_payment_method_id': self.payment_method_cash.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_in').id,
            'journal_id': self.bank_journal.id,
            'communication': invoice.number,
            'amount': 225000.00,
            'payment_difference_handling': 'reconcile',
            'writeoff_account_id': self.account.id,
            'invoice_ids': [(6, 0, invoice.ids + [inv_id])],
        })
        payment.post()
        xml = payment.l10n_mx_edi_get_xml_etree()
        namespaces = {'pago10': 'http://www.sat.gob.mx/Pagos'}
        comp = xml.Complemento.xpath('//pago10:Pagos', namespaces=namespaces)
        self.assertTrue(comp[0], 'Complement to Pagos not added correctly')
        xml_expected = objectify.fromstring(self.xml_expected_str)
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        self.assertEqualXML(xml, xml_expected)
