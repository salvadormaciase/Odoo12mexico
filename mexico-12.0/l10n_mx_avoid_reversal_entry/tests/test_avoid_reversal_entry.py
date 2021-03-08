# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxTaxCashBasis(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxTaxCashBasis, self).setUp()
        self.account_move_model = self.env['account.move']
        self.account_model = self.env['account.account']
        self.register_payments_model = self.env['account.register.payments']
        self.today = (self.env['l10n_mx_edi.certificate'].sudo().
                      get_mx_current_datetime())
        self.company.write({'currency_id': self.mxn.id})
        self.tax_cash_basis_journal_id = self.company.tax_cash_basis_journal_id
        self.curr_ex_journal_id = self.company.currency_exchange_journal_id
        self.curr_ex_journal_id.write({'update_posted': True})
        self.tax_cash_basis_journal_id.write({'update_posted': True})
        self.user_type_id = self.env.ref(
            'account.data_account_type_current_liabilities')
        self.payment_method_manual_out = self.env.ref(
            'account.account_payment_method_manual_out')
        self.payment_method_manual_in = self.env.ref(
            'account.account_payment_method_manual_in')
        self.bank_journal_mxn = self.env['account.journal'].create(
            {'name': 'Bank MXN',
             'type': 'bank',
             'code': 'BNK37',
             })
        self.tax_account = self.create_account(
            '11111101', 'Tax Account')
        cash_tax_account = self.create_account(
            '77777777', 'Cash Tax Account')
        account_tax_cash_basis = self.create_account(
            '99999999', 'Tax Base Account')
        self.tax_positive.write({
            'tax_exigibility': 'on_payment',
            'type_tax_use': 'purchase',
            'account_id': self.tax_account.id,
            'refund_account_id': self.tax_account.id,
            'cash_basis_account_id': cash_tax_account.id,
            'cash_basis_base_account_id': account_tax_cash_basis.id
        })
        self.product.supplier_taxes_id = [self.tax_positive.id]

        self.partner_agrolait.write({'supplier': True})
        self.set_currency_rates(mxn_rate=21, usd_rate=1)

    def create_payment(self, invoice, date, amount, journal, currency):
        payment_method_id = self.payment_method_manual_out.id
        if invoice.type == 'in_invoice':
            payment_method_id = self.payment_method_manual_in.id

        ctx = {'active_model': 'account.invoice', 'active_ids': [invoice.id]}
        register_payments = self.register_payments_model.with_context(
            ctx).create({
                'payment_date': date,
                'l10n_mx_edi_payment_method_id': self.payment_method_cash.id,
                'payment_method_id': payment_method_id,
                'journal_id': journal.id,
                'currency_id': currency.id,
                'communication': invoice.number,
                'amount': amount,
            })
        return register_payments.create_payments()

    def delete_journal_data(self):
        """Delete journal data
        delete all journal-related data, so a new currency can be set.
        """

        # 1. Reset to draft invoices and moves, so some records may be deleted
        company = self.company
        moves = self.env['account.move'].search(
            [('company_id', '=', company.id)])
        moves.write({'state': 'draft'})
        invoices = self.invoice_model.search([('company_id', '=', company.id)])
        invoices.write({'state': 'draft', 'move_name': False})

        # 2. Delete related records
        models_to_clear = [
            'account.move.line', 'account.invoice', 'account.payment',
            'account.bank.statement']
        for model in models_to_clear:
            records = self.env[model].search([('company_id', '=', company.id)])
            records.unlink()

    def create_account(self, code, name, user_type_id=False):
        """This account is created to use like cash basis account and only
        it will be filled when there is payment
        """
        return self.account_model.create({
            'name': name,
            'code': code,
            'user_type_id': user_type_id or self.user_type_id.id,
        })

    def test_instead_of_reverting_entry_delete_it(self):
        """What I expect from here:
            - On Payment unreconciliation cash flow journal entry is deleted
        """
        self.delete_journal_data()
        self.tax_account.write({'reconcile': True})
        self.env['res.config.settings'].write({'group_multi_currency': True})
        cash_am_ids = self.env['account.move'].search(
            [('journal_id', 'in', [self.tax_cash_basis_journal_id.id,
                                   self.curr_ex_journal_id.id])])

        self.assertEquals(
            len(cash_am_ids), 0, 'There should be no journal entry')

        invoice_date = self.today - timedelta(days=1)
        invoice_id = self.create_invoice(
            inv_type='in_invoice',
            currency_id=self.usd.id,
        )
        invoice_id.write({'date_invoice': invoice_date.strftime('%Y-%m-%d')})
        invoice_id.refresh()
        invoice_id.compute_taxes()
        invoice_id.action_invoice_open()

        self.create_payment(
            invoice_id, self.today, invoice_id.amount_total,
            self.bank_journal_mxn, self.usd)

        cash_am_ids = self.env['account.move'].search(
            [('journal_id', 'in', [self.tax_cash_basis_journal_id.id,
                                   self.curr_ex_journal_id.id])])
        self.assertEquals(
            len(cash_am_ids), 3, 'There should be Three journal entry')

        invoice_id.mapped('move_id.line_ids').sudo().remove_move_reconcile()

        cash_am_ids = self.env['account.move'].search(
            [('journal_id', 'in', [self.tax_cash_basis_journal_id.id,
                                   self.curr_ex_journal_id.id])])
        self.assertEquals(
            len(cash_am_ids), 0, 'There should be no journal entry')

    def test_reverting_exchange_difference_from_non_mxn(self):
        self.delete_journal_data()
        self.company.write({
            'currency_id': self.usd.id,
            'country_id': self.env.ref('base.us').id,
        })

        cash_am_ids = self.env['account.move'].search(
            [('journal_id', 'in', [self.tax_cash_basis_journal_id.id,
                                   self.curr_ex_journal_id.id])])

        self.assertEquals(
            len(cash_am_ids), 0, 'There should be no journal entry')

        invoice_date = self.today - timedelta(days=1)
        invoice_id = self.create_invoice(
            inv_type='in_invoice',
            currency_id=self.mxn.id,
        )
        invoice_id.write({'date_invoice': invoice_date.strftime('%Y-%m-%d')})
        invoice_id.refresh()
        invoice_id.compute_taxes()
        invoice_id.action_invoice_open()

        self.create_payment(
            invoice_id, self.today, invoice_id.amount_total,
            self.bank_journal_mxn, self.mxn)

        cash_am_ids = self.env['account.move'].search(
            [('journal_id', 'in', [self.tax_cash_basis_journal_id.id,
                                   self.curr_ex_journal_id.id])])

        self.assertEquals(
            len(cash_am_ids), 2, 'There should be Two journal entry')

        invoice_id.mapped('move_id.line_ids').sudo().remove_move_reconcile()

        cash_am_ids = self.env['account.move'].search(
            [('journal_id', 'in', [self.tax_cash_basis_journal_id.id,
                                   self.curr_ex_journal_id.id])])

        self.assertEquals(
            len(cash_am_ids), 4, 'There should be Two journal entry')
