from odoo import models, fields, api, _
from odoo.exceptions import UserError


class L10nMxEdiReclassifyJournalEntries(models.TransientModel):
    _name = 'l10n_mx_edi.reclassify.journal.entries'
    _description = 'Allow reclassify the journal entries'

    account_id = fields.Many2one(
        'account.account', help="An expense account is expected")
    product_id = fields.Many2one(
        'product.product', domain=[('can_be_expensed', '=', True)],
        help="Product to assign in the expenses related")
    date = fields.Date(help="Date to assign in the expenses related")

    @api.model
    def default_get(self, fields_list):
        res = super(
            L10nMxEdiReclassifyJournalEntries, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.invoice':
            return res
        if self.env['account.invoice'].browse(active_ids).mapped(
                'type')[0] not in ['in_invoice', 'in_refund']:
            raise UserError(_(
                "You can only reclassify journal entries for vendor bills"))
        return res

    @api.multi
    def reclassify_journal_entries(self):
        model = self._context.get('active_model')
        records = self._context.get('active_ids')
        if model == 'hr.expense.sheet':
            records = self.env[model].browse(records).mapped(
                'expense_line_ids').ids
            model = 'hr.expense'
        records = self.env[model].browse(records)
        records._reclassify_journal_entries(
            self.account_id, self.product_id, self.date)
        if model == 'hr.expense':
            records.mapped(
                'l10n_mx_edi_invoice_id')._reclassify_journal_entries(
                    self.account_id, self.product_id, self.date)
        elif model == 'account.invoice':
            records.mapped(
                'l10n_mx_edi_expense_id')._reclassify_journal_entries(
                    self.account_id, self.product_id, self.date)
