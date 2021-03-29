# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class PointOfSale(TransactionCase):

    def setUp(self):
        super(PointOfSale, self).setUp()
        self.pos_order_obj = self.env['pos.order']
        self.pmp_obj = self.env['pos.make.payment']

        self.config = self.env.ref('point_of_sale.pos_config_main')
        self.partner = self.env.ref('base.res_partner_address_2')
        self.category = self.env.ref('product.product_category_5')
        self.product = self.env.ref('product.product_product_9')
        self.config.available_pricelist_ids.currency_id = self.config.currency_id  # noqa
        self.session = self.env['pos.session'].create({
            'user_id': self.uid,
            'config_id': self.config.id
        })
        # Allowing Cancel Entries
        self.config.journal_id.update_posted = True
        # Set product category
        account_input = self.env['account.account'].search(
            [('code', '=', '205.06.01')], limit=1)
        account_output = self.env['account.account'].search(
            [('code', '=', '107.05.01')], limit=1)
        account_valuation = self.env['account.account'].search(
            [('code', '=', '115.01.01')], limit=1)
        self.category.property_valuation = 'real_time'
        self.category.property_stock_account_input_categ_id = account_input
        self.category.property_stock_account_output_categ_id = account_output
        self.category.property_stock_valuation_account_id = account_valuation
        # Set product
        self.product.categ_id = self.category
        self.product.standard_price = 55
        self.product.available_in_pos = True
        self.product.type = 'product'

    def create_order(self, partner=False, qty=5):
        """Create the orders needed for each use case"""
        # Creating Order
        order = self.pos_order_obj.create({
            'partner_id': partner or False,
            'session_id': self.session.id,
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': 100.0,
                'qty': qty,
                'price_subtotal': 100.0 * qty,
                'price_subtotal_incl': 100.0 * qty,
            })],
            'amount_total': 100.0 * qty,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })
        # Creating payment
        payment = self.pmp_obj.with_context(active_id=order.id).create({
            'journal_id': order.session_id.config_id.journal_ids.ids[0],
            'amount': order.amount_total
        })
        payment.check()
        return order

    def _check_cogs(self, ret=False):
        """Validate that all cogs were generated correctly with the order
        information"""
        # Getting the account to validate the corrects values for
        # debit and credit

        sacc = (
            self.product[ret and 'property_stock_account_input' or
                         'property_stock_account_output'].id or
            self.product.categ_id[
                ret and 'property_stock_account_input_categ_id' or
                'property_stock_account_output_categ_id'].id)
        eacc = (self.product.property_account_expense_id.id or
                self.product.categ_id.
                property_account_expense_categ_id.id)

        accounts = {
            sacc: ret and 'debit' or 'credit',
            eacc: ret and 'credit' or 'debit'
        }

        journal_entry = self.env['account.move'].search(
            [('ref', '=', self.session.name)])

        # Validate that jornal entry was created
        self.assertTrue(journal_entry,
                        'The Cost Journal Entry was not created')

        lines = journal_entry.line_ids.filtered(
            lambda a: a.account_id.id in (sacc, eacc) and a.product_id)
        values_in_line = [i.debit or i.credit for i in lines]

        # Validating the values of credit and debit
        self.assertTrue(values_in_line.count(275) == 2,
                        'The values for debit and credit must be 275, '
                        'because the current cost for the product is 55')

        # Checking that the credit and debit are correctly set
        for line in lines:
            self.assertEqual(275,
                             line[accounts.get(line.account_id.id)],
                             'The values of the credit and debit are not '
                             'correctly set in the Journal Entry for '
                             'the return')

    def test_01_close_session(self):
        """Close the current session and validate that the Journal Entry are
        correctly posted"""
        # Create an order with partner
        self.create_order(qty=3)
        self.create_order(qty=2)
        # Validating the Cost Journal Entry
        self.session.action_pos_session_closing_control()
        self._check_cogs()
