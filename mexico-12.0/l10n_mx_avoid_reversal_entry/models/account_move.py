# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    @api.multi
    def unlink(self):
        """When removing a full reconciliation, we need to delete any eventual
        journal entry that was created to book the fluctuation of the foreign
        currency's exchange rate. """
        mxn_moves = self.mapped('reconciled_line_ids').filtered(
            lambda r: r.company_id.country_id == self.env.ref(
                'base.mx')).mapped('full_reconcile_id')
        mxn_moves.write({'exchange_move_id': False})
        return super(AccountFullReconcile, self).unlink()


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    @api.multi
    def unlink(self):
        """ When removing a partial reconciliation, also unlink its full
        reconciliation if it exists.
        This Method will un-post and delete the journal entry from the Tax Cash
        Basis
        """
        mxn_moves = self.filtered(
            lambda r: r.company_id.country_id == self.env.ref('base.mx'))
        res = super(AccountPartialReconcile, self - mxn_moves).unlink()
        if not mxn_moves:
            return res
        partial_to_unlink = mxn_moves
        full_to_unlink = mxn_moves.mapped('full_reconcile_id')
        # delete the tax basis move created at the reconciliation time
        move_ids = self.env['account.move'].search(
            [('tax_cash_basis_rec_id', 'in', partial_to_unlink.ids)])
        # Journal entries from tax cash might include reconciliations
        full_to_unlink |= move_ids.mapped('line_ids.full_reconcile_id')
        # include deletion of exchange rate journal entries
        move_ids |= full_to_unlink.mapped('exchange_move_id')
        partial_to_unlink |= move_ids.mapped('line_ids.matched_debit_ids')
        partial_to_unlink |= move_ids.mapped('line_ids.matched_credit_ids')
        full_to_unlink.unlink()
        res = super(models.Model, partial_to_unlink).unlink()
        move_ids.button_cancel()
        move_ids.unlink()
        return res
