# LICENSE file for full copyright and licensing details.

from lxml import etree

from .common import AddendasTransactionCase


class TestAddendaSams(AddendasTransactionCase):

    def setUp(self):
        super(TestAddendaSams, self).setUp()
        self.install_addenda('sams')

    def test_addenda_sams(self):
        """Test addenda for SAMS"""""
        self.partner_agrolait.street_number2 = '8098'
        invoice = self.create_invoice()
        invoice.invoice_line_ids.invoice_line_tax_ids = [(6, 0, self.tax_positive.ids)]
        invoice.compute_taxes()
        invoice.partner_shipping_id = self.partner_agrolait
        invoice.partner_shipping_id.sudo().ref = '7507003100001'
        # wizard values
        invoice.x_addenda_sams = '20200619'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        expected_addenda = self.get_expected_addenda('sams')
        addenda = etree.tostring(expected_addenda)
        date_time = '{date}{time}'.format(date=invoice.date_invoice.strftime('%Y%m%d'), time=(
            invoice.l10n_mx_edi_time_invoice or '000000').replace(':', ''))
        addenda = addenda.replace(
            b'-folio-', invoice._l10n_mx_get_serie_and_folio(invoice.number)['folio'].encode()).replace(
                b'-date-', invoice.date_invoice.strftime('%y%m%d').encode()).replace(
                    b'-time-', (invoice.l10n_mx_edi_time_invoice or '0000').replace(':', '')[:4].encode()).replace(
                        b'-datetime-', date_time.encode(),
                    )
        self.assertEqualXML(xml.Addenda, etree.fromstring(addenda))
