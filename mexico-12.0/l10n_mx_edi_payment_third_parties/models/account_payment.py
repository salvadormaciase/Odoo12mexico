# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def _get_cfdi_third_part(self):
        return self.invoice_ids.filtered(
            lambda inv: inv.l10n_mx_edi_cfdi_supplier_rfc != inv.company_id.vat)  # noqa

    @api.multi
    def _l10n_mx_edi_get_total_third_part(self):
        invoice = self._get_cfdi_third_part()
        amount = [p for p in invoice._get_payments_vals() if (p.get(
            'account_payment_id', False) == self.id or not p.get(
                'account_payment_id') and (not p.get('invoice_id') or p.get(
                    'invoice_id') == invoice.id))]
        amount_payment = sum([data.get('amount', 0.0) for data in amount])
        return self.amount - amount_payment
