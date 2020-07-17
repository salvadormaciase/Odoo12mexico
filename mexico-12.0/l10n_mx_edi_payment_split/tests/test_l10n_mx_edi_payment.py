from datetime import timedelta
import base64
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tests import Form


class TestAccountPayment(InvoiceTransactionCase):
    def setUp(self):
        super(TestAccountPayment, self).setUp()
        self.register_payments_model = self.env['account.register.payments']
        self.payment_model = self.env['account.payment']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.partner_agrolait = self.env.ref("base.res_partner_address_4")
        self.partner_deco = self.env.ref("base.res_partner_2")
        self.currency_usd = self.env.ref("base.USD")
        self.currency_mxn = self.env.ref("base.MXN")
        self.today = self.env['l10n_mx_edi.certificate'].get_mx_current_datetime().date()
        company = self.env.ref('base.main_company')
        self.main_company_id = company.id
        self.env['res.currency.rate'].create({
            'name': self.today,
            'rate': 1.0/19.6829,
            'currency_id': self.currency_usd.id,
            'company_id': self.main_company_id
        })
        account_obj = self.env['account.account']
        journal_obj = self.env['account.journal']
        self.env.user.company_id.country_id = False
        self.cr.execute(
            """
            UPDATE
                res_company
            SET
                currency_id = %s
            WHERE
                id = %s
            """, [self.currency_mxn.id, company.id])

        self.product = self.env.ref("product.product_product_4")
        self.payment_method_manual_in = self.env.ref("account.account_payment_method_manual_in")
        self.account_receivable = account_obj.search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id)], limit=1)
        self.account_revenue = account_obj.search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)], limit=1)
        self.bank_journal_mxn = journal_obj.create({
            'name': 'Bank',
            'type': 'bank',
            'code': 'BNK67',
        })
        self.bank_journal_usd = journal_obj.create({
            'name': 'Bank US',
            'type': 'bank',
            'code': 'BNK68',
            'currency_id': self.currency_usd.id,
        })
        self.diff_expense_account = self.env.user.company_id.expense_currency_exchange_account_id

    def create_invoice(
            self, amount=100, inv_type='out_invoice', currency_id=None, partner=None, account_id=None, date=None):
        """ Returns an open invoice  """
        invoice = self.invoice_model.create({
            'partner_id': partner or self.partner_agrolait.id,
            'currency_id': currency_id or self.currency_mxn.id,
            'name': inv_type,
            'account_id': account_id or self.account_receivable.id,
            'type': inv_type,
            'date_invoice': date or self.today,
        })
        self.invoice_line_model.create({
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': self.account_revenue.id,
        })
        invoice.action_invoice_open()
        return invoice

    def create_payment(self, invoices, payment_type, currency, journal, amount=False, date=False, csv=False):
        """Creating payment using wizard"""
        ctx = {'active_model': 'account.invoice', 'active_ids': invoices.ids}
        date = date or (self.today + timedelta(days=1))
        register = Form(self.register_payments_model.with_context(ctx))
        register.payment_date = date
        register.currency_id = currency
        register.journal_id = journal
        register.payment_method_id = self.payment_method_manual_in
        if amount:
            register.amount = amount
        if csv:
            register.csv_file = csv
        payment = register.save()
        return payment

    def check_payments(self, invoices, amount, n_aml, inv_state='paid'):
        payment = self.payment_model.search(
            [('invoice_ids', 'in', invoices.ids)], order="id desc", limit=1)
        state = list(set(invoices.mapped('state')))
        self.assertAlmostEquals(payment.amount, amount)
        self.assertEqual(payment.state, 'posted')
        self.assertEqual(len(state), 1)
        self.assertEqual(state[0], inv_state)
        self.assertEqual(len(payment.move_line_ids), n_aml)

    def test_full_payment_process_01(self):
        """Paying fully invoices with same currency MXN and USD"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        currencies = (self.currency_mxn + self.currency_usd)
        journals = {self.currency_mxn.id: self.bank_journal_mxn, self.currency_usd.id: self.bank_journal_usd}
        for invo_type in ('in_invoice', 'out_invoice'):
            for currency in currencies:
                inv_1 = self.create_invoice(
                    inv_type=invo_type, amount=100, currency_id=currency.id, partner=self.partner_agrolait.id)
                inv_2 = self.create_invoice(
                    inv_type=invo_type, amount=200, currency_id=currency.id, partner=self.partner_agrolait.id)
                invoices = (inv_1 + inv_2)
                payment = self.create_payment(
                    invoices, payment_type[invo_type], currency, journals[currency.id])
                payment.create_payments()
                self.check_payments(invoices, 300, 3)

    def test_full_payment_process_multi_currencies_usd_01(self):
        """Paying fully invoices with different currencies with a USD payment"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_usd, self.bank_journal_usd)

            payment.create_payments()

            self.check_payments(invoices, payment.amount, 3)

    def test_full_payment_process_multi_currencies_mxn_01(self):
        """Paying fully invoices with different currencies with a MXN payment"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn)

            payment.create_payments()

            self.check_payments(invoices, payment.amount, 3)

    def test_partial_payment_multi_currencies(self):
        """Partial payment on multi invoices with different currencies with a MXN payment"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn, 300)
            for inv in payment.payment_invoice_ids:
                if inv.invoice_id.currency_id == self.currency_usd:
                    inv.payment_currency_amount = 200
                else:
                    inv.payment_currency_amount = 100
            payment._onchange_payment_invoice()
            payment.create_payments()
            self.check_payments(invoices, 300, 3, 'open')

    def test_change_payment_partner(self):
        """Use different partner on wizard"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type, amount=100, currency_id=self.currency_mxn.id, partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type, amount=200, currency_id=self.currency_mxn.id, partner=self.partner_agrolait.id)
            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn)
            payment.partner_id = self.partner_deco
            payment.create_payments()
            self.check_payments(invoices, 300, 3)
            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc", limit=1)
            self.assertEqual(payment.partner_id, self.partner_deco, "Wrong payment partner")

    def test_use_csv_to_change_invoices_info(self):
        """Create a payment getting invoice info"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type, amount=300, currency_id=self.currency_mxn.id, partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type, amount=200, currency_id=self.currency_mxn.id, partner=self.partner_agrolait.id)
            inv_3 = self.create_invoice(
                inv_type=invo_type, amount=200, currency_id=self.currency_mxn.id, partner=self.partner_agrolait.id)
            # Create csv with invoice numbers
            csv_data = 'Invoice,Amount\r\n%s,50\r\n%s,50\r\n' % (inv_2.number, inv_3.number)
            csv_data = bytes(csv_data, 'utf-8')
            csv_data = base64.b64encode(csv_data)
            self.manager_billing.write({
                'groups_id': [(4, self.ref('l10n_mx_edi_payment_split.payment_split_allow_csv_info_import'))]})
            payment = self.create_payment(
                inv_1, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn, csv=csv_data)
            payment.create_payments()
            self.assertEqual(payment.amount, 100, "Wrong payment amount")
            self.assertEqual((inv_2 + inv_3), payment.invoice_ids, "Wrong invoices")
            self.assertEqual(inv_2.residual, 150, "Wrong invoice residual")
            self.assertEqual(inv_3.residual, 150, "Wrong invoice residual")
            self.assertEqual(inv_1.residual, inv_1.amount_total, "Wrong invoice residual")
