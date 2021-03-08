# See LICENSE file for full copyright and licensing details.

import os

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo import tools


class AddendasTransactionCase(InvoiceTransactionCase):

    def setUp(self):
        super(AddendasTransactionCase, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.set_currency_rates(mxn_rate=20.0, usd_rate=1.0)

    def get_expected_addenda(self, addenda_name):
        """Given an addenda name, returns the expected node"""
        xml_path = os.path.join(
            'l10n_mx_edi_addendas', 'tests', '%s_expected.xml' % addenda_name)
        with tools.file_open(xml_path, 'rb') as xml_file:
            addenda = xml_file.read()
        addenda_tree = objectify.fromstring(addenda)
        return addenda_tree

    def install_addenda(self, addenda_name):
        config = self.env['res.config.settings'].create({
            'l10n_mx_addenda': addenda_name,
        })
        config.install_addenda()
        addenda = self.env.ref('l10n_mx_edi_addendas.%s' % addenda_name)
        self.partner_agrolait.l10n_mx_edi_addenda = addenda

    def set_wizard_values(self, invoice, addenda_name, values):
        wizard = self.env['x_addenda.%s' % addenda_name].create(values)
        set_addenda_action = self.env.ref(
            'l10n_mx_edi_addendas.set_addenda_%s_values' % addenda_name)
        context = {
            'active_id': wizard.id,
            'invoice_id': invoice.id,
        }
        set_addenda_action.with_context(context).run()
