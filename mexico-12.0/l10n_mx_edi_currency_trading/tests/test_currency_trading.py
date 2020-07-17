# coding: utf-8
import base64

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.exceptions import ValidationError


class TestCurrencyTrading(InvoiceTransactionCase):
    def setUp(self):
        super(TestCurrencyTrading, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.namespaces = {
            'cfdi': 'http://www.sat.gob.mx/cfd/3',
            'divisas': 'http://www.sat.gob.mx/divisas',
        }
        self.product2 = self.env.ref("product.product_product_4")
        self.product2.l10n_mx_edi_code_sat_id = self.ref(
            'l10n_mx_edi.prod_code_sat_01010101')

    def test_xml_node(self):
        """Validates that the XML node ``<divisas:Divisas>`` is included only
            when the field Exchange operation type is specified on a product,
            and that its content is generated correctly
        """
        # First, creates an invoice without any exchange operation type on any
        # of its products. XML node should not be included
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.l10n_mx_edi_pac_status, "signed",
            invoice.message_ids.mapped('body'))
        xml = objectify.fromstring(base64.b64decode(invoice.l10n_mx_edi_cfdi))
        error_msg = "The node '<divisas:Divisas> should not be present"
        self.assertFalse(xml.Complemento.xpath(
            'divisas:Divisas', namespaces=self.namespaces), error_msg)

        # Then, set the field on the product and re-sign.
        # This time, the XML node should be included
        xml_expected = objectify.fromstring('''
            <divisas:Divisas
                xmlns:divisas="http://www.sat.gob.mx/divisas"
                version="1.0"
                tipoOperacion="venta"/>''')
        self.product.sudo().l10n_mx_edi_ct_type = 'sale'
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.l10n_mx_edi_pac_status, "signed",
            invoice.message_ids.mapped('body'))
        xml = objectify.fromstring(base64.b64decode(invoice.l10n_mx_edi_cfdi))
        error_msg = "The node '<divisas:Divisas> should be present"
        self.assertTrue(xml.Complemento.xpath(
            'divisas:Divisas', namespaces=self.namespaces), error_msg)
        xml_divisas = xml.Complemento.xpath(
            'divisas:Divisas', namespaces=self.namespaces)[0]
        self.assertEqualXML(xml_divisas, xml_expected)

    def test_ct_types_dont_match(self):
        """Validates that, when an invoice are issued for multiple products,
            and the field Exchange operation type are set but they're not the
            same for all products, an exception is raised
        """
        self.product.sudo().l10n_mx_edi_ct_type = 'sale'
        self.product2.sudo().l10n_mx_edi_ct_type = 'purchase'
        invoice = self.create_invoice()
        invoice.invoice_line_ids |= invoice.invoice_line_ids.copy()
        invoice.invoice_line_ids[1].product_id = self.product2.id
        error_msg = ("This invoice contains products with different exchange "
                     "operation types.")
        with self.assertRaisesRegexp(ValidationError, error_msg):
            invoice.action_invoice_open()
