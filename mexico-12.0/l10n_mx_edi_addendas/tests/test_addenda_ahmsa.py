# See LICENSE file for full copyright and licensing details.

import os

from lxml.objectify import fromstring

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class MxEdiAddendaAhmsa(InvoiceTransactionCase):
    def setUp(self):
        super().setUp()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'ahmsa'})
        conf.install_addenda()
        self.partner_agrolait.write({
            'l10n_mx_edi_addenda': self.ref('l10n_mx_edi_addendas.ahmsa'),
            'ref': '0000123456',
        })
        self.partner_agrolait.commercial_partner_id.vat = 'MNO810731QF9'
        ahmsa_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'ahmsa_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(ahmsa_expected)

    def test_001_addenda_in_xml(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        invoice.currency_id = self.mxn.id
        # wizard values
        invoice.x_addenda_ahmsa = '1|PE|D002||||||||'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        self.assertEqualXML(xml.Addenda, self.addenda_tree)
