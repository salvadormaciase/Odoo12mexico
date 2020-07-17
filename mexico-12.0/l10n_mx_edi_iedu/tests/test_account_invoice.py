# -*- coding: utf-8 -*-

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceIEDU(InvoiceTransactionCase):
    def setUp(self):
        super(TestL10nMxEdiInvoiceIEDU, self).setUp()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        self.company.company_registry = '5152'  # set institution code
        # set curp because group account invoice can't modify partners
        self.partner_agrolait.l10n_mx_edi_curp = "ROGC001031HJCDRR07"
        self.partner_agrolait.write({
            'category_id': [(4, self.ref('l10n_mx_edi_iedu.iedu_level_4'))],
        })

    def test_l10n_mx_edi_invoice_iedu(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        self.env['l10n_mx_edi_iedu.codes'].create({
            'journal_id': invoice.journal_id.id,
            'l10n_mx_edi_iedu_education_level_id': self.ref(
                'l10n_mx_edi_iedu.iedu_level_4'),
            'l10n_mx_edi_iedu_code': 'ES4-728L-3018'
        })
        invoice.invoice_line_ids.write({
            'l10n_mx_edi_iedu_id': self.partner_agrolait.id,
        })
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'iedu': "http://www.sat.gob.mx/iedu"
        }
        iedu = xml.Conceptos.Concepto.ComplementoConcepto.xpath(
            '//iedu:instEducativas', namespaces=namespaces)
        self.assertTrue(iedu, 'Iedu complement was not added correctly')

    def test_l10n_mx_edi_xsd(self):
        """Verify that xsd file is downloaded"""
        self.company._load_xsd_attachments()
        xsd_file = self.ref('l10n_mx_edi.xsd_cached_iedu_xsd')
        self.assertTrue(xsd_file, 'XSD file not load')
