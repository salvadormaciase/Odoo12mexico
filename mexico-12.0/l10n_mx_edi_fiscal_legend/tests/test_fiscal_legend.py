# coding: utf-8
import base64

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestFiscalLegend(InvoiceTransactionCase):
    def setUp(self):
        super(TestFiscalLegend, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.namespaces = {
            'cfdi': 'http://www.sat.gob.mx/cfd/3',
            'leyendasFisc': 'http://www.sat.gob.mx/leyendasFiscales',
        }
        self.legend = self.env['l10n_mx_edi.fiscal.legend'].create({
            'name': "Legend's Text",
            'tax_provision': 'ISR',
            'rule': 'Article 1, paragraph 2',
        })

    def test_xml_node(self):
        """Validates that the XML node ``<leyendasFisc:LeyendasFiscales>`` is
            included when the invoice contains fiscal legends, and that
            its content is generated correctly
        """
        xml_expected = objectify.fromstring('''
            <leyendasFisc:LeyendasFiscales
                xmlns:leyendasFisc="http://www.sat.gob.mx/leyendasFiscales"
                version="1.0">
                <leyendasFisc:Leyenda
                    disposicionFiscal="ISR"
                    norma="Article 1, paragraph 2"
                    textoLeyenda="Legend's Text"/>
            </leyendasFisc:LeyendasFiscales>''')
        invoice = self.create_invoice()
        invoice.l10n_mx_edi_legend_ids = self.legend
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.l10n_mx_edi_pac_status, "signed",
            invoice.message_ids.mapped('body'))
        xml = objectify.fromstring(base64.b64decode(invoice.l10n_mx_edi_cfdi))
        self.assertTrue(xml.Complemento.xpath(
            'leyendasFisc:LeyendasFiscales', namespaces=self.namespaces),
            "The node '<leyendasFisc:LeyendasFiscales> should be present")
        xml_leyendas = xml.Complemento.xpath(
            'leyendasFisc:LeyendasFiscales', namespaces=self.namespaces)[0]
        self.assertEqualXML(xml_leyendas, xml_expected)
