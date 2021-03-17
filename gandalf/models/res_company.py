from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    account_realization_journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help='Journal where realization entries for Accounts will be booked')
    invoice_realization_journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help='Journal where realization entries for Invoices will be booked')
    account_realization_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        help='Maps accounts in the Revaluation Ledger Items for Accounts')
    invoice_realization_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        help='Maps accounts in the Revaluation Ledger Items for Invoices')
    create_realization_entry_on_accounts = fields.Boolean(
        help='If True a Realization Entry will be created on Accounts')
    create_realization_entry_on_invoices = fields.Boolean(
        help='If True a Realization Entry will be created on Invoices')
    apply_only_on_receivable_payable = fields.Boolean(
        help='If True only invoices with Receivables/Payables will be taken')
