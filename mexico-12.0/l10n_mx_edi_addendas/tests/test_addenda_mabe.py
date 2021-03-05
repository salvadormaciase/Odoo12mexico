# See LICENSE file for full copyright and licensing details.

import os

from lxml.objectify import fromstring
from odoo import fields
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tools import misc


class MxEdiAddendaMabe(InvoiceTransactionCase):
    def setUp(self):
        super(MxEdiAddendaMabe, self).setUp()
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id, })
        conf = self.env['res.config.settings'].create({
            'l10n_mx_addenda': 'mabe'})
        conf.install_addenda()
        self.partner_agrolait.l10n_mx_edi_addenda = self.env.ref(
            'l10n_mx_edi_addendas.mabe')
        self.partner_agrolait.ref = '0107|0107'
        mabe_expected = misc.file_open(os.path.join(
            'l10n_mx_edi_addendas', 'tests', 'mabe_expected.xml')
        ).read().encode('UTF-8')
        self.addenda_tree = fromstring(mabe_expected)
        self.set_currency_rates(mxn_rate=21, usd_rate=1)

    def test_001_addenda_in_xml(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        invoice = self.create_invoice()
        self.partner_agrolait.type = 'delivery'
        invoice.name = 'PO002'
        # wizard values
        invoice.sudo().partner_id.lang = 'en_US'
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertTrue(hasattr(xml, 'Addenda'), "There is not Addenda node")
        self.addenda_tree.getchildren()[0].attrib[
            'fecha'] = fields.Date.to_string(invoice.date_invoice)
        self.addenda_tree.getchildren()[0].attrib['folio'] = xml.get(
            'Serie') + xml.get('Folio')
        self.addenda_tree.getchildren()[0].attrib['referencia1'] = xml.get(
            'Serie') + xml.get('Folio')
        self.assertEqualXML(xml.Addenda, self.addenda_tree)
