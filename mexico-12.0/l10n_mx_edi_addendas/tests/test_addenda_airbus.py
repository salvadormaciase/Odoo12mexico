# See LICENSE file for full copyright and licensing details.

from .common import AddendasTransactionCase


class TestAddendaAirbus(AddendasTransactionCase):
    def setUp(self):
        super(TestAddendaAirbus, self).setUp()
        self.install_addenda('airbus')

    def test_addenda_airbus(self):
        invoice = self.create_invoice()
        invoice.currency_id = self.mxn.id
        invoice.invoice_line_ids.write({
            'x_addenda_sap_sequence': '01',
            'x_addenda_sap_code': 'CONS-CH-0079',
            'x_addenda_sap_uom': 'TR',
            'l10n_mx_edi_customs_number': '15  48  3009  0001234',
        })
        self.set_wizard_values(invoice, 'airbus', {
            'x_concept': 'CALIBRACIONES',
            'x_description': 'New purchase',
            'x_purchase_order': '4530023319',
            'x_reception_num': '7381890',
            'x_delivery_num': '234225',
            'x_type_operation': 'IMPORTACION',
        })
        invoice.sudo().partner_id.lang = 'en_US'
        invoice.sudo().partner_id.commercial_partner_id.country_id = self.env.ref('base.mx')
        invoice.sudo().partner_id.commercial_partner_id.vat = 'EMP110817U86'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")

        expected_addenda = self.get_expected_addenda('airbus')
        self.assertEqualXML(xml.Addenda, expected_addenda)

        # Validate that a supplier info was created for the product
        supplier_info = invoice.invoice_line_ids.product_id.seller_ids
        self.assertTrue(
            supplier_info, "A supplier info was not created for the product")
        self.assertEqual(len(supplier_info), 1)
        self.assertEqual(supplier_info.name, invoice.commercial_partner_id)
        self.assertEqual(supplier_info.product_id, self.product)
        self.assertEqual(supplier_info.product_code, 'CONS-CH-0079')
        self.assertEqual(supplier_info.x_addenda_uom_code, 'TR')
