# See LICENSE file for full copyright and licensing details.

import os

from lxml.objectify import fromstring

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class MxEdiAddendaNissan(InvoiceTransactionCase):
    def setUp(self):
        super(MxEdiAddendaNissan, self).setUp()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'nissan'})
        conf.install_addenda()
        self.partner_agrolait.l10n_mx_edi_addenda = self.env.ref(
            'l10n_mx_edi_addendas.nissan')
        self.partner_agrolait.street_number2 = '8098'
        nissan_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'nissan_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(nissan_expected)

    def test_001_addenda_in_xml(self):
        """test addenda nissan"""
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        invoice.partner_shipping_id = self.partner_agrolait
        # wizard values
        invoice.x_addenda_nissan = '123|12|1234||10.00'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        nissan_nodes = xml.Addenda.getchildren()
        nissan_nodes[0].attrib['cCadena'] = ""
        nissan_nodes[1].Detalle.attrib['SERIE'] = ''
        nissan_nodes[1].Detalle.attrib['DOCUMENTO'] = ''
        self.assertEqualXML(xml.Addenda, self.addenda_tree)
