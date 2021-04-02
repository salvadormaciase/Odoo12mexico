# See LICENSE file for full copyright and licensing details.
from .common import AddendasTransactionCase


class TestAddendaVallen(AddendasTransactionCase):
    def setUp(self):
        super(TestAddendaVallen, self).setUp()
        self.install_addenda('vallen')

    def test_001_addenda_vallen(self):
        invoice = self.create_invoice()
        invoice.name = '0131'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        xml.Addenda.find('requestForPayment').set('DeliveryDate', '2018-12-16')
        expected_addenda = self.get_expected_addenda('vallen')
        self.assertEqualXML(xml.Addenda, expected_addenda)
