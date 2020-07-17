# See LICENSE file for full copyright and licensing details.

from .common import AddendasTransactionCase


class TestAddendaZfmexico(AddendasTransactionCase):

    def setUp(self):
        super(TestAddendaZfmexico, self).setUp()
        self.install_addenda('zfmexico')

    def test_001_addenda_zfmexico(self):
        invoice = self.create_invoice()
        invoice.write({
            'name': '5644544',
            'move_name': "INV/2018/1003",
        })

        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        expected_addenda = self.get_expected_addenda('zfmexico')
        self.assertEqualXML(xml.Addenda, expected_addenda)
