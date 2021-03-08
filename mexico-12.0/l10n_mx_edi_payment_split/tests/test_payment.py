from datetime import timedelta
from odoo.tests import Form
from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.tests import tagged

MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


@tagged('post_install', '-at_install')
class TestPayment(AccountingTestCase):

    def setUp(self):
        super(TestPayment, self).setUp()
        self.register_payments_model = self.env[
            'account.register.payments'].with_context(
                active_model='account.invoice')
        self.payment_model = self.env['account.payment']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']

        self.partner_agrolait = self.env.ref("base.res_partner_address_4")
        self.currency_usd = self.env.ref("base.USD")
        self.currency_mxn = self.env.ref("base.MXN")
        self.today = self.env[
            'l10n_mx_edi.certificate'].get_mx_current_datetime().date()
        company = self.env.ref('base.main_company')
        self.main_company_id = company.id
        self.currency_usd.rate_ids.unlink()
        self.env['res.currency.rate'].create({
            'name': '2019-09-28',
            'rate': 1.0/19.6363,
            'currency_id': self.currency_usd.id,
            'company_id': self.main_company_id
        })
        self.env['res.currency.rate'].create({
            'name': '2019-10-15',
            'rate': 1.0/19.3217,
            'currency_id': self.currency_usd.id,
            'company_id': self.main_company_id
        })
        self.env['res.currency.rate'].create({
            'name': '2019-10-22',
            'rate': 1.0/19.1492,
            'currency_id': self.currency_usd.id,
            'company_id': self.main_company_id
        })
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
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in")

        self.account_receivable = account_obj.search(
            [('user_type_id', '=',
              self.env.ref('account.data_account_type_receivable').id)],
            limit=1)
        self.account_revenue = account_obj.search(
            [('user_type_id', '=',
              self.env.ref('account.data_account_type_revenue').id)], limit=1)

        self.bank_journal_mxn = journal_obj.create(
            {'name': 'Bank',
             'type': 'bank',
             'code': 'BNK67'})

        self.bank_journal_usd = journal_obj.create(
            {'name': 'Bank US',
             'type': 'bank',
             'code': 'BNK68',
             'currency_id': self.currency_usd.id})

        self.diff_expense_account = (self.env.user.company_id.
                                     expense_currency_exchange_account_id)

    def create_invoice(self, amount=100, inv_type='out_invoice',
                       currency_id=None, partner=None, account_id=None,
                       date=None):
        """ Returns an open invoice """
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

    def create_payment(self, invoices, payment_type, currency, journal, amount=False, date=False):
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
        payment = register.save()
        return payment

    def check_payments(self, invoices, amount, n_aml):

        payment = self.payment_model.search(
            [('invoice_ids', 'in', invoices.ids)], order="id desc",
            limit=1)

        state = list(set(invoices.mapped('state')))
        self.assertAlmostEquals(payment.amount, amount)
        self.assertEqual(payment.state, 'posted')
        self.assertEqual(len(state), 1)
        self.assertEqual(state[0], 'paid')
        self.assertEqual(len(payment.move_line_ids), n_aml)

    def test_full_payment_process_01(self):
        """Paying fully invoices with same currency MXN and USD"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            currencies = (self.currency_mxn + self.currency_usd)
            for currency in currencies:
                inv_1 = self.create_invoice(
                    inv_type=invo_type,
                    amount=100, currency_id=currency.id,
                    partner=self.partner_agrolait.id)
                inv_2 = self.create_invoice(
                    inv_type=invo_type,
                    amount=200, currency_id=currency.id,
                    partner=self.partner_agrolait.id)

                invoices = (inv_1 + inv_2)
                payment = self.create_payment(
                    invoices, payment_type[invo_type], currency, self.bank_journal_mxn)
                payment.create_payments()

                self.check_payments(invoices, 300, 3)

    def test_payment_wizard_usd_currency_payment(self):
        """Checking the computation of payment in USD for Multi-currency
        Invoices"""
        pay_amount = 11342.41
        currency = self.currency_usd

        inv_1 = self.create_invoice(
            inv_type='out_invoice',
            amount=33783.84, currency_id=self.currency_mxn.id,
            partner=self.partner_agrolait.id,
            date='2019-09-28')
        inv_2 = self.create_invoice(
            inv_type='out_invoice',
            amount=9578.17, currency_id=self.currency_usd.id,
            partner=self.partner_agrolait.id,
            date='2019-10-15')

        invoices = (inv_1 + inv_2)
        payment = self.create_payment(
            invoices, 'inbound', currency, self.bank_journal_mxn, pay_amount, date='2019-10-22')

        pay_line_inv_1 = payment.payment_invoice_ids.filtered(
            lambda x: x.invoice_id == inv_1)
        pay_line_inv_2 = payment.payment_invoice_ids.filtered(
            lambda x: x.invoice_id == inv_2)
        self.assertAlmostEquals(
            pay_line_inv_1.payment_amount, 33782.28, 2,
            'Invoice in MXN Paid in USD got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_1.payment_currency_amount, 94.51, 2,
            'Invoice in MXN Paid in USD got a wrong value in Payment Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_amount, 9578.17, 2,
            'Invoice in USD Paid in USD got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_currency_amount, 9578.17, 2,
            'Invoice in USD Paid in USD got a wrong value in Payment Currency')

        payment._onchange_currency_at_payment()
        payment.write({'payment_invoice_ids': []})
        self.assertAlmostEquals(
            pay_line_inv_1.payment_amount, 33782.28, 2,
            'Invoice in MXN Paid in USD got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_1.payment_currency_amount, 94.51, 2,
            'Invoice in MXN Paid in USD got a wrong value in Payment Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_amount, 9578.17, 2,
            'Invoice in USD Paid in USD got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_currency_amount, 9578.17, 2,
            'Invoice in USD Paid in USD got a wrong value in Payment Currency')

    def test_payment_wizard_mxn_currency_payment(self):
        """Checking the computation of payment in MXN for Multi-currency
        Invoices"""
        pay_amount = 217198.13
        currency = self.currency_mxn

        inv_1 = self.create_invoice(
            inv_type='out_invoice',
            amount=33783.84, currency_id=self.currency_mxn.id,
            partner=self.partner_agrolait.id,
            date='2019-09-28')
        inv_2 = self.create_invoice(
            inv_type='out_invoice',
            amount=9578.17, currency_id=self.currency_usd.id,
            partner=self.partner_agrolait.id,
            date='2019-10-15')

        invoices = (inv_1 + inv_2)
        payment = self.create_payment(
            invoices, 'inbound', currency, self.bank_journal_mxn, pay_amount, date='2019-10-22')
        pay_line_inv_1 = payment.payment_invoice_ids.filtered(
            lambda x: x.invoice_id == inv_1)
        pay_line_inv_2 = payment.payment_invoice_ids.filtered(
            lambda x: x.invoice_id == inv_2)
        self.assertAlmostEquals(
            pay_line_inv_1.payment_amount, 33783.84, 2,
            'Invoice in MXN Paid in MXN got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_1.payment_currency_amount, 33783.84, 2,
            'Invoice in MXN Paid in MXN got a wrong value in Payment Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_amount, 513.12, 2,
            'Invoice in USD Paid in MXN got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_currency_amount, 183414.29, 2,
            'Invoice in USD Paid in MXN got a wrong value in Payment Currency')

        payment._onchange_currency_at_payment()
        payment.write({'payment_invoice_ids': []})
        self.assertAlmostEquals(
            pay_line_inv_1.payment_amount, 33783.84, 2,
            'Invoice in MXN Paid in MXN got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_1.payment_currency_amount, 33783.84, 2,
            'Invoice in MXN Paid in MXN got a wrong value in Payment Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_amount, 9578.17, 2,
            'Invoice in USD Paid in MXN got a wrong value in Invoice Currency')
        self.assertAlmostEquals(
            pay_line_inv_2.payment_currency_amount, 3423684.56, 2,
            'Invoice in USD Paid in MXN got a wrong value in Payment Currency')

    def test_full_payment_process_multi_currencies_usd_01(self):
        """Paying fully invoices with different currencies with a USD
        payment"""
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
        """Paying fully invoices with different currencies with a MXN
        payment"""
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

            self.check_payments(invoices, 36940.89, 3)

    # ----------------------------- Excess --------------------------------

    def test_full_payment_process_02_handling_open_mxn(self):
        """Paying MXN invoices with MXN payment(Excess) - Handling Open
        payment and using different accounts for same partner"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        new_account = self.account_receivable.copy()
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id, account_id=new_account.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn, 400)

            payment.create_payments()

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            # /!\ NOTE: Fetching the line with the bank value
            aml_id = payment.move_line_ids.filtered(
                lambda x: x.account_id in (
                    payment.journal_id.default_debit_account_id,
                    payment.journal_id.default_credit_account_id))
            self.assertAlmostEquals(abs(aml_id.balance), 400)
            # /!\ NOTE: Fetching the line for inv_1 value
            aml_id = payment.move_line_ids.filtered(
                lambda x: x.account_id == self.account_receivable and
                x.full_reconcile_id)
            self.assertAlmostEquals(abs(aml_id.balance), 100)
            # /!\ NOTE: Fetching the line for inv_2 value
            aml_id = payment.move_line_ids.filtered(
                lambda x: x.account_id == new_account and
                x.full_reconcile_id)
            self.assertAlmostEquals(abs(aml_id.balance), 200)
            # /!\ NOTE: Fetching the line with the excess value
            aml_id = payment.move_line_ids.filtered(
                lambda x: x.account_id not in (
                    payment.journal_id.default_debit_account_id,
                    payment.journal_id.default_credit_account_id) and
                not x.full_reconcile_id)
            self.assertAlmostEquals(abs(aml_id.balance), 100)
            state = list(set(invoices.mapped('state')))
            self.assertAlmostEquals(payment.amount, 400)
            self.assertEqual(payment.state, 'posted')
            self.assertEqual(len(state), 1)
            self.assertEqual(state[0], 'paid')
            self.assertEqual(len(payment.move_line_ids), 4)

    def test_full_payment_process_02_handling_open_usd(self):
        """Paying USD invoices with USD payment(Excess) - Handling Open"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_usd, self.bank_journal_usd, 400)

            payment.create_payments()

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            # /!\ NOTE: Fetching the line with the bank value
            aml_id = payment.move_line_ids.filtered(
                lambda x: x.account_id in (
                    payment.journal_id.default_debit_account_id,
                    payment.journal_id.default_credit_account_id))
            self.assertAlmostEquals(abs(aml_id.amount_currency), 400)
            # /!\ NOTE: Fetching the line with the excess value
            aml_id = payment.move_line_ids.filtered(
                lambda x: x.account_id not in (
                    payment.journal_id.default_debit_account_id,
                    payment.journal_id.default_credit_account_id) and
                not x.full_reconcile_id)
            self.assertAlmostEquals(abs(aml_id.amount_currency), 100)
            state = list(set(invoices.mapped('state')))
            self.assertAlmostEquals(payment.amount, 400)
            self.assertEqual(payment.state, 'posted')
            self.assertEqual(len(state), 1)
            self.assertEqual(state[0], 'paid')
            self.assertEqual(len(payment.move_line_ids), 4)

    def test_full_payment_process_02(self):
        """Paying MXN invoices with MXN payment(Excess)"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn, 400)

            payment.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })
            payment.create_payments()

            self.check_payments(invoices, 400, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 100)

    def test_full_payment_process_usd_02(self):
        """Paying USD invoices with USD payment(Excess)"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_usd, self.bank_journal_usd, 400)
            payment.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })
            payment.create_payments()

            self.check_payments(invoices, 400, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 36740.88)

    def test_full_payment_process_multi_currencies_usd_02(self):
        """Pay with Excess invoices with different currencies with USD
        payment"""
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
                invoices, payment_type[invo_type], self.currency_usd, self.bank_journal_usd, 200)

            payment.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })

            payment.create_payments()

            self.check_payments(invoices, 200, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 36540.89)

    def test_full_payment_process_multi_currencies_mxn_02(self):
        """Pay with Excess invoices with different currencies with MXN
        payment"""
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
            payment.update({
                'amount': payment.amount + 831.71,
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })
            payment._onchange_payment_invoice()
            payment.create_payments()

            self.check_payments(invoices, payment.amount, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 831.71)

    # ----------------------------- Partial --------------------------------

    def test_full_payment_process_03(self):
        """Partial Payment: invoices and payment with the same currency MXN"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_mxn.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_mxn, self.bank_journal_mxn, 200)

            payment.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })
            payment.create_payments()

            self.check_payments(invoices, 200, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 100)

    def test_full_payment_process_usd_03(self):
        """Partial Payment: invoices and payment with the same currency USD"""
        payment_type = {'in_invoice': 'outbound', 'out_invoice': 'inbound'}
        for invo_type in ('in_invoice', 'out_invoice'):
            inv_1 = self.create_invoice(
                inv_type=invo_type,
                amount=100, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)
            inv_2 = self.create_invoice(
                inv_type=invo_type,
                amount=200, currency_id=self.currency_usd.id,
                partner=self.partner_agrolait.id)

            invoices = (inv_1 + inv_2)
            payment = self.create_payment(
                invoices, payment_type[invo_type], self.currency_usd, self.bank_journal_usd, 200)
            payment.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })
            payment._onchange_payment_invoice()
            payment.create_payments()

            self.check_payments(invoices, 200, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 36740.89)

    def test_full_payment_process_multi_currencies_usd_03(self):
        """Partial Payment: invoices with different currencies and USD
        payment"""
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
                invoices, payment_type[invo_type], self.currency_usd, self.bank_journal_usd, 80)
            payment.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })

            payment.create_payments()

            self.check_payments(invoices, 80, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 7548.18)

    def test_full_payment_process_multi_currencies_mxn_03(self):
        """Partial Payment: invoices with different currencies and MXN
        payment"""
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

            payment.update({
                'amount': payment.amount + 668.29,
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': self.diff_expense_account.id,
            })
            payment._onchange_payment_invoice()
            payment.create_payments()

            self.check_payments(invoices, payment.amount, 4)

            payment = self.payment_model.search(
                [('invoice_ids', 'in', invoices.ids)], order="id desc",
                limit=1)

            writeoff_line = payment.move_line_ids.filtered(
                lambda a: a.account_id == self.diff_expense_account)

            self.assertEqual(abs(writeoff_line.balance), 668.29)
