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
        move_obj = self.env['account.move']

        partial_to_unlink = mxn_moves

        # let us fetch the full reconciliation from the partial reconciliation
        afr_ids = mxn_moves.mapped('full_reconcile_id')
        # include deletion of exchange rate journal entries
        fx_move_ids = afr_ids.mapped('exchange_move_id')
        fx_apr_ids = fx_move_ids.mapped('line_ids.matched_debit_ids')
        fx_apr_ids |= fx_move_ids.mapped('line_ids.matched_credit_ids')
        # delete the tax basis move created at the reconciliation time by the FX moves
        caba_fx_move_ids = move_obj.search([('tax_cash_basis_rec_id', 'in', fx_apr_ids.ids)])
        caba_fx_apr_ids = caba_fx_move_ids.mapped('line_ids.matched_debit_ids')
        caba_fx_apr_ids |= caba_fx_move_ids.mapped('line_ids.matched_credit_ids')
        caba_fx_afr_ids = caba_fx_move_ids.mapped('line_ids.full_reconcile_id')
        fx_caba_fx_move_ids = caba_fx_afr_ids.mapped('exchange_move_id')
        fx_caba_fx_apr_ids = fx_caba_fx_move_ids.mapped('line_ids.matched_debit_ids')
        fx_caba_fx_apr_ids |= fx_caba_fx_move_ids.mapped('line_ids.matched_credit_ids')

        # delete the tax basis move created at the reconciliation time
        caba_move_ids = move_obj.search([('tax_cash_basis_rec_id', 'in', partial_to_unlink.ids)])
        # Journal entries from tax cash might include reconciliations
        caba_afr_ids = caba_move_ids.mapped('line_ids.full_reconcile_id')
        caba_apr_ids = caba_move_ids.mapped('line_ids.matched_debit_ids')
        caba_apr_ids |= caba_move_ids.mapped('line_ids.matched_credit_ids')

        fx_caba_move_ids = caba_afr_ids.mapped('exchange_move_id')
        fx_caba_apr_ids = fx_caba_move_ids.mapped('line_ids.matched_debit_ids')
        fx_caba_apr_ids |= fx_caba_move_ids.mapped('line_ids.matched_credit_ids')

        # stitch together all the full reconcile records
        full_to_unlink = afr_ids | caba_fx_afr_ids | caba_afr_ids
        full_to_unlink.unlink()
        # stitch together all the partial reconcile records
        partial_to_unlink |= fx_apr_ids | caba_fx_apr_ids | fx_caba_fx_apr_ids | caba_apr_ids | fx_caba_apr_ids
        res = super(models.Model, partial_to_unlink).unlink()
        # stitch together all the caba and fx moves
        move_ids = fx_move_ids | caba_fx_move_ids | fx_caba_fx_move_ids | caba_move_ids | fx_caba_move_ids
        move_ids.button_cancel()
        move_ids.unlink()
        return res
