# See LICENSE file for full copyright and licensing details.

from .common import AddendasTransactionCase


class TestAddendaFord(AddendasTransactionCase):

    def setUp(self):
        super(TestAddendaFord, self).setUp()
        self.install_addenda('ford')

    def test_001_addenda_ford_with_asn(self):
        """Test case: generate addenda Ford providing ASN numbers"""
        invoice = self.create_invoice()
        self.set_wizard_values(invoice, 'ford', {
            'x_gsdb': 'GYFZA',
            'x_asn': 'ASN1,ASN2',
        })

        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        expected_addenda = self.get_expected_addenda('ford')
        self.assertEqualXML(xml.Addenda, expected_addenda)

    def test_002_addenda_ford_wo_asn(self):
        """Test case: generate addenda Ford without providing an ASN number

        When the ASN number is not provided, is should be taken from the
        invoice's folio.
        """
        invoice = self.create_invoice()
        self.set_wizard_values(invoice, 'ford', {
            'x_gsdb': 'GYFZA',
        })
        invoice.move_name = 'INV/2018/0921'

        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        expected_addenda = self.get_expected_addenda('ford_wo_asn')
        self.assertEqualXML(xml.Addenda, expected_addenda)
