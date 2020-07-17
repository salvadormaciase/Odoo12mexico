# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.tools import date_utils


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def l10n_mx_edi_action_reinvoice(self):
        """Allows generating a new invoice with the current date from the
        customer portal."""
        mx_date = self.env[
            'l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date()
        ctx = {'disable_after_commit': True}
        for invoice in self.filtered(lambda inv: inv.state != 'draft'):
            if mx_date <= date_utils.end_of(invoice.date_invoice, 'month'):
                # Get the credit move line to reconcile with a new invoice
                payment_move_lines = invoice.payment_move_line_ids
                invoice.action_invoice_cancel()
                invoice.refresh()
                invoice.action_invoice_draft()
                invoice.write({
                    'date_invoice': mx_date.strftime("%Y-%m-%d")
                })
                invoice.refresh()
                invoice.with_context(**ctx).action_invoice_open()
                invoice.refresh()
                # Now reconcile the payment
                if payment_move_lines:
                    invoice.register_payment(payment_move_lines)
                continue

            # Case B: Create a new invoice and pay with a Credit Note
            # Create a Credit Note from old invoice
            refund_invoice = invoice.refund(
                date_invoice=mx_date, date=mx_date,
                description=_('Re-invoiced from %s') % invoice.number,
                journal_id=invoice.journal_id.id)
            refund_invoice.action_invoice_open()
            # Get the credit move line to reconcile with a new invoice
            refund_move_line = refund_invoice.move_id.line_ids.filtered(
                'credit')
            # Create a new invoice
            new_invoice = invoice.copy({'date_invoice': mx_date})
            new_invoice.action_invoice_open()
            # Now reconcile the the new invoice with the credit note
            new_invoice.assign_outstanding_credit(refund_move_line.id)
