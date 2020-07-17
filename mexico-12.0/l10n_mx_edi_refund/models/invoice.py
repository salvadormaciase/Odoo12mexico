# -*- coding: utf-8 -*-

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        """ Prepare the dict of values to create the new credit note from
        the invoice. Method inherit for to add the fields:
        l10n_mx_edi_payment_method_id, l10n_mx_edi_usage, payment_term_id
        """
        values = super()._prepare_refund(
            invoice, date_invoice, date, description, journal_id)
        if not invoice.l10n_mx_edi_cfdi_uuid:
            return values
        payment_inmediate = self.env.ref(
            'account.account_payment_term_immediate', raise_if_not_found=False)
        payment_refund = self._context.get(
            'payment_refund') or invoice.l10n_mx_edi_payment_method_id.id
        usage_refund = self._context.get('usage_refund') or 'P01'
        values.update({
            'payment_term_id': payment_inmediate.id,
            'date_due': invoice.date_invoice,
            'l10n_mx_edi_payment_method_id': payment_refund,
            'l10n_mx_edi_usage': usage_refund})
        return values

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None,
               journal_id=None):
        """ Modified value the new credit note from the wizard.
        Method inherit for to modify the field: l10n_mx_edi_origin
        """
        refund_invoices = super().refund(
            date_invoice, date, description, journal_id)
        origin_refund = self._context.get('origin_refund') or '01'
        for refund_inv in refund_invoices.filtered(
                lambda r: r.refund_invoice_id.l10n_mx_edi_cfdi_uuid):
            related = refund_inv.get_cfdi_related()
            uuid = [] if origin_refund == related.get('type') else [
                refund_inv.refund_invoice_id.l10n_mx_edi_cfdi_uuid]
            refund_inv._set_cfdi_origin(origin_refund, uuid)
        return refund_invoices
