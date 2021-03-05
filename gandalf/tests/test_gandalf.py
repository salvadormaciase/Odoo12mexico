from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged
from odoo.tests.common import Form
try:
    from itertools import zip_longest as izip_longest
except ImportError:
    from itertools import izip_longest

from ..models.account import s2d


@tagged('post_install', '-at_install')
class TestGandalf(AccountTestInvoicingCommon):

    def setUp(self):
        super(TestGandalf, self).setUp()
        self.account_obj = self.env['account.account']
        self.invoice_model = self.env['account.move']
        self.invoice_line_obj = self.env['account.move.line']
        self.account_payment_model = self.env['account.payment']
        self.res_currency_model = self.env['res.currency']
        self.rate_model = self.env['res.currency.rate']
        self.am_obj = self.env['account.move']
        self.aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        self.arl_obj = self.env['account.revaluation.ledger']
        self.fp_obj = self.env['account.fiscal.position']
        self.rcs_obj = self.env['res.config.settings']

        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.currency_usd_id = self.env.ref("base.USD").id
        self.currency_eur_id = self.env.ref("base.EUR").id
        self.company = self.env.user.company_id
        self.product = self.env.ref("product.product_product_4")

        self.bank_journal_mxn = self.env['account.journal'].create({
            'name': 'Bank MXN',
            'type': 'bank',
            'code': 'BNK31'})
        self.bank_account_mxn = self.bank_journal_mxn.default_account_id

        self.bank_journal_eur = self.env['account.journal'].create({
            'name': 'Bank EUR',
            'type': 'bank',
            'code': 'BNK79',
            'currency_id': self.currency_eur_id})
        self.bank_account_eur = self.bank_journal_eur.default_account_id

        self.bank_journal_usd = self.env['account.journal'].create({
            'name': 'Bank US',
            'type': 'bank',
            'code': 'BNK68'})
        self.bank_account = self.bank_journal_usd.default_account_id

        self.diff_income_account = self.company.income_currency_exchange_account_id
        self.diff_expense_account = self.company.expense_currency_exchange_account_id

        self.inbound_payment_method = (
            self.env['account.payment.method'].create({
                'name': 'inbound',
                'code': 'IN',
                'payment_type': 'inbound',
            }))

        self.equity_account = self.account_obj.create({
            'name': 'EQT',
            'code': 'EQT',
            'user_type_id':
            self.env.ref('account.data_account_type_equity').id,
            'company_id': self.env['res.users'].browse(self.env.uid).company_id.id,
        })

        self.expense_account = self.account_obj.create({
            'name': 'EXP',
            'code': 'EXP',
            'user_type_id':
            self.env.ref('account.data_account_type_expenses').id,
            'company_id': self.env['res.users'].browse(self.env.uid).company_id.id,
        })
        # cash basis intermediary account
        self.tax_waiting_account = self.account_obj.create({
            'name': 'TAX_WAIT',
            'code': 'TWAIT',
            'user_type_id':
            self.env.ref('account.data_account_type_current_liabilities').id,
            'reconcile': True,
            'company_id': self.env['res.users'].browse(self.env.uid).company_id.id,
        })
        # cash basis final account
        self.tax_final_account = self.account_obj.create({
            'name': 'TAX_TO_DEDUCT',
            'code': 'TDEDUCT',
            'user_type_id':
            self.env.ref('account.data_account_type_current_assets').id,
            'company_id': self.env['res.users'].browse(self.env.uid).company_id.id,
        })
        self.tax_base_amount_account = self.account_obj.create({
            'name': 'TAX_BASE',
            'code': 'TBASE',
            'user_type_id':
            self.env.ref('account.data_account_type_current_assets').id,
            'company_id': self.env['res.users'].browse(self.env.uid).company_id.id,
        })

        # Journals
        self.purchase_journal = self.env['account.journal'].create({
            'name': 'purchase',
            'code': 'PURCH',
            'type': 'purchase',
        })

        self.cash_basis_journal = self.company.tax_cash_basis_journal_id
        self.fx_journal = self.company.currency_exchange_journal_id

        # Tax Cash Basis
        self.tax_cash_basis = self.env['account.tax'].create({
            'name': 'cash basis 16%',
            'type_tax_use': 'purchase',
            'company_id': self.env['res.users'].browse(self.env.uid).company_id.id,
            'amount': 16,
            'tax_exigibility': 'on_payment',
            'cash_basis_transition_account_id': self.tax_waiting_account.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': self.tax_final_account.id,
                }),
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': self.tax_final_account.id,
                }),
            ],
        })

        self.rcs_obj.search([('company_id', '=', self.company.id)]).write({
            'sale_tax_id': self.tax_cash_basis.id,
            'purchase_tax_id': self.tax_cash_basis.id,
            'account_cash_basis_base_account_id': self.tax_base_amount_account.id,
        })

        self.nov_21 = s2d('2018-11-21')
        self.nov_29 = s2d('2018-11-29')
        self.nov_30 = s2d('2018-11-30')
        self.dec_20 = s2d('2018-12-20')
        self.dec_31 = s2d('2018-12-31')
        self.jan_01 = s2d('2019-01-01')

        self.delete_journal_data()

        self.payment_method_manual_out = self.env.ref(
            'account.account_payment_method_manual_out')
        self.payment_method_manual_in = self.env.ref(
            'account.account_payment_method_manual_in')

        self.env.user.company_id.write({'currency_id': self.ref('base.MXN')})

        self.create_fiscal_position()
        self.create_rates()

    def create_fiscal_position(self):
        account_fp = self.fp_obj.create(dict(
            name="Invoice Fiscal Position",
            vat_required=False,
            sequence=10,
            account_ids=[(0, 0, dict(
                account_src_id=self.bank_account_eur.id,
                account_dest_id=self.bank_account_mxn.id))]))

        rec_pay_ids = self.account_obj.search(
            [('internal_type', 'in', ('receivable', 'payable')), ('company_id', '=', self.company.id)])

        invoice_fp = self.fp_obj.create(dict(
            name="Invoice Fiscal Position",
            vat_required=False,
            sequence=10,
            company_id=self.env['res.users'].browse(self.env.uid).company_id.id,
            account_ids=[(0, 0, dict(
                account_src_id=account.id,
                account_dest_id=self.equity_account.id))
                for account in rec_pay_ids]))
        self.company.write({
            'invoice_realization_position_id': invoice_fp.id,
            'account_realization_position_id': account_fp.id})

    def delete_journal_data(self):
        """Delete journal data
        delete all journal-related data, so a new currency can be set.
        """

        # 1. Reset to draft invoices and moves, so some records may be deleted
        company = self.company
        moves = self.am_obj.search(
            [('company_id', '=', company.id)])
        moves.write({'state': 'draft'})
        invoices = self.invoice_model.search([('company_id', '=', company.id)])
        invoices.write({'state': 'draft', 'name': '/'})

        # 2. Delete related records
        models_to_clear = [
            'account.move.line',
            'account.payment', 'account.bank.statement', 'res.currency.rate']
        for model in models_to_clear:
            records = self.env[model].search([('company_id', '=', company.id)])
            records.unlink()
        self.am_obj.search([]).unlink()

    def create_rates(self):
        dates = (self.nov_21, self.nov_29, self.nov_30, self.dec_20,
                 self.dec_31, self.jan_01)

        rates = (20.1550, 20.4977, 20.4108, 20.1277, 19.6829, 19.6566)
        for name, rate in izip_longest(dates, rates):
            self.rate_model.sudo().create({
                'currency_id': self.currency_eur_id,
                'company_id': self.company.id,
                'name': name,
                'rate': round(1/rate, 6)})

    def create_payment(self, invoice_record, pay_date, amount=0.0, bank_journal=None, amount_currency=0.0,
                       currency_id=None):

        partner_type = 'customer' if invoice_record.move_type in ('out_invoice', 'out_refund') else 'supplier'
        payment_type = 'inbound' if invoice_record.move_type in ('out_invoice', 'in_refund') else 'outbound'
        account_type = 'receivable' if invoice_record.move_type in ('out_invoice', 'in_refund') else 'payable'

        payment_form = Form(self.account_payment_model.with_context(
            default_partner_type=partner_type, default_payment_type=payment_type))

        payment_form.amount = amount
        payment_form.date = pay_date
        payment_form.currency_id = currency_id if currency_id else bank_journal.currency_id
        payment_form.journal_id = bank_journal
        payment_form.partner_id = self.partner_agrolait

        payment = payment_form.save()

        payment.action_post()

        lines = (payment.line_ids | invoice_record.line_ids).filtered(
            lambda l: l.account_id.internal_type == account_type)

        lines.reconcile()

        return payment

    def create_account(self, code, name, user_type_id=False):
        """This account is created to use like cash basis account and only
        it will be filled when there is payment
        """
        account_ter = self.account_model.create({
            'name': name,
            'code': code,
            'user_type_id': user_type_id or self.user_type_id.id,
        })
        return account_ter

    def _create_invoice(self, inv_type='out_invoice', invoice_amount=50, currency_id=None, partner_id=None,
                        date_invoice=None, payment_term_id=False, auto_validate=False):
        move_form = Form(self.invoice_model.with_context(default_move_type=inv_type))
        move_form.invoice_date = date_invoice
        move_form.partner_id = partner_id or self.partner_agrolait
        move_form.date = date_invoice

        if currency_id:
            move_form.currency_id = self.res_currency_model.browse(currency_id)

        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = 'product that cost %s' % invoice_amount
            line_form.quantity = 1
            line_form.price_unit = invoice_amount
            line_form.account_id = self.expense_account
            line_form.tax_ids.clear()
            line_form.tax_ids.add(self.tax_cash_basis)

        invoice = move_form.save()
        invoice.action_post()

        return invoice

    def create_invoice(self, invoice_amount=50, date_invoice=None, inv_type='out_invoice', currency_id=None):
        return self._create_invoice(
            inv_type=inv_type, invoice_amount=invoice_amount, date_invoice=date_invoice, currency_id=currency_id,
            auto_validate=True)

    def test_001_create(self):

        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        self.create_payment(
            invoice_id, self.dec_20, 6149.16, self.bank_journal_eur)

        invoice_id.realize_invoice(self.dec_31, self.dec_20)

        self.assertEqual(
            len(invoice_id.realization_move_ids), 0,
            'There should be No Realization entry')

        invoice_id.realize_invoice(self.dec_31, self.dec_20, do_entry=True)
        self.assertEqual(
            invoice_id.realization_move_ids.date, self.dec_20,
            'Wrong Realization entry date')

        self.assertEqual(
            len(invoice_id.realization_move_ids), 1,
            'There should be One Realization entry')

        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 2,
            'There should be Two Revaluation Ledger Items')

        self.assertEqual(
            invoice_id.date_last_ledger, self.dec_20,
            'Wrong date on Last Ledger Date')

        self.assertTrue(
            invoice_id.fully_realized,
            'This Invoice should be fully realized')

    def test_001_create_invoice_reconciling_with_credit_note(self):

        # /!\ NOTE: If someone enough picky and thorough checks on the amounts on this test (v13) and the ones in v12
        # s/he will realize that 5301 * 1.16 = 6149.16. This change is related in the way invoice in this Unit Tests
        # v13 are created.
        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)
        invoice_line_id = invoice_id.line_ids.filtered(
            lambda l: l.account_id.user_type_id.type in ('receivable', 'payable'))
        invoice_account_id = invoice_line_id.account_id

        credit_note_id = self.create_invoice(
            5301, self.dec_20,
            inv_type='in_refund',
            currency_id=self.currency_eur_id)

        credit_note_aml_id = credit_note_id.line_ids.filtered(
            lambda l: l.account_id == invoice_account_id)

        (invoice_line_id | credit_note_aml_id).with_context(default_type='entry').reconcile()

        # NOTE: On all the previous versions of Odoo (v11 / v12 / v13) tax
        # recomputation for CABA entries were performed at the Invoice rate,
        # leading in MX to inconsistencies in the FX entries for taxes. Vauxoo
        # managed to address using `l10n_mx_tax_cash_basis` module. Without
        # that module when an invoice and a refund were reconciled taxed didn't
        # yield any FX entry. That is not longer the case for v14.
        # This reasoning is based on the results fetched from this unit test.
        # More research on it may change my opinion in the future.
        # NOTE: The warning below no longer applies!!! It was left for
        # historical reasons.
        ############################################
        # DON'T YOU DARE TO DELETE THIS COMMENT!!! #
        ############################################
        # /!\ WARNING: Test on taxes are done on Odoo's perspective on MX the
        # tax from CABA is computed on rate at date of payment. In this case at
        # rate of Credit Note.

        invoice_id.realize_invoice(self.dec_31, self.dec_20)
        arl_dec_20 = (
            invoice_id.revaluation_ledger_ids.filtered(
                lambda x: x.date == self.dec_20 and
                x.account_id == invoice_account_id).fx_amount)
        self.assertEqual(
            arl_dec_20, 169.63, 'Something went wrong on Dec 20')
        arl_dec_20_tax = (
            invoice_id.revaluation_ledger_ids.filtered(
                lambda x: x.date == self.dec_20 and
                x.account_id == self.tax_waiting_account).fx_amount)
        self.assertAlmostEqual(arl_dec_20_tax, -23.40, 2, 'Something went wrong on Dec 20 in the Invoice Tax')

        credit_note_id.realize_invoice(self.dec_31, self.dec_20)
        arl_dec_20 = (
            credit_note_id.revaluation_ledger_ids.filtered(
                lambda x: x.date == self.dec_20 and
                x.account_id == invoice_account_id).fx_amount)
        self.assertEqual(
            arl_dec_20, 169.63, 'Something went wrong on Dec 20')
        arl_dec_20_tax = (
            credit_note_id.revaluation_ledger_ids.filtered(
                lambda x: x.date == self.dec_20 and
                x.account_id == self.tax_waiting_account).fx_amount)
        self.assertAlmostEqual(arl_dec_20_tax, -23.40, 2, 'Something went wrong on Dec 20 in the Invoice Tax')

    def test_001_month_end_invoice_no_previous_payment(self):

        invoice_id = self.create_invoice(
            5301, self.nov_30.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        invoice_id.realize_invoice(self.nov_30, '2018-01-01')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 0,
            'There should be No Revaluation Ledger Items')

    def test_001_month_end_invoice_with_previous_payment(self):

        invoice_id = self.create_invoice(
            5301, self.nov_30.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        self.create_payment(
            invoice_id, self.nov_21, 6149.16, self.bank_journal_eur)

        invoice_id.realize_invoice(self.nov_30, '2018-01-01')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 2,
            'There should be Two Revaluation Ledger Items')

    def test_001_no_month_end_invoice_with_previous_payment(self):

        invoice_id = self.create_invoice(
            806.60, '2019-03-27',
            inv_type='out_invoice',
            currency_id=self.currency_eur_id)

        self.create_payment(
            invoice_id, '2018-12-31', 112.75, self.bank_journal_eur)
        self.create_payment(
            invoice_id, '2019-01-31', 0.02, self.bank_journal_eur)
        self.create_payment(
            invoice_id, '2019-03-26', 822.89, self.bank_journal_eur)

        invoice_id.realize_invoice('2019-08-31', '2018-12-31')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 2,
            'There should be Two Revaluation Ledger Items')
        self.assertEqual(
            invoice_id.revaluation_ledger_ids[0].date, invoice_id.date,
            'Revaluation Ledger Date should be equal to Invoice Date')

    def test_001_month_end_invoice_with_payment_on_same_date(self):

        invoice_id = self.create_invoice(
            5301, self.nov_30.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        self.create_payment(
            invoice_id, self.nov_30, 6149.16, self.bank_journal_eur)

        invoice_id.realize_invoice(self.nov_30, '2018-01-01')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 2,
            'There should be Two Revaluation Ledger Items')

    def test_001_month_end_invoice_with_payment_afterwards(self):

        invoice_id = self.create_invoice(
            5301, self.nov_30.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        self.create_payment(
            invoice_id, self.dec_20, 6149.16, self.bank_journal_eur)

        invoice_id.realize_invoice(self.nov_30, '2018-01-01')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 0,
            'There should be Two Revaluation Ledger Items')

    def test_002_create(self):
        """ Test 002
        Having issued an invoice at date Nov-21-2018 as:

        Accounts         Amount Currency         Debit(EUR)       Credit(EUR)
        ---------------------------------------------------------------------
        Expenses            5,301.00 USD         106,841.65              0.00
        Taxes                 848.16 USD          17,094.66              0.00
            Payables       -6,149.16 USD               0.00        123,936.31

        On Nov-30-2018 user issues an FX Journal Entry as required by law:

        Accounts         Amount Currency         Debit(EUR)       Credit(EUR)
        ---------------------------------------------------------------------
        FX Losses               0.00 USD           1,570.91             0.00
            Payables            0.00 USD               0.00         1,570.91

        On Dec-20-2018 user issues an FX Journal Entry as payment is done:

        Accounts         Amount Currency         Debit(EUR)       Credit(EUR)
        ---------------------------------------------------------------------
        Payables                0.00 USD           1,740.54             0.00
            FX Gains            0.00 USD               0.00         1,740.54
        """

        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        invoice_id.create_realization_entries(
            stop_date='2000-01-01', do_entry=True)
        self.assertEqual(
            invoice_id.realization_move_ids_nbr, 0,
            'There should be no Realization entry')

        invoice_id.create_realization_entries(
            stop_date=self.nov_30, do_entry=True)
        self.assertEqual(
            len(invoice_id.realization_move_ids), 1,
            'There should be One Realization entry')

        action = (
            invoice_id.with_context(realization_move=True)
            .action_view_realization_move())
        self.assertEqual(
            action.get('res_id'), invoice_id.realization_move_ids[0].id,
            'There should be One Realization entry')

        action = (
            invoice_id.with_context(revaluation_ledger=True)
            .action_view_realization_move())
        self.assertEqual(
            action.get('domain'),
            [('id', 'in', invoice_id.revaluation_ledger_ids.ids)],
            'There should be Two Revaluation Ledger Items')

        self.create_payment(
            invoice_id, self.dec_20, 6149.16, self.bank_journal_eur)

        invoice_id.create_realization_entries(
            stop_date=self.dec_31, do_entry=True)
        self.assertEqual(
            min(invoice_id.mapped('realization_move_ids.date')), self.nov_30,
            'Wrong Realization entry date')
        self.assertEqual(
            max(invoice_id.mapped('realization_move_ids.date')), self.dec_20,
            'Wrong Realization entry date')

        aml_nov_30 = (
            invoice_id
            .mapped('realization_move_ids.line_ids')
            .filtered(
                lambda x:
                x.account_id == self.equity_account and
                x.date == self.nov_30))
        self.assertEqual(
            aml_nov_30.credit, 1570.91, 'Wrong Credit on Reevaluation')

        aml_nov_30_tax = (
            invoice_id
            .mapped('realization_move_ids.line_ids')
            .filtered(
                lambda x:
                x.account_id == self.tax_waiting_account and
                x.date == self.nov_30))
        self.assertEqual(
            aml_nov_30_tax.debit, 216.68, 'Wrong Debit on Reevaluation')

        aml_dec_20 = (
            invoice_id
            .mapped('realization_move_ids.line_ids')
            .filtered(
                lambda x:
                x.account_id == self.equity_account and
                x.date == self.dec_20))
        self.assertEqual(
            aml_dec_20.debit, 1740.54, 'Wrong Debit on Reevaluation')

    def test_003_create(self):

        invoice_id = self.create_invoice(
            6149.16, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        invoice_id.create_realization_entries(
            init_date='2000-01-01', do_entry=True)
        self.assertNotEqual(
            len(invoice_id.realization_move_ids), 0,
            'There should be at least One Realization entry')

        invoice_id.button_draft()
        self.assertEqual(
            len(invoice_id.realization_move_ids), 0,
            'There should be no Realization entry')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 0,
            'There should be no Revaluation Ledger Items')

        invoice_id.create_realization_entries(
            stop_date=self.nov_30.strftime('%Y-%m-%d'), do_entry=True)
        self.assertEqual(
            len(invoice_id.realization_move_ids), 0,
            'There should be no Realization entry')
        self.assertEqual(
            len(invoice_id.revaluation_ledger_ids), 0,
            'There should be no Revaluation Ledger Items')

    def test_004_create(self):

        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        invoice_id.create_realization_entries(
            stop_date=self.nov_30, do_entry=True)

        self.assertEqual(
            invoice_id.realization_move_ids_nbr, 1,
            'There should be One Realization entry')
        self.assertEqual(
            invoice_id.mapped('realization_move_ids.date')[0], self.nov_30,
            'Dates should be equal on Entries')

        self.assertEqual(
            invoice_id.revaluation_ledger_ids_nbr, 2,
            'There should be Two Revaluation Ledger Items')
        self.assertEqual(
            invoice_id.mapped('revaluation_ledger_ids.date')[0], self.nov_30,
            'Dates should be equal on Items')

        invoice_id.button_draft()
        self.assertEqual(
            invoice_id.realization_move_ids_nbr, 0,
            'There should be No Realization entry')
        self.assertEqual(
            invoice_id.revaluation_ledger_ids_nbr, 0,
            'There should be No Revaluation Ledger Item')

        invoice_id.action_post()

        invoice_id.create_realization_entries(
            stop_date=self.nov_30, do_entry=False)
        self.assertEqual(
            invoice_id.realization_move_ids_nbr, 0,
            'There should be No Realization entry')

    def test_005_create(self):
        """ Test 005 - Invoice in local currency
        """

        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.company.currency_id.id)

        invoice_id.create_realization_entries(
            stop_date=self.nov_30, do_entry=True)
        self.assertEqual(
            invoice_id.realization_move_ids_nbr, 0,
            'There should be No Realization entry')
        self.assertEqual(
            invoice_id.revaluation_ledger_ids_nbr, 0,
            'There should be No Revaluation Ledger Item')

    def test_006_create(self):

        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='out_invoice',
            currency_id=self.currency_eur_id)

        self.create_payment(
            invoice_id, self.dec_20, 6149.16, self.bank_journal_eur)

        today = s2d(fields.Date.today())

        # /!\ NOTE: It is due to run tomorrow
        res = self.arl_obj.cron_monthly_realization(
            today.day + 1, init_date=self.nov_21)
        self.assertEqual(res, False, 'Cron Job should have not run')

        res = len(self.arl_obj.search([]))
        self.assertEqual(
            res, 0, 'There should be no Revaluation Ledger Items')

        # /!\ NOTE: It is due to run today. Only for one month span.
        res = self.arl_obj.cron_monthly_realization(today.day)
        self.assertEqual(res, True, 'Cron Job should have run')

        # /!\ NOTE: This produces no results as the invoice is fully paid and
        # is out of the scope of the revaluation.
        res = len(self.arl_obj.search([]))
        self.assertEqual(
            res, 0, 'There should be no Revaluation Ledger Items')

        # /!\ NOTE: It is due to run today. Since 2001-01-01
        res = self.arl_obj.cron_monthly_realization(
            today.day, init_date='2001-01-01')
        self.assertEqual(res, True, 'Cron Job should have run')

        res = len(self.arl_obj.search([]))
        self.assertNotEqual(
            res, 0, 'There should be Revaluation Ledger Items')

    def test_008_create(self):
        """Computing account realization from wizard"""

        wizard = self.env['realization.date.wizard']

        record = wizard.with_context(
            {'active_id': False,
             'active_ids': [],
             'active_model': 'account.move'}).create(
                 {'realization_date': self.dec_20})
        record.onchange_internal_type()
        record.compute_realization()

        invoice_id = self.create_invoice(
            5301, self.nov_21.strftime('%Y-%m-%d'),
            inv_type='in_invoice',
            currency_id=self.currency_eur_id)

        record = wizard.with_context(
            {'active_id': invoice_id.id,
             'active_ids': invoice_id.ids,
             'active_model': 'account.revaluation.ledger'}).create(
                 {'realization_date': self.dec_20})
        record.onchange_internal_type()
        record.compute_realization()

        res = len(self.arl_obj.search([]))
        self.assertEqual(
            res, 0, 'There should be no Revaluation Ledger Items')

        record = wizard.with_context(
            {'active_id': invoice_id.id,
             'active_ids': invoice_id.ids,
             'active_model': 'account.move'}).create(
                 {'realization_date': self.dec_20})
        record.onchange_internal_type()
        record.compute_realization()

        fx_move_before = invoice_id.revaluation_ledger_ids

        record = wizard.with_context(
            {'active_id': invoice_id.id,
             'active_ids': invoice_id.ids,
             'active_model': 'account.move'}).create(
                 {'realization_date': self.dec_31})
        record.onchange_internal_type()
        record.compute_realization()

        fx_move_after = invoice_id.revaluation_ledger_ids

        self.assertNotEqual(
            fx_move_after, fx_move_before,
            'For different rates in same month FX Journal must change')

        res = len(self.arl_obj.search([]))
        self.assertNotEqual(
            res, 0, 'There should be Revaluation Ledger Items')

    def test_101_account_realization(self):
        """ - Test 101
        Company's Currency EUR

        Having made a bank deposit at date Nov-21-2018 as:

        Accounts         Amount Currency         Debit(EUR)       Credit(EUR)
        ---------------------------------------------------------------------
        Bank                6,149.16 USD         123,936.31              0.00
            Equity         -6,149.16 USD               0.00        123,936.31

        On Nov-30-2018 user issues an FX Journal Entry as:

        Accounts         Amount Currency         Debit(EUR)       Credit(EUR)
        ---------------------------------------------------------------------
        Bank                    0.00 USD           1.572.12             0.00
            FX Gains            0.00 USD               0.00         1.572.12

        So Bank balance at November 30th is: EUR 125,508.43 = USD 6,149.16

        On Dec-20-2018 user issues an FX Journal Entry as:

        Accounts         Amount Currency         Debit(EUR)       Credit(EUR)
        ---------------------------------------------------------------------
        FX Losses               0.00 USD           1.740.54             0.00
            Bank                0.00 USD               0.00         1.740.54

        So Bank balance at December 20th is: EUR 123,767.89 = USD 6,149.16
        """

        company = self.env.ref('base.main_company')
        company.country_id = self.ref('base.us')
        company.tax_cash_basis_journal_id = self.cash_basis_journal

        # Bank Deposit
        bank_move = self.am_obj.create({
            'date': self.nov_21,
            'name': 'Bank Deposit',
            'journal_id': self.bank_journal_eur.id,
        })

        self.aml_obj.create({
            'move_id': bank_move.id,
            'name': 'Equity Item',
            'account_id': self.equity_account.id,
            'credit': 123936.31,
            'amount_currency': -6149.16,
            'currency_id': self.currency_eur_id,
        })
        self.aml_obj.create({
            'move_id': bank_move.id,
            'name': 'Bank Deposit',
            'account_id': self.bank_account_eur.id,
            'debit': 123936.31,
            'amount_currency': 6149.16,
            'currency_id': self.currency_eur_id,
        })
        bank_move.action_post()

        aml_ids = self.aml_obj.search(
            [('account_id', '=', self.bank_account_eur.id)])

        self.assertEqual(
            sum(aml_ids.mapped('balance')), 123936.31,
            'Incorrect Balance for Account')

        self.assertEqual(
            sum(aml_ids.mapped('amount_currency')), 6149.16,
            'Incorrect Balance for Account')

        self.arl_obj.process_realization(
            'account', date='2018-01-01', do_entry=True)
        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 0,
            'There should be no journal entry')

        self.account_obj.create_realization_entries(stop_date=self.nov_30)
        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 0,
            'There should be no journal entry')
        self.assertEqual(
            self.bank_account_eur.revaluation_ledger_ids_nbr, 0,
            'There should be no journal entry')

        self.bank_account_eur.write({'realizable_account': True})

        self.bank_account_eur.refresh()
        self.bank_account_eur.flush()

        self.bank_account_eur.create_realization_entries(
            stop_date=self.nov_30)
        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 0,
            'There should be No journal entry')

        self.bank_account_eur.create_realization_entries(
            stop_date=self.nov_30, do_entry=True)

        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 1,
            'There should be One journal entry')
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 1,
            'There should be One Revaluation Ledger Item')

        action = (
            self.bank_account_eur.with_context(realization_move=True)
            .action_view_realization_move())
        self.assertEqual(
            action.get('res_id'),
            self.bank_account_eur.realization_move_ids[0].id,
            'There should be One Realization entry')

        action = (
            self.bank_account_eur.with_context(revaluation_ledger=True)
            .action_view_realization_move())
        self.assertEqual(
            action.get('domain'),
            [('id', 'in', self.bank_account_eur.revaluation_ledger_ids.ids)],
            'There should be Two Revaluation Ledger Items')

        rev_aml_ids = (
            self.bank_account_eur.realization_move_ids
            .mapped('line_ids')
            .filtered(lambda x: x.account_id == self.bank_account_mxn))

        self.assertEqual(
            round(sum(rev_aml_ids.mapped('debit')), 2), 1572.12,
            'Incorrect Balance for Account')

        aml_ids = self.aml_obj.search(
            [('account_id', '=', self.bank_account_mxn.id)])
        self.assertEqual(
            round(sum(aml_ids.mapped('balance')), 2), 1572.12,
            'Incorrect Balance for Reevaluated Account')

        aml_ids = self.aml_obj.search(
            [('account_id', '=', self.bank_account_eur.id)])
        self.assertEqual(
            round(sum(aml_ids.mapped('balance')), 2), 123936.31,
            'Incorrect Balance for Reevaluated Account')

        self.assertEqual(
            round(sum(aml_ids.mapped('amount_currency')), 2), 6149.16,
            'Incorrect Balance for Account')

        self.bank_account_eur.create_realization_entries(
            stop_date=self.dec_20, do_entry=True)

        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 2,
            'There should be Two journal entries')
        self.assertEqual(
            self.bank_account_eur.revaluation_ledger_ids_nbr, 2,
            'There should be Two Revaluation Ledger Item')
        self.assertEqual(
            self.bank_account_eur.date_last_ledger, self.dec_20,
            'Wrong date on Last Ledger Date')

        rev_aml_ids = (
            self.bank_account_eur.realization_move_ids
            .mapped('line_ids')
            .filtered(
                lambda x: x.account_id == self.bank_account_mxn and
                x.date == self.dec_20))

        self.assertEqual(
            sum(rev_aml_ids.mapped('credit')), 1740.54,
            'Incorrect Balance for Account')

        aml_ids = self.aml_obj.search(
            [('account_id', '=', self.bank_account_mxn.id)])

        self.assertEqual(
            round(sum(aml_ids.mapped('balance')), 2), -168.42,
            'Incorrect Balance for Reevaluated Account')

        aml_ids = self.aml_obj.search(
            [('account_id', '=', self.bank_account_eur.id)])
        self.assertEqual(
            sum(aml_ids.mapped('balance')), 123936.31,
            'Incorrect Balance for Reevaluated Account')
        self.assertEqual(
            sum(aml_ids.mapped('amount_currency')), 6149.16,
            'Incorrect Balance for Account')

    def test_104_account_realization_non_realizable_account(self):

        company = self.env.ref('base.main_company')
        company.country_id = self.ref('base.us')
        company.tax_cash_basis_journal_id = self.cash_basis_journal

        # Bank Deposit
        bank_move = self.am_obj.create({
            'date': self.nov_21,
            'name': 'Bank Deposit',
            'journal_id': self.bank_journal_usd.id,
        })

        self.aml_obj.create({
            'move_id': bank_move.id,
            'name': 'Equity Item',
            'account_id': self.equity_account.id,
            'credit': 123936.31,
        })
        self.aml_obj.create({
            'move_id': bank_move.id,
            'name': 'Bank Deposit',
            'account_id': self.bank_account_eur.id,
            'debit': 123936.31,
            'amount_currency': 6149.10,
            'currency_id': self.bank_account_eur.currency_id.id,
        })
        bank_move.action_post()

        aml_ids = self.aml_obj.search(
            [('account_id', '=', self.bank_account_eur.id)])

        self.assertEqual(
            sum(aml_ids.mapped('balance')), 123936.31,
            'Incorrect Balance for Account')

        self.assertEqual(
            sum(aml_ids.mapped('amount_currency')), 6149.10,
            'Incorrect Balance for Account')

        self.bank_account_eur.create_realization_entries(
            stop_date=self.nov_30, do_entry=True)

        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 0,
            'There should be no journal entry')
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 0,
            'There should be no Revaluation Ledger Items')

    def test_105_account_realization_non_realizable_account(self):
        self.bank_account_mxn.write({
            'realizable_account': True,
            'deprecated': True})
        self.bank_account_mxn.create_realization_entries()
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 0,
            'There are Revaluation Ledger Items on Deprecated Account')

    def test_106_account_realization_non_realizable_account(self):
        self.bank_account_mxn.write({'realizable_account': True})
        self.bank_account_mxn.create_realization_entries(
            stop_date='2019-01-01')
        self.assertEqual(
            len(self.bank_account_mxn.revaluation_ledger_ids), 0,
            'There are Revaluation Ledger Items on Account with no currency')

    def test_107_account_realization_non_realizable_account(self):
        self.bank_account_mxn.write({
            'realizable_account': True,
            'currency_id': self.bank_account_mxn.company_id.currency_id.id
        })

        self.bank_account_eur.refresh()
        self.bank_account_eur.flush()

        self.bank_account_mxn.create_realization_entries(
            init_date='2001-01-01')
        self.assertEqual(
            len(self.bank_account_mxn.revaluation_ledger_ids), 0,
            'There are Revaluation Ledger Items on Account with currency '
            'same in the company')

    def test_108_account_realization_non_realizable_account(self):
        self.bank_account_eur.write({'realizable_account': True})
        self.bank_account_eur.create_realization_entries(
            stop_date='2000-01-01', init_date='2001-01-01')
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 0,
            'There are Revaluation Ledger Items in a Configuration that seems '
            'impossible to provide meaningful data')

    def test_109_account_realization_non_realizable_account(self):
        self.bank_account_eur.write({'realizable_account': True})
        self.bank_account_eur.create_realization_entries(
            do_ledger=False, do_entry=True)
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 0,
            'There should be no Revaluation Ledger Items')
        self.assertEqual(
            len(self.bank_account_eur.realization_move_ids), 0,
            'There should be no Journal Entries in this account as no '
            'Revaluation Ledger Items were created')

    def test_110_account_realization(self):
        # /!\ WARNING: Ugly hack! I had to write the value Through orm thus ORM reads it in the code been tested.
        self.bank_account_eur.write({'realizable_account': True})
        # /!\ WARNING: Oh yeah! I had to do this in order to be able to test the code where the SQL is used.
        # Odoo has done this before in Unit Tests too.
        self.cr.execute("UPDATE account_account SET realizable_account = TRUE WHERE id = %s",
                        [self.bank_account_eur.id])
        self.arl_obj.process_realization(
            'account', do_ledger=False, do_entry=True)
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 0,
            'There should be no Revaluation Ledger Items')
        self.assertEqual(
            len(self.bank_account_eur.realization_move_ids), 0,
            'There should be no Journal Entries in this account as no '
            'Revaluation Ledger Items were created')

    def test_111_realization(self):
        with self.assertRaises(Exception):
            self.arl_obj.prepare_realization_move(
                fields.Date.today(), invoice_id=False, account_id=False)
        with self.assertRaises(Exception):
            self.arl_obj._remove_previous_revaluation(
                fields.Date.today(), invoice_id=False, account_id=False)

    def test_112_account_realization(self):
        company = self.env.ref('base.main_company')
        company.country_id = self.ref('base.us')
        company.tax_cash_basis_journal_id = self.cash_basis_journal

        # Bank Deposit
        bank_move = self.am_obj.create({
            'date': self.nov_21,
            'name': 'Bank Deposit',
            'journal_id': self.bank_journal_eur.id,
        })

        self.aml_obj.create({
            'move_id': bank_move.id,
            'name': 'Equity Item',
            'account_id': self.equity_account.id,
            'credit': 123936.31,
            'amount_currency': -6149.16,
            'currency_id': self.currency_eur_id,
        })
        self.aml_obj.create({
            'move_id': bank_move.id,
            'name': 'Bank Deposit',
            'account_id': self.bank_account_eur.id,
            'debit': 123936.31,
            'amount_currency': 6149.16,
            'currency_id': self.currency_eur_id,
        })
        bank_move.action_post()

        self.arl_obj.process_realization(
            'account', do_ledger=False, do_entry=True)
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 0,
            'There should be no Revaluation Ledger Items')
        self.assertEqual(
            len(self.bank_account_eur.realization_move_ids), 0,
            'There should be no Journal Entries in this account as no '
            'Revaluation Ledger Items were created')

        # /!\ WARNING: Ugly hack! I had to write the value Through orm thus ORM reads it in the code been tested.
        self.bank_account_eur.write({'realizable_account': True})
        # /!\ WARNING: Oh yeah! I had to do this in order to be able to test the code where the SQL is used.
        # Odoo has done this before in Unit Tests too.
        self.cr.execute("UPDATE account_account SET realizable_account = TRUE WHERE id = %s",
                        [self.bank_account_eur.id])

        self.bank_account_eur.refresh()
        self.bank_account_eur.flush()

        self.arl_obj.process_realization(
            'account', date=self.nov_30, do_entry=True)

        self.assertEqual(
            self.bank_account_eur.realization_move_ids_nbr, 1,
            'There should be One journal entry')
        self.assertEqual(
            len(self.bank_account_eur.revaluation_ledger_ids), 1,
            'There should be One Revaluation Ledger Item')
