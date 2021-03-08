# Copyright 2019 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.tests.common import TransactionCase


class TestSaleCoupon(TransactionCase):

    def setUp(self):
        super().setUp()
        self.sale_id = self.env.ref('sale.sale_order_1').copy()
        self.sale_id.order_line.mapped('product_id').write({'invoice_policy': 'order'})
        self.coupon_program = self.env['sale.coupon.program']
        self.generate_coupon = self.env['sale.coupon.generate']
        self.apply_coupon = self.env['sale.coupon.apply.code']

    def test_coupon_on_order(self):
        sale = self.sale_id
        program = self.coupon_program.create({
            'name': 'Buena Onda',
            'discount_type': 'percentage',
            'discount_percentage': 10.0,
        })

        self.generate_coupon.with_context(active_id=program.id).create({'nbr_coupons': 1}).generate_coupon()
        coupon = program.coupon_ids
        self.apply_coupon.create({'coupon_code': coupon.code}).with_context(active_id=sale.id).process_coupon()

        sale.action_confirm()
        sale.action_invoice_create()
        self.assertEquals(sale.invoice_status, 'invoiced', 'The lines in the sale are not invoiced')

        total_sale = round(sale.amount_total, 0)
        total_inv = round(sale.order_line.mapped('invoice_lines.invoice_id').amount_total, 0)
        self.assertTrue(float_is_zero(float_compare(total_inv, total_sale, 2), 2),
                        'The invoice total is different to the sale order. %s != %s' % (total_inv, total_sale))

        reward_line = sale.invoice_ids.invoice_line_ids.filtered(lambda l: not l.price_total)
        invoice_lines = sale.invoice_ids.invoice_line_ids - reward_line
        self.assertTrue(reward_line, 'The reward line amount must be 0')
        # Remove the reward line and check that all lines have amount_discount
        self.assertTrue(all(invoice_lines.mapped('l10n_mx_edi_amount_discount')),
                        'All normal invoice lines must have discount')

    def test_coupon_on_order_tax_included(self):
        program = self.coupon_program.create({
            'name': 'Buena Onda',
            'discount_type': 'percentage',
            'discount_percentage': 10.0,
        })
        self.generate_coupon.with_context(active_id=program.id).create({'nbr_coupons': 1}).generate_coupon()
        coupon = program.coupon_ids
        sale = self.sale_id
        tax16 = self.env['account.tax'].create({
            'name': 'IVA(16%) VENTAS INC',
            'description': 'IVA(16%)',
            'amount': 16,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'price_include': True,
        })
        program.discount_line_product_id.taxes_id = [(6, 0, tax16.ids)]
        for line in sale.order_line:
            line.tax_id = [(6, 0, tax16.ids)]

        self.apply_coupon.create({'coupon_code': coupon.code}).with_context(active_id=sale.id).process_coupon()
        sale.order_line.filtered('is_reward_line').tax_id = False
        sale.action_confirm()
        sale.action_invoice_create()
        self.assertEquals(sale.invoice_status, 'invoiced', 'The lines in the sale are not invoiced')

        total_sale = round(sale.amount_total, 0)
        total_inv = round(sale.order_line.mapped('invoice_lines.invoice_id').amount_total, 0)
        self.assertTrue(float_is_zero(float_compare(total_inv, total_sale, 2), 2),
                        'The invoice total is different to the sale order. %s != %s' % (total_inv, total_sale))

        reward_line = sale.invoice_ids.invoice_line_ids.filtered(lambda l: not l.price_total)
        invoice_lines = sale.invoice_ids.invoice_line_ids - reward_line
        self.assertTrue(reward_line, 'The reward line amount must be 0')
        # Remove the reward line and check that all lines have amount_discount
        self.assertTrue(all(invoice_lines.mapped('l10n_mx_edi_amount_discount')),
                        'All normal invoice lines must have discount')

    def test_promotion_on_order(self):
        """Test an Immediate Promo Program"""
        sale = self.sale_id
        self.coupon_program.create({
            'name': 'Buena Onda',
            'discount_type': 'percentage',
            'discount_percentage': 10.0,
            'discount_apply_on': 'on_order',
            'rule_minimum_amount': 1000,
            'promo_code_usage': 'no_code_needed',
            'program_type': 'promotion_program',
        })
        sale.recompute_coupon_lines()
        sale.action_confirm()
        sale.action_invoice_create()

        self.assertEquals(sale.invoice_status, 'invoiced', 'The lines in the sale are not invoiced')

        total_sale = round(sale.amount_total, 0)
        total_inv = round(sale.order_line.mapped('invoice_lines.invoice_id').amount_total, 0)
        self.assertTrue(float_is_zero(float_compare(total_inv, total_sale, 2), 2),
                        'The invoice total is different to the sale order. %s != %s' % (total_inv, total_sale))

        reward_line = sale.invoice_ids.invoice_line_ids.filtered(lambda l: not l.price_total)
        invoice_lines = sale.invoice_ids.invoice_line_ids - reward_line
        self.assertTrue(reward_line, 'The reward line amount must be 0')
        # Remove the reward line and check that all lines have amount_discount
        self.assertTrue(all(invoice_lines.mapped('l10n_mx_edi_amount_discount')),
                        'All normal invoice lines must have discount')
