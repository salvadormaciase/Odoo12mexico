from datetime import timedelta
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestAccountPaymentReversal(InvoiceTransactionCase):
    def setUp(self):
        super(TestAccountPaymentReversal, self).setUp()
        self.journal = self.env['account.journal']
        self.register_payments_model = self.env['account.register.payments']
        self.payment_model = self.env['account.payment']
        self.payment_method_manual_out = self.env.ref(
            "account.account_payment_method_manual_out")
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.company.l10n_mx_cancellation_with_reversal_customer = True
        self.env.ref('l10n_mx_edi_cancellation_complement.allow_cancel_with_reversal_move').sudo().write({
            'users': [(4, self.env.user.id)]})

    def test_l10n_mx_edi_account_payment(self):
        journal = self.journal.search([('type', '=', 'bank')], limit=1)
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        ctx = {'active_model': 'account.invoice', 'active_ids': [invoice.id]}
        register_payments = self.register_payments_model.with_context(ctx).create({
            'payment_date': invoice.date_invoice - timedelta(days=40),
            'l10n_mx_edi_payment_method_id': self.payment_method_cash.id,
            'payment_method_id': self.payment_method_manual_out.id,
            'journal_id': journal.id,
            'communication': invoice.number,
            'amount': invoice.amount_total,
        })

        # First payment
        payment = register_payments.create_payments()
        payment = self.payment_model.search(payment.get('domain', []))
        self.assertEqual(
            payment.l10n_mx_edi_pac_status, 'signed', payment.message_ids.mapped('body'))
        self.company.period_lock_date = invoice.date_invoice
        payment.cancel()
        self.env['l10n_mx_edi.payment_cancellation_with_reversal_move'].with_context(
            active_ids=payment.ids, l10n_mx_edi_manual_reconciliation=False).create({}).cancel_with_reversal_move()
        self.assertEqual(
            payment.state, 'posted', payment.message_ids.mapped('body'))
        self.assertEqual(
            payment.l10n_mx_edi_pac_status, 'cancelled', payment.message_ids.mapped('body'))
