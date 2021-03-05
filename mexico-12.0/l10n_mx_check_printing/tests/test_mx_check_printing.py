import time
from openerp.addons.account.tests.account_test_classes import AccountingTestCase  # noqa


class TestMXCheckPrinting(AccountingTestCase):

    def setUp(self):
        super(TestMXCheckPrinting, self).setUp()
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.register_payments_model = self.env['account.register.payments']

        self.partner_jackson = self.env.ref("base.res_partner_10")
        self.product = self.env.ref("product.product_product_4")
        self.payment_method_check = self.env.ref(
            "account_check_printing.account_payment_method_check")
        self.bank_journal = self.env['account.journal'].create(
            {'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})
        self.bank_journal.check_manual_sequencing = True
        self.bank_journal.mx_check_layout = "l10n_mx_check_printing.action_print_check_bbva_bancomer" # noqa
        self.account_payable = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_payable').id)], limit=1)
        self.account_expenses = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id)], limit=1)

    def create_invoice(self, amount=100):
        invoice = self.invoice_model.create({
            'partner_id': self.partner_jackson.id,
            'name': "Supplier Invoice",
            'type': "in_invoice",
            'account_id': self.account_payable.id,
            'date_invoice': time.strftime('%Y') + '-06-26',
        })
        self.invoice_line_model.create({
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': self.account_expenses.id,
        })
        invoice.action_invoice_open()
        return invoice

    def create_payment(self, invoices):
        register_payments = self.register_payments_model.with_context({
            'active_model': 'account.invoice',
            'active_ids': invoices.ids
        }).create({
            'payment_date': time.strftime('%Y') + '-07-15',
            'journal_id': self.bank_journal.id,
            'payment_method_id': self.payment_method_check.id,
        })
        register_payments.create_payments()
        return self.env['account.payment'].search([], order="id desc", limit=1)

    def test_print_check(self):
        invoice = self.create_invoice()
        payment = self.create_payment(invoice)

        payment.print_checks()
        self.assertEqual(payment.state, 'sent')
