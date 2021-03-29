import os

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class TestL10nMxEdiInvoiceFuel(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiInvoiceFuel, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.partner_chinaexport = self.env.ref("base.res_partner_address_11")
        self.env.ref('l10n_mx.1_tax12').l10n_mx_cfdi_tax_type = 'Tasa'
        self.fuel_product = self.env.ref(
            'l10n_mx_edi_fuel.res_product_fuel_diesel')
        self.fuel_product.write({
            'l10n_mx_edi_code_sat_id': self.ref(
                'l10n_mx_edi.prod_code_sat_15101505'),
            'taxes_id': [(6, 0, [self.ref('l10n_mx.1_tax12')])],
        })
        self.service_station = self.env['res.partner'].create({
            'name': 'MX Service Station',
            'ref': '1234',
        })
        service_station_bank = self.env['res.partner.bank'].create({
            'bank_id': self.ref('base.res_bank_1'),
            'acc_number': '0987654321',
            'partner_id': self.service_station.id,
        })
        self.service_station.bank_ids = [service_station_bank.id]
        self.service_station.category_id = [self.ref(
            'l10n_mx_edi_fuel.res_partner_category_service_station')]
        self.xml_expected_ecc = misc.file_open(os.path.join(
            'l10n_mx_edi_fuel', 'tests', 'expected_ecc.xml')).read(
            ).encode('UTF-8')
        self.xml_expected_cc = misc.file_open(os.path.join(
            'l10n_mx_edi_fuel', 'tests', 'expected_cc.xml')).read(
            ).encode('UTF-8')
        self.xml_expected_only_cc = misc.file_open(os.path.join(
            'l10n_mx_edi_fuel', 'tests', 'expected_only_cc.xml')).read(
            ).encode('UTF-8')
        self.xml_expected_ecc_discount = misc.file_open(os.path.join(
            'l10n_mx_edi_fuel', 'tests', 'expected_ecc_discount.xml')).read(
            ).encode('UTF-8')

    def create_fuel_invoice(self, service_station=None, inv_type='out_invoice', currency_id=None): # noqa
        if currency_id is None:
            currency_id = self.usd.id
        invoice = self.invoice_model.create({
            'partner_id': self.partner_agrolait.id,
            'type': inv_type,
            'currency_id': currency_id,
            'l10n_mx_edi_payment_method_id': self.payment_method_cash.id,
            'l10n_mx_edi_partner_bank_id': self.account_payment.id,
            'l10n_mx_edi_usage': 'P01',
        })
        self.create_fuel_invoice_line(invoice, service_station)
        invoice.compute_taxes()
        return invoice

    def create_fuel_invoice_line(self, invoice_id, service_station):
        invoice_line = self.invoice_line_model.new({
            'product_id': self.fuel_product.id,
            'invoice_id': invoice_id,
            'quantity': 1,
            'l10n_mx_edi_fuel_partner_id': service_station.id if service_station else None # noqa
        })
        invoice_line._onchange_product_id()
        invoice_line_dict = invoice_line._convert_to_write({
            name: invoice_line[name] for name in invoice_line._cache})
        invoice_line_dict['price_unit'] = self.fuel_product.lst_price
        self.invoice_line_model.create(invoice_line_dict)

    def test_l10n_mx_edi_ecc_invoice(self):
        self.company.write({'l10n_mx_edi_isepi': True, })
        self.partner_chinaexport.parent_id.write(
            {'ref': '0000123',
             'vat': 'XEXX010101000',
             'country_id': self.env.ref('base.mx').id, })
        self.partner_agrolait.parent_id.write(
            {'vat': 'EKU9003173C9',
             'country_id': self.env.ref('base.mx').id})

        invoice = self.create_fuel_invoice(self.service_station)
        invoice.move_name = 'INV/2018/999'
        invoice.partner_id = self.partner_chinaexport.parent_id
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'ecc12': 'http://www.sat.gob.mx/EstadoDeCuentaCombustible12'}
        ecc12 = xml.Complemento.xpath('//ecc12:EstadoDeCuentaCombustible',
                                      namespaces=namespaces)
        self.assertTrue(ecc12, 'Complement to ECC12 not added correctly')
        xml_expected = objectify.fromstring(self.xml_expected_ecc)
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        xml_expected.attrib['TipoCambio'] = xml.attrib['TipoCambio']
        self.assertEqualXML(xml, xml_expected)

        # Generating a refund to test consumodecombustible complement
        # when company is only an emitter
        refund = invoice.refund()
        refund.date_invoice = invoice.date_invoice
        refund.name = '0000123'
        refund.partner_bank_id.unlink()
        refund.partner_id = self.service_station
        refund.l10n_mx_edi_partner_bank_id = self.service_station.bank_ids.id
        refund.l10n_mx_edi_payment_method_id = invoice.l10n_mx_edi_payment_method_id.id # noqa
        refund.l10n_mx_edi_usage = 'P01'
        refund.action_invoice_open()
        self.assertEqual(refund.l10n_mx_edi_pac_status, "signed",
                         refund.message_ids.mapped('body'))
        xml = refund.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'consumodecombustibles11': 'http://www.sat.gob.mx/ConsumoDeCombustibles11'}  # noqa
        cc = xml.Complemento.xpath(
            '//consumodecombustibles11:ConsumoDeCombustibles',
            namespaces=namespaces)
        self.assertTrue(cc, 'Complement to ConsumoDeCombustibles not added '
                        'correctly')
        xml_expected = objectify.fromstring(self.xml_expected_cc)
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        xml_expected.attrib['TipoCambio'] = xml.attrib['TipoCambio']
        xml_expected.CfdiRelacionados.CfdiRelacionado.attrib['UUID'] = xml.CfdiRelacionados.CfdiRelacionado.attrib['UUID'] # noqa
        self.assertEqualXML(xml, xml_expected)

        # Testing with discount
        invoice = self.create_fuel_invoice(self.service_station)
        invoice.invoice_line_ids.write({'discount': 13.00})
        invoice.compute_taxes()
        invoice.move_name = 'INV/2018/1001'
        invoice.partner_id = self.partner_chinaexport.parent_id
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        xml_expected = objectify.fromstring(self.xml_expected_ecc_discount)
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        xml_expected.attrib['TipoCambio'] = xml.attrib['TipoCambio']
        self.assertEqualXML(xml, xml_expected)

    def test_l10n_mx_edi_cc_invoice(self):
        self.company.write({'l10n_mx_edi_isepi': False, })
        self.company.partner_id.ref = '1234'
        self.company.partner_id.category_id = [self.ref(
            'l10n_mx_edi_fuel.res_partner_category_service_station')]
        self.partner_agrolait.parent_id.write(
            {'vat': 'EKU9003173C9',
             'country_id': self.env.ref('base.mx').id})
        invoice = self.create_fuel_invoice()
        invoice.l10n_mx_edi_emitter_reference = "123456|000008955"
        invoice.l10n_mx_edi_origin = "01|B4536414-607E-42CA-AAB4-03EB964002A1"
        invoice.partner_id = self.partner_agrolait.parent_id
        invoice.move_name = 'INV/2018/1000'
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'consumodecombustibles11': 'http://www.sat.gob.mx/ConsumoDeCombustibles11'}  # noqa
        cc = xml.Complemento.xpath(
            '//consumodecombustibles11:ConsumoDeCombustibles',
            namespaces=namespaces)
        self.assertTrue(cc, 'Complement to ConsumoDeCombustibles not added '
                        'correctly')
        xml_expected = objectify.fromstring(self.xml_expected_only_cc)
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        xml_expected.attrib['TipoCambio'] = xml.attrib['TipoCambio']
        xml_expected.CfdiRelacionados.CfdiRelacionado.attrib['UUID'] = xml.CfdiRelacionados.CfdiRelacionado.attrib['UUID'] # noqa
        self.assertEqualXML(xml, xml_expected)
