import base64

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceEAPA(InvoiceTransactionCase):

    def test_l10n_mx_edi_invoice_eapa(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.product.write({
            'l10n_mx_edi_art_complement': 'eapa',
            'l10n_mx_edi_good_type': '03',
            'l10n_mx_edi_acquisition': '05',
            'l10n_mx_edi_other_good_type': 'Was found in a construction',
            'l10n_mx_edi_tax_paid': '15.00',
            'l10n_mx_edi_acquisition_date': '2015/07/01',
            'l10n_mx_edi_characteristic': '06',
            'standard_price': 1000,
        })
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'obrasarte': 'http://www.sat.gob.mx/arteantiguedades'}
        eapa = xml.Complemento.xpath('//obrasarte:obrasarteantiguedades',
                                     namespaces=namespaces)
        self.assertTrue(eapa, 'Complement to EAPA not added correctly')

    def test_l10n_mx_edi_xsd(self):
        """Verify that xsd file is downloaded"""
        self.company._load_xsd_attachments()
        xsd_file = self.ref(
            'l10n_mx_edi.xsd_cached_obrasarteantiguedades_xsd')
        self.assertTrue(xsd_file, 'XSD file not load')

    def test_invoice_payment_in_kind(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.donation = self.env['product.product'].create({
            'name': 'Painting',
            'lst_price': '1.00',
            'l10n_mx_edi_art_complement': 'pee',
            'l10n_mx_edi_good_type': '04',
            'l10n_mx_edi_other_good_type': 'oil painting',
            'l10n_mx_edi_acquisition_date': '2000/01/19',
            'l10n_mx_edi_pik_dimension': '2m height and 2m width',
        })
        self.donation.l10n_mx_edi_code_sat_id = self.ref('l10n_mx_edi.prod_code_sat_01010101') # noqa
        self.donation.taxes_id.unlink()

        invoice = self.create_invoice()
        invoice.sudo().partner_id.ref = 'A&C8317286A1-18000101-020'
        invoice.name = 'PE-53-78436'
        self.create_donation_line(invoice, self.donation)
        invoice.message_ids.unlink()
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml_str = base64.b64decode(
            invoice.message_ids[-2].attachment_ids.datas)
        xml = objectify.fromstring(xml_str)
        xml_expected = objectify.fromstring(
            '<pagoenespecie:PagoEnEspecie '
            'xmlns:pagoenespecie="http://www.sat.gob.mx/pagoenespecie" '
            'Version="1.0" CvePIC="A&amp;C8317286A1-18000101-020" '
            'FolioSolDon="PE-53-78436" PzaArtNombre="Painting" '
            'PzaArtTecn="oil painting" PzaArtAProd="2000" '
            'PzaArtDim="2m height and 2m width"/>')
        namespaces = {
            'pagoenespecie': 'http://www.sat.gob.mx/pagoenespecie'}
        comp = xml.Complemento.xpath('//pagoenespecie:PagoEnEspecie',
                                     namespaces=namespaces)
        self.assertEqualXML(comp[0], xml_expected)

    def create_donation_line(self, invoice, product):
        invoice_line = self.invoice_line_model.new({
            'product_id': product.id,
            'invoice_id': invoice,
            'quantity': 1,
        })
        invoice_line._onchange_product_id()
        invoice_line_dict = invoice_line._convert_to_write({
            name: invoice_line[name] for name in invoice_line._cache
        })
        invoice_line_dict['price_unit'] = product.lst_price
        self.invoice_line_model.create(invoice_line_dict)
