# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _


def create_list_html(array):
    """Convert an array of string to a html list."""
    if not array:
        return ''
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _create_payment_entry(self, amount):
        is_required = self.l10n_mx_edi_advance_is_required(amount)
        if is_required:
            self._l10n_mx_edi_generate_advance(is_required)
        return super(AccountPayment, self)._create_payment_entry(amount)

    def l10n_mx_edi_advance_is_required(self, amount):
        """Verify that the configuration necessary to create the advance
        invoice is complete.
        TODO: Dear future me, propose a clean PR to avoid amount as parameter
        and use a computed field instead."""
        self.ensure_one()
        # First check if i need at least to check the payment to be an advance
        if (self.payment_type != 'inbound' or (
            self.invoice_ids and self.payment_difference >= 0) or
                self.company_id.country_id != self.env.ref('base.mx')):
            return False
        messages = []
        company = self.company_id
        if not company.l10n_mx_edi_product_advance_id:
            messages.append(_(
                'The product that must be used in the advance invoice line '
                'is not configured in the accounting settings.'))

        aml = self.env['account.move.line'].with_context(
            check_move_validity=False, date=self.payment_date)
        debit, credit, _amount_currency, _currency_id = \
            aml._compute_amount_fields(
                amount, self.currency_id, self.company_id.currency_id)
        partner = self.partner_id._find_accounting_partner(self.partner_id)
        lines = self.env['account.move.line'].read_group([
            ('partner_id', '=', partner.id),
            ('account_id', '=', partner.property_account_receivable_id.id),
            ('move_id.state', '=', 'posted')],
            ['debit', 'credit'], 'partner_id')
        debt = company.currency_id.round(
            lines[0]['debit'] + debit -
            (lines[0]['credit'] + credit)) if lines else 0.0
        if debt > 0:
            messages.append(_(
                'This payment do not generate advance because the customer '
                'has invoices with pending payment.'))
        if not messages:
            return self.payment_difference or debt or amount
        self.message_post(body=_(
            'This record cannot create the advance document automatically '
            'for the next reason: %sFor this record, you '
            'need create the invoice manually and reconcile it with this '
            'payment or cancel and validate again after that the data was '
            'completed.') % (create_list_html(messages)))
        return False

    def _l10n_mx_edi_generate_advance(self, amount):
        """Return if with the payment must be created the invoice for the
        advance"""
        advance = self.env['account.invoice'].advance(
            self.env['res.partner']._find_accounting_partner(self.partner_id),
            abs(amount), self.currency_id)
        advance.message_post_with_view(
            'mail.message_origin_link',
            values={'self': advance, 'origin': self},
            subtype_id=self.env.ref('mail.mt_note').id)
        self.message_post_with_view(
            'l10n_mx_edi_advance.l10n_mx_edi_message_advance_created',
            values={'self': self, 'origin': advance},
            subtype_id=self.env.ref('mail.mt_note').id)
        advance.date_invoice = self.payment_date
        ctx = {'disable_after_commit': True}
        advance.with_context(**ctx).action_invoice_open()
        if advance.l10n_mx_edi_pac_status == 'signed':
            self.invoice_ids = [(4, advance.id)]
            advance._compute_cfdi_values()  # avoid inv signed with uuid false
            return advance
        self.message_post_with_view(
            'l10n_mx_edi_advance.l10n_mx_edi_message_advance',
            values={'self': self, 'origin': advance},
            subtype_id=self.env.ref('mail.mt_note').id)
        advance.action_invoice_cancel()
        advance.action_invoice_draft()
        return advance
