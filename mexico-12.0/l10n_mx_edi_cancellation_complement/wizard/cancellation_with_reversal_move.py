from odoo import models, fields, api


class PaymentCancellationWithReversalMove(models.TransientModel):
    """ Wizard to set the necessary information
    to create the reversal move of the payment
    """
    _name = 'l10n_mx_edi.payment_cancellation_with_reversal_move'
    _description = 'Wizard for Payment cancellation with reversal move'

    date = fields.Date(
        string='Reversal date', default=fields.Date.context_today,
        required=True, help="Date of the reversal move")
    journal_id = fields.Many2one(
        'account.journal', string='Use Specific Journal',
        help='If empty, uses the journal of the journal entry to be reversed.')

    @api.multi
    def cancel_with_reversal_move(self):
        payment_ids = self._context.get('active_ids', False)
        self.env['account.payment'].browse(
            payment_ids).l10n_mx_edi_cancel_with_reversal(
                self.date, self.journal_id)
        return {'type': 'ir.actions.act_window_close'}
