# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _l10n_mx_get_cash_basis(self):
        """Currently, the accounting entry for the VAT effectively paid
        is generated independently of the invoice and the generated payment.
        With this method it obtain the accounting entry mentioned above.
        """
        am_obj = self.env['account.move']
        caba_res = {}
        for inv in self.filtered(lambda i: i.move_id):
            line = inv.move_id.line_ids.filtered(
                lambda x: x.account_id == inv.account_id)
            matched_ids = line.mapped('matched_debit_ids') | line.mapped(
                'matched_credit_ids')
            if not matched_ids:
                continue
            caba_res[inv.id] = am_obj.search([
                ('tax_cash_basis_rec_id', 'in', matched_ids.ids)])
        return caba_res
