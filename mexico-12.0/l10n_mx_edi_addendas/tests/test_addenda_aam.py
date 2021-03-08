# See LICENSE file for full copyright and licensing details.

from .common import AddendasTransactionCase


class TestAddendaAam(AddendasTransactionCase):

    def setUp(self):
        super(TestAddendaAam, self).setUp()
        self.install_addenda('aam')

    def test_001_addenda_aam(self):
        invoice = self.create_invoice()
        invoice.name = '369796'
        invoice.invoice_line_ids.write({
            'x_addenda_sap_description': 'Desk Combination Standard',
            'x_addenda_sap_code': 'FURN-7800',
            'x_addenda_sap_uom': 'PCS',
        })
        self.set_wizard_values(invoice, 'aam', {
            'x_operational_organization': 'GMC',
        })

        invoice.sudo().partner_id.lang = 'en_US'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        # PDF may not be printed in test mode. We used to set the config param
        # test_report_directory=True to achieve that, but that param was
        # removed by Odoo (see odoo/odoo@ad7bf6b9c9b3)
        xml.Addenda.getchildren()[0].Archivo.set('datos', 'PDF in base64')
        expected_addenda = self.get_expected_addenda('aam')
        self.assertEqualXML(xml.Addenda, expected_addenda)

        # Validate that a supplier info was created for the product
        supplier_info = invoice.invoice_line_ids.product_id.seller_ids
        self.assertTrue(
            supplier_info, "A supplier info was not created for the product")
        self.assertEqual(len(supplier_info), 1)
        self.assertEqual(supplier_info.name, invoice.commercial_partner_id)
        self.assertEqual(supplier_info.product_id, self.product)
        self.assertEqual(
            supplier_info.product_name, 'Desk Combination Standard')
        self.assertEqual(supplier_info.product_code, 'FURN-7800')
        self.assertEqual(supplier_info.x_addenda_uom_code, 'PCS')

        # If another invoice is created for the same product and values are not
        # filled, they should be taken from the supplierinfo
        invoice = self.create_invoice()
        invoice.name = '369796'
        invoice.sudo().partner_id.lang = 'en_US'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        # Check addenda has been appended and it's equal to the expected one
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")
        # Since we didn't set any addenda value, the operational organization
        # won't be set, so it needs to be set on the generated XML
        xml.Addenda.getchildren()[0].set('OrganizacionOperacional', 'GMC')
        xml.Addenda.getchildren()[0].Archivo.set('datos', 'PDF in base64')
        expected_addenda = self.get_expected_addenda('aam')
        self.assertEqualXML(xml.Addenda, expected_addenda)
