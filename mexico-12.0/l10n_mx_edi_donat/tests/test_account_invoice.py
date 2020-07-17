# coding: utf-8

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceDonat(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiInvoiceDonat, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.namespaces = {
            'donat': 'http://www.sat.gob.mx/donat'}
        self.partner_agrolait.write({
            'l10n_mx_edi_donations': True,
        })
        self.company.write({
            'l10n_mx_edi_donat_auth': '12345',
            'l10n_mx_edi_donat_date': '2017-01-23',
            'l10n_mx_edi_donat_note': 'Este comprobante ampara un donativo,'
            ' el cual será destinado por la donataria a los fines propios de'
            ' su objeto social. En el caso de que los bienes donados hayan'
            ' sido deducidos previamente para los efectos del impuesto sobre'
            ' la renta, este donativo no es deducible.',
        })
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })

    def test_l10n_mx_edi_invoice_donat(self):
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        scp = xml.Complemento.xpath('//donat:Donatarias',
                                    namespaces=self.namespaces)
        self.assertTrue(scp, 'Complement to Donatarias not added correctly')
