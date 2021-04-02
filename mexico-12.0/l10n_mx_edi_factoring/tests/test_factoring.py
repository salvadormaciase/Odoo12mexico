from os import path

from lxml import objectify
from odoo.tools import misc

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestMxEdiFactoring(InvoiceTransactionCase):
    def setUp(self):
        super(TestMxEdiFactoring, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })

    def test_001_factoring(self):
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.l10n_mx_edi_pac_status, "signed",
            invoice.message_ids.mapped('body'))
        factoring = invoice.partner_id.sudo().create({
            'name': 'Financial Factoring',
            'country_id': self.env.ref('base.mx').id,
        })
        invoice.partner_id.sudo().commercial_partner_id.l10n_mx_edi_factoring_id = factoring.id  # noqa
        # Register the payment
        ctx = {'active_model': 'account.invoice', 'active_ids': invoice.ids}
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)
        register_payments = self.env['account.register.payments'].with_context(
            ctx).create({
                'payment_date': invoice.date,
                'l10n_mx_edi_payment_method_id': self.env.ref(
                    'l10n_mx_edi.payment_method_efectivo').id,
                'payment_method_id': self.env.ref(
                    "account.account_payment_method_manual_in").id,
                'journal_id': bank_journal.id,
                'communication': invoice.number,
                'amount': invoice.amount_total, })
        payment = register_payments.create_payments()
        payment = self.env['account.payment'].search(payment.get('domain', []))
        self.assertTrue(invoice.l10n_mx_edi_factoring_id,
                        'Financial Factor not assigned')
        xml_expected_str = misc.file_open(path.join(
            'l10n_mx_edi_factoring', 'tests',
            'expected_payment.xml')).read().encode('UTF-8')
        xml_expected = objectify.fromstring(xml_expected_str)
        xml = payment.l10n_mx_edi_get_xml_etree()
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        self.assertEqualXML(xml, xml_expected)
