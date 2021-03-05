from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    realization_invoice_id = fields.Many2one(
        'account.move',
        readonly=True,
        help="Invoice for which this Realization has being made")
    realization_account_id = fields.Many2one(
        'account.account',
        readonly=True,
        help="Account for which this Realization has being made")
