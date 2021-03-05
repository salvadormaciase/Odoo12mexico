# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def _l10n_mx_get_cash_basis(self):
        """Get cash basis entries

        Currently, the accounting entries for the VAT effectively paid
        is generated independently of the invoice and the generated payment.

        This method  returns the following entries, grouped by payment:
        - Cash basis entries of the payment
        - Exchange difference entries of the payment
        - Exchange difference entries of cash basis
        """
        am_obj = self.env['account.move']
        res = {}
        for record in self.filtered('move_line_ids'):
            # 1. Cash basis entries of the payment
            payment_moves = record.move_line_ids.mapped('move_id')
            partials = (payment_moves.mapped('line_ids.matched_debit_ids')
                        + payment_moves.mapped('line_ids.matched_credit_ids'))
            pay_caba_moves = am_obj.search([
                ('tax_cash_basis_rec_id', 'in', partials.ids)])

            # 2. Exchange difference entries of the payment
            pay_diff_moves = payment_moves.mapped(
                'line_ids.full_reconcile_id.exchange_move_id')

            # 3. Exchange difference entries of cash basis
            caba_diff_moves = pay_caba_moves.mapped(
                'line_ids.full_reconcile_id.exchange_move_id')

            # Include all three kinds of entries
            all_moves = pay_caba_moves + pay_diff_moves + caba_diff_moves
            res[record.id] = all_moves
        return res
