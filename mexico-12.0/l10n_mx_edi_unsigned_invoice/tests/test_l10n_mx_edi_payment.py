from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiPayment(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiPayment, self).setUp()
        self.product = self.env.ref("product.product_product_6")
        self.product.taxes_id = [self.tax_positive.id, self.tax_negative.id]
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)

    def test_invoice_not_signed(self):
        """Post a payment in a not signed invoice"""
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        self.assertNotEqual(invoice.l10n_mx_edi_pac_status, "signed")
        date_mx = self.env[
            'l10n_mx_edi.certificate'].sudo().get_mx_current_datetime()
        ctx = {'active_model': 'account.invoice', 'active_ids': [invoice.id]}
        register_payments = self.env['account.register.payments'].with_context(
            ctx).create({
                'payment_date': date_mx,
                'l10n_mx_edi_payment_method_id': self.env.ref(
                    'l10n_mx_edi.payment_method_efectivo').id,
                'payment_method_id': self.env.ref(
                    "account.account_payment_method_manual_in").id,
                'journal_id': self.bank_journal.id,
                'communication': invoice.number,
                'amount': invoice.amount_total, })
        payment = register_payments.create_payments()
        payment = self.env['account.payment'].search(payment.get('domain', []))
        self.assertNotEqual(payment.l10n_mx_edi_pac_status, "signed")
