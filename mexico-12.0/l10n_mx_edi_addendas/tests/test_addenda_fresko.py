# See LICENSE file for full copyright and licensing details.

import os

from lxml.objectify import fromstring

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class MxEdiAddendaFresko(InvoiceTransactionCase):
    def test_001_addenda_in_xml(self):
        language = self.env['base.language.install'].create(
            {'lang': 'es_ES', 'overwrite': 0})
        language.lang_install()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'fresko'})
        conf.install_addenda()
        self.partner_agrolait.write({
            'l10n_mx_edi_addenda': self.ref('l10n_mx_edi_addendas.fresko'),
            'ref': '7505000099632',
        })
        addenda_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'fresko_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(addenda_expected)

        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        invoice.currency_id = self.mxn.id
        invoice.move_name = 'INV/2019/999'
        invoice.invoice_line_ids.write({
            'name': '[PCSC234] Computer SC234 17',
            'x_addenda_supplier_code': '1234567890',
        })
        invoice.x_addenda_fresko = "DQ|2019-01-24|123456|\
            123|10"
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        date = xml.Addenda.xpath('//requestForPayment')[0].get('DeliveryDate')
        self.addenda_tree.xpath('//requestForPayment')[0].attrib[
            'DeliveryDate'] = date
        self.assertEqualXML(xml.Addenda, self.addenda_tree)
