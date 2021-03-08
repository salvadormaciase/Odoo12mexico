# See LICENSE file for full copyright and licensing details.

from .common import AddendasTransactionCase


class TestAddendaEnvases(AddendasTransactionCase):

    def setUp(self):
        super(TestAddendaEnvases, self).setUp()
        self.install_addenda('envases')
        self.namespaces = {
            "eu": "http://factura.envasesuniversales.com/addenda/eu"
        }

    def test_001_addenda_envases(self):
        invoice = self.create_invoice()
        self.set_wizard_values(invoice, 'envases', {
            'x_incoming_code': '12345',
        })

        invoice.move_name = "INV/2018/987456"
        invoice.name = "PO456"

        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is no Addenda node")

        expected_addenda = self.get_expected_addenda('envases')
        xml.xpath('//eu:TipoFactura/eu:FechaMensaje',
                  namespaces=self.namespaces)[0]._setText('2018-12-06')

        self.assertEqualXML(xml.Addenda, expected_addenda)
