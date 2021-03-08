# See LICENSE file for full copyright and licensing details.

import os

from lxml.objectify import fromstring

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class MxEdiAddendaAmazon(InvoiceTransactionCase):
    def test_001_addenda_in_xml(self):
        language = self.env['base.language.install'].create(
            {'lang': 'es_ES', 'overwrite': 0})
        language.lang_install()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'amazon'})
        conf.install_addenda()
        self.partner_agrolait.write({
            'l10n_mx_edi_addenda': self.ref('l10n_mx_edi_addendas.amazon'),
        })
        addenda_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'amazon_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(addenda_expected)
        addenda_expected_refund = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'amazon_expected_refund.xml')
        ).read().encode('UTF-8')
        self.addenda_tree_refund = fromstring(addenda_expected_refund)

        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        invoice.currency_id = self.mxn.id
        invoice.move_name = 'INV/2019/999'
        invoice.invoice_line_ids.write({
            'name': '[PCSC234] Computer SC234 17',
        })
        invoice.comment = "Free Text"
        invoice.name = 'ABC123'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        self.assertEqualXML(xml.Addenda, self.addenda_tree)

        # testing refund with Attribute QPD
        refund = self.env['account.invoice.refund'].with_context(
            active_ids=invoice.ids).create({
                'filter_refund': 'refund',
                'description': 'QPD|ABC123',
                'date': invoice.date_invoice,
            })
        result = refund.invoice_refund()
        refund_id = result.get('domain')[1][2]
        refund = self.env['account.invoice'].browse(refund_id)
        refund.action_invoice_open()
        refund.refresh()
        self.assertEqual(refund.state, "open")
        self.assertEqual(refund.l10n_mx_edi_pac_status, "signed",
                         refund.message_ids.mapped('body'))
        xml = refund.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        self.assertEqualXML(xml.Addenda, self.addenda_tree_refund)
