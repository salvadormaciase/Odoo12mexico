# See LICENSE file for full copyright and licensing details.

from .common import AddendasTransactionCase


class TestAddendaNestle(AddendasTransactionCase):

    def setUp(self):
        super(TestAddendaNestle, self).setUp()
        self.install_addenda('nestle')
        self.partner_agrolait.write({
            'type': 'delivery',
            'city': 'City Test 1',
            'l10n_mx_edi_colony': 'Colony Test 1',
        })
        self.partner_agrolait.parent_id.write({
            'city': 'City Test 2',
            'l10n_mx_edi_colony': 'Colony Test 2',
        })

    def test_001_addenda_nestle(self):
        """Tests addenda for Nestle

        Tests both possible cases of the addenda for Nestle:
        - Customer invoice
        - Customer refund
        """
        # ---------------------
        # Test Customer Invoice
        # ---------------------
        invoice = self.create_invoice()
        invoice.write({
            'move_name': 'INV/2018/0932',
            'name': '369796',
        })
        invoice.invoice_line_ids.x_addenda_sap_code = 'SP-002'
        self.set_wizard_values(invoice, 'nestle', {
            'x_incoming_code': 'IC002',
        })

        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        expected_addenda = self.get_expected_addenda('nestle')
        self.assertEqualXML(xml.Addenda, expected_addenda)

        # --------------------
        # Test Customer refund
        # --------------------
        ctx = {'active_ids': invoice.ids}
        refund = self.env['account.invoice.refund'].with_context(ctx).create({
            'filter_refund': 'refund',
            'description': 'Refund Test',
            'date': invoice.date_invoice,
            'date_invoice': invoice.date_invoice,
        })
        result = refund.invoice_refund()
        refund_id = result.get('domain')[1][2]
        invoice_refund = self.invoice_model.browse(refund_id)
        invoice_refund.move_name = 'INV/2018/0933'
        invoice_refund.refresh()
        invoice_refund.action_invoice_open()
        self.assertEqual(invoice_refund.l10n_mx_edi_pac_status, "signed",
                         invoice_refund.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        invoice_refund.refresh()
        xml = invoice_refund.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        expected_addenda = self.get_expected_addenda('nestle_nc')
        self.assertEqualXML(xml.Addenda, expected_addenda)
