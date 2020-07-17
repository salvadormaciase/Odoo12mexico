# See LICENSE file for full copyright and licensing details.

import os

from lxml.objectify import fromstring

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class MxEdiAddendaPepsico(InvoiceTransactionCase):
    def setUp(self):
        super().setUp()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'pepsico'})
        conf.install_addenda()
        self.partner_agrolait.l10n_mx_edi_addenda = self.env.ref(
            'l10n_mx_edi_addendas.pepsico')
        self.partner_agrolait.ref = '1000007516'
        addenda_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'pepsico_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(addenda_expected)

    def test_001_addenda_in_xml(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        invoice.write({
            'name': '0151',
            'currency_id': self.mxn.id,
        })
        # wizard values
        invoice.x_addenda_pepsico = '000|5029374767'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        uuid = invoice.l10n_mx_edi_cfdi_uuid
        self.addenda_tree.xpath('//Documento')[0].attrib['folioUUID'] = uuid
        self.assertEqualXML(xml.Addenda, self.addenda_tree)
