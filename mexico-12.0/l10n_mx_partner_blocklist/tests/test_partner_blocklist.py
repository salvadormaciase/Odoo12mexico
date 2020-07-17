# coding: utf-8

from odoo import fields
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.exceptions import ValidationError


class TestL10nMxPartnerBlocklist(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxPartnerBlocklist, self).setUp()
        self.partner_camptocamp = self.env.ref('base.res_partner_12')
        self.partner_camptocamp.write({
            'customer': True,
            'supplier': True,
            'vat': 'XAXX010101000',
        })
        self.server_action = self.env.ref(
            'l10n_mx_partner_blocklist.partner_blocklist_status_server_action')
        self.manager_billing.write({
            'groups_id': [(6, 0, [
                self.ref('sales_team.group_sale_manager'),
                self.ref('purchase.group_purchase_manager'),
                self.ref('l10n_mx_partner_blocklist.group_partner_blacklist'),
            ])]
        })

    def test_partner_blocklist(self):
        # Checking partner status messages
        self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist,
                         'normal', 'The action was already executed')
        self.server_action.with_context({
            'active_ids': self.partner_camptocamp.id,
            'active_model': 'res.partner'}).run()
        self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist,
                         'done', 'The partner is not OK')
        self.env['res.partner.blacklist'].create({
            'vat': 'XAXX010101000',
            'taxpayer_name': self.partner_camptocamp.name,
        })
        self.server_action.with_context({
            'active_ids': self.partner_camptocamp.id,
            'active_model': 'res.partner'}).run()
        self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist,
                         'blocked', 'The partner is not blocked')

        # Checking the user is not able to sale, purchase or invoicing with
        # a blocked partner.
        raise_msg = 'The SAT provides a block list'
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_camptocamp.id,
            'picking_policy': 'direct',
            'date_order': fields.datetime.today(),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.name,
                'product_uom_qty': 1.00,
                'price_unit': 100.00,
            })]
        })
        try:
            sale_order.action_confirm()
            self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist,
                             'blocked', "The Sale Order has been confirmed")
        except ValidationError as e:
            self.assertEqual(raise_msg, e.name[:29])

        purchase = self.env['purchase.order'].create({
            'partner_id': self.partner_camptocamp.id,
            'date_order': fields.datetime.today(),
            'date_planned': fields.datetime.today(),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.name,
                'date_planned': fields.datetime.today(),
                'product_qty': 1.00,
                'price_unit': 100.00,
                'product_uom': self.ref('uom.product_uom_unit'),
            })]
        })
        try:
            purchase.button_confirm()
            self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist,
                             'blocked', "The Purchase Order has been "
                             "confirmed")
        except ValidationError as e:
            self.assertEqual(raise_msg, e.name[:29])

        invoice = self.create_invoice()
        try:
            invoice.action_invoice_open()
            self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist,
                             'blocked', "The Invoice has been validated")
        except ValidationError as e:
            self.assertEqual(raise_msg, e.name[:29])
