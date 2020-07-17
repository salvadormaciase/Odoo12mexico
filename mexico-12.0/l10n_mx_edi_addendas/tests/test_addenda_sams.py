# LICENSE file for full copyright and licensing details.

import os
from lxml.objectify import fromstring
from odoo.tools import misc
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class MxEdiAddendaSams(InvoiceTransactionCase):
    def setUp(self):
        super(MxEdiAddendaSams, self).setUp()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'sams'})
        conf.install_addenda()
        self.partner_agrolait.l10n_mx_edi_addenda = self.env.ref(
            'l10n_mx_edi_addendas.sams')
        self.partner_agrolait.street_number2 = '8098'
        sams_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'sams_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(sams_expected)

    def test_001_addenda_in_xml(self):
        """test addenda sams"""""
        invoice = self.create_invoice()
        invoice.partner_shipping_id = self.partner_agrolait
        # wizard values
        invoice.x_addenda_sams = '9250113699|20200619|185853950'
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        sams_nodes = xml.Addenda.getchildren()
        sams_nodes[0] = ""
        self.assertEqualXML(xml.Addenda, self.addenda_tree)
