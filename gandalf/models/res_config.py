from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_realization_journal_id = fields.Many2one(
        related='company_id.account_realization_journal_id',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        readonly=False,
        help='Journal where realization entries for Accounts will be booked')
    invoice_realization_journal_id = fields.Many2one(
        related='company_id.invoice_realization_journal_id',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        readonly=False,
        help='Journal where realization entries for Invoices will be booked')
    account_realization_position_id = fields.Many2one(
        related='company_id.account_realization_position_id',
        comodel_name='account.fiscal.position',
        readonly=False,
        help='Maps accounts in the Revaluation Ledger Items for Accounts')
    invoice_realization_position_id = fields.Many2one(
        related='company_id.invoice_realization_position_id',
        comodel_name='account.fiscal.position',
        readonly=False,
        help='Maps accounts in the Revaluation Ledger Items for Invoices')
    create_realization_entry_on_accounts = fields.Boolean(
        related='company_id.create_realization_entry_on_accounts',
        readonly=False,
        help='If True a Realization Entry will be created on Accounts')
    create_realization_entry_on_invoices = fields.Boolean(
        related='company_id.create_realization_entry_on_invoices',
        readonly=False,
        help='If True a Realization Entry will be created on Invoices')
