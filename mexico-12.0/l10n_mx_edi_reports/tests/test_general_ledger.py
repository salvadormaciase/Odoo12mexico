# Part of Odoo. See LICENSE file for full copyright and licensing details.

from os.path import join
from dateutil.relativedelta import relativedelta
from lxml import objectify
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo import fields
from odoo.tools import misc


class TestJournalEntryReport(InvoiceTransactionCase):

    def setUp(self):
        super().setUp()
        self.journal_obj = self.env['account.journal']
        self.report_moves = self.env['l10n_mx.general.ledger.report']
        self.payments_model = self.env['account.register.payments']
        self.payment_obj = self.env['account.payment']
        self.env.ref('l10n_mx.1_tax9').l10n_mx_cfdi_tax_type = 'Tasa'
        self.journal_bank = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        self.date = fields.Datetime.context_timestamp(
            self.journal_bank, fields.Datetime.from_string(
                fields.Datetime.now())).replace(day=15)
        self.date = self.date - relativedelta(months=1)
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.xml_expected_str = misc.file_open(join(
            'l10n_mx_edi_reports', 'tests', 'expected_moves.xml')
        ).read().encode('UTF-8')
        self.payment_method_manual_out = self.env.ref(
            'account.account_payment_method_manual_out')
        self.transfer = self.env.ref(
            'l10n_mx_edi.payment_method_transferencia')
        self.bank_account = self.ref(
            'account_bank_statement_import.ofx_partner_bank_1')
        journal_acc = self.env['res.partner.bank'].create({
            'acc_number': '123456789012345',
            'bank_id': self.ref('l10n_mx_edi_bank.acc_bank_012_BBVA_BANCOMER'),
            'partner_id': self.company.partner_id.id,
        })
        self.journal_bank.bank_account_id |= journal_acc

    def test_001_get_report(self):
        self.product.taxes_id = False
        invoice = self.create_invoice(currency_id=self.mxn.id)
        invoice.date = self.date.date()
        invoice.tax_line_ids.unlink()
        invoice.compute_taxes()
        invoice.action_invoice_open()
        invoice.refresh()
        payment = self.generate_payment(invoice)
        payment2 = self.generate_payment(invoice)
        payment2.write({
            'l10n_mx_edi_payment_method_id': self.transfer.id,
            'l10n_mx_edi_partner_bank_id': self.bank_account,
        })
        options = self.report_moves._get_options()
        date = self.date.strftime('%Y-%m-%d')
        options.get('date', {})['date_from'] = date
        options.get('date', {})['date_to'] = date
        data = self.report_moves.get_xml(options)
        xml = objectify.fromstring(data)
        xml.attrib['Sello'] = ''
        xml.attrib['Certificado'] = ''
        xml.attrib['noCertificado'] = ''
        xml_dt = self.xml2dict(xml)
        self.xml_expected_str = self.xml_expected_str.decode().format(
            concept1=invoice.number, date=date, move1=invoice.move_id.id,
            uuid1=invoice.l10n_mx_edi_cfdi_uuid,
            payment_date=payment.payment_date,
            uuid2=payment.l10n_mx_edi_cfdi_uuid,
            move2=payment.move_line_ids.mapped('move_id').id,
            concept2=payment.communication,
            move3=payment2.move_line_ids.mapped('move_id').id,
            concept3=payment2.communication)
        xml_expected = objectify.fromstring(self.xml_expected_str.encode(
            'utf-8'))
        xml_expected.attrib['Mes'] = self.date.strftime('%m')
        xml_expected.attrib['Anio'] = self.date.strftime('%Y')
        xml_expected_dt = self.xml2dict(xml_expected)
        self.maxDiff = None
        self.assertEqual(xml_dt, xml_expected_dt)
        # Check the first payment
        xml.remove(xml.getchildren()[0])
        xml_expected.remove(xml_expected.getchildren()[0])
        xml_dt = self.xml2dict(xml)
        xml_expected_dt = self.xml2dict(xml_expected)
        self.assertEqual(xml_dt, xml_expected_dt)
        # Check the second payment
        xml.remove(xml.getchildren()[0])
        xml_expected.remove(xml_expected.getchildren()[0])
        xml_dt = self.xml2dict(xml)
        xml_expected_dt = self.xml2dict(xml_expected)
        self.assertEqual(xml_dt, xml_expected_dt)

    def generate_payment(self, invoice):
        # Register payment
        ctx = {'active_model': 'account.invoice', 'active_ids': [invoice.id]}
        today = self.company.l10n_mx_edi_certificate_ids.sudo().get_mx_current_datetime()  # noqa
        register_payments = self.payments_model.with_context(ctx).create({
            'payment_date': self.date,
            'l10n_mx_edi_payment_method_id': self.payment_method_cash.id,
            'payment_method_id': self.payment_method_manual_out.id,
            'journal_id': self.journal_bank.id,
            'communication': invoice.number,
            'amount': invoice.amount_total / 2,
            'currency_id': invoice.currency_id.id,
        })
        register_payments._onchange_payment_invoice()
        payment = register_payments.create_payments()
        return self.payment_obj.search(payment.get('domain', []))
