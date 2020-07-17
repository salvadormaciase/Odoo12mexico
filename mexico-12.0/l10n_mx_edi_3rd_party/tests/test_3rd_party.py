# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

import base64
import os

from lxml import objectify

from odoo import tools
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class Test3rdParty(InvoiceTransactionCase):

    def setUp(self):
        super(Test3rdParty, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.namespaces = {
            'cfdi': 'http://www.sat.gob.mx/cfd/3',
            'terceros': 'http://www.sat.gob.mx/terceros',
        }
        self.third = self.env.ref('base.res_partner_main2')
        self.third.write({
            'city_id': self.ref('l10n_mx_edi.res_city_mx_son_001') or self.ref(
                'l10n_mx_edi_3rd_party.res_city_mx_son_001'),
        })

    def create_invoice_line_to_3rd(self, invoice, product):
        self.create_invoice_line(invoice)
        invoice_line = invoice.invoice_line_ids[-1]
        invoice_line.write({
            'product_id': product.id,
            'l10n_mx_edi_3rd_party_id': self.third.id,
        })
        invoice_line._onchange_product_id()
        return invoice_line

    def test_xml_node(self):
        """Validates the XML node of the third party complement

        Validates that the XML node ``<terceros:PorCuentadeTerceros>`` is
        included, and that its content is generated correctly.

        This test covers all three possible cases of products sold on
        behalf of third parties:
        1. The product is imported and sold first hand
        2. The product is made from other products (parts or components). This
           also covers the case when one of its parts is imported and sold
           first hand.
        3. The product is a lease
        """
        invoice = self.create_invoice()

        # Case 1: the product is imported and sold first hand
        imported_product = self.env.ref('product.product_product_24')
        imported_product.write({
            'l10n_mx_edi_code_sat_id':
                self.ref('l10n_mx_edi.prod_code_sat_43201401'),
        })
        line = self.create_invoice_line_to_3rd(invoice, imported_product)
        line.l10n_mx_edi_customs_number = '15  48  3009  0001234'
        line.l10n_mx_edi_customs_date = '2015-01-01'
        line.l10n_mx_edi_customs_name = "Mexico City's customs"

        # Case 2: the product is made from other products
        # There's a BoM for the default product, it doesn't need to be created
        self.create_invoice_line_to_3rd(invoice, self.product)
        self.product.bom_ids.bom_line_ids[0].write({
            'l10n_mx_edi_customs_number': '15  48  3009  0001234',
            'l10n_mx_edi_customs_date': '2015-01-01',
            'l10n_mx_edi_customs_name': "Mexico City's customs",
        })

        # Case 3: the product is a lease
        lease_product = self.env.ref('product.service_cost_01')
        lease_product.write({
            'name': 'House Lease',
            'l10n_mx_edi_code_sat_id':
                self.ref('l10n_mx_edi.prod_code_sat_80131501'),
            'l10n_mx_edi_property_tax': 'CP1234',
        })
        self.create_invoice_line_to_3rd(invoice, lease_product)
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = objectify.fromstring(base64.b64decode(invoice.l10n_mx_edi_cfdi))
        self.assertEqual(
            len(xml.Conceptos.Concepto), 4,
            "There should be exactly four nodes 'Concepto'")
        # Retrieve nodes <PorCuentadeTerceros> from all concepts
        node0 = xml.Conceptos.Concepto[0].find(
            'cfdi:ComplementoConcepto/terceros:PorCuentadeTerceros',
            namespaces=self.namespaces)
        node1 = xml.Conceptos.Concepto[1].find(
            'cfdi:ComplementoConcepto/terceros:PorCuentadeTerceros',
            namespaces=self.namespaces)
        node2 = xml.Conceptos.Concepto[2].find(
            'cfdi:ComplementoConcepto/terceros:PorCuentadeTerceros',
            namespaces=self.namespaces)
        node3 = xml.Conceptos.Concepto[3].find(
            'cfdi:ComplementoConcepto/terceros:PorCuentadeTerceros',
            namespaces=self.namespaces)
        # All but the first node shoulb be present
        error_msg = ("Node <terceros:PorCuentadeTerceros> should%sbe present "
                     "for concept #%s")
        self.assertIsNone(node0, error_msg % (' not ', '1'))
        self.assertIsNotNone(node1, error_msg % (' ', '2'))
        self.assertIsNotNone(node2, error_msg % (' ', '3'))
        self.assertIsNotNone(node2, error_msg % (' ', '3'))

        xmlpath = os.path.join(os.path.dirname(__file__), 'expected_nodes.xml')
        with tools.file_open(xmlpath, mode='rb') as xmlfile:
            xml_expected = objectify.fromstring(xmlfile.read())
        nodes_expected = xml_expected.findall(
            'terceros:PorCuentadeTerceros', namespaces=self.namespaces)
        self.assertEqualXML(node1, nodes_expected[0])
        self.assertEqualXML(node2, nodes_expected[1])
        self.assertEqualXML(node3, nodes_expected[2])
