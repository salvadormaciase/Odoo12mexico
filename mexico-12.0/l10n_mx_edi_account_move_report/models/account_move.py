from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def l10n_mx_edi_get_uuid(self):
        cfdi = {}
        cfdi['type'] = ''
        # cash basis
        move_cb = self.mapped('tax_cash_basis_rec_id')
        move_cb = move_cb.credit_move_id | move_cb.debit_move_id
        all_move = self | move_cb.mapped('move_id')
        # Exchange difference
        full_reconcile = self.env['account.full.reconcile'].search([
            ('exchange_move_id', 'in', all_move.ids)])
        move_dff = full_reconcile.mapped('reconciled_line_ids.move_id')
        all_move |= move_dff
        # payments
        payments = all_move.mapped('line_ids.payment_id')
        if payments:
            cfdi['type'] = 'Banco'
        cfdi['all_payments'] = payments
        cfdi['payments'] = payments.filtered(lambda p: p.l10n_mx_edi_cfdi_uuid)
        # invoices
        invoices = all_move.mapped('line_ids.invoice_id')
        cfdi['invoices'] = invoices.filtered(lambda i: i.l10n_mx_edi_cfdi_uuid)
        if invoices:
            cfdi['type'] = {
                'out_invoice': 'Ingreso',
                'in_refund': 'Ingreso',
                'out_refund': 'Egreso',
                'in_invoice': 'Egreso'}.get(invoices[0].type)
        # Payment in PUE
        payment_without_cfdi = payments - cfdi['payments']
        cfdi['invoices'] |= payment_without_cfdi.mapped('invoice_ids').filtered(lambda i: i.l10n_mx_edi_cfdi_uuid)
        return cfdi
