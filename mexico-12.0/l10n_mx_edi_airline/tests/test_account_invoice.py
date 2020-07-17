# coding: utf-8

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceAirline(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiInvoiceAirline, self).setUp()
        self.tua = self.env['product.product'].create({
            'name': 'TUA',
            'default_code': 'tua',
            'lst_price': '135.00',
            'l10n_mx_edi_airline_type': 'tua',
        })
        self.tua.l10n_mx_edi_code_sat_id = self.ref('l10n_mx_edi.prod_code_sat_01010101') # noqa

    def test_invoice_airline_no_extra_charges(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        invoice = self.create_invoice()
        self.tua.taxes_id.unlink()
        self.create_airline_line(invoice, self.tua)
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'aerolineas': 'http://www.sat.gob.mx/aerolineas'}
        comp = xml.Complemento.xpath('//aerolineas:Aerolineas',
                                     namespaces=namespaces)
        self.assertTrue(comp, 'Complement to Airlines not added correctly')

    def test_invoice_airline_extra_charges(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        extra_charge1 = self.env['product.product'].create({
            'name': 'Charge DW',
            'default_code': 'DW',
            'lst_price': '220.00',
            'l10n_mx_edi_airline_type': 'extra',
        })
        extra_charge1.l10n_mx_edi_code_sat_id = self.ref('l10n_mx_edi.prod_code_sat_01010101') # noqa
        extra_charge1.taxes_id.unlink()
        extra_charge2 = self.env['product.product'].create({
            'name': 'Charge BA',
            'default_code': 'BA',
            'lst_price': '125.00',
            'l10n_mx_edi_airline_type': 'extra',
        })
        extra_charge2.l10n_mx_edi_code_sat_id = self.ref('l10n_mx_edi.prod_code_sat_01010101') # noqa
        extra_charge2.taxes_id.unlink()
        invoice = self.create_invoice()
        self.create_airline_line(invoice, self.tua)
        self.create_airline_line(invoice, extra_charge1)
        self.create_airline_line(invoice, extra_charge2)
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'aerolineas': 'http://www.sat.gob.mx/aerolineas'}
        comp = xml.Complemento.xpath('//aerolineas:OtrosCargos',
                                     namespaces=namespaces)
        self.assertTrue(comp, 'Complement to Airlines not added correctly')

    def create_airline_line(self, invoice, product):
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
