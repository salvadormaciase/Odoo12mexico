from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_factoring_id = fields.Many2one(
        "res.partner", "Financial Factor", copy=False, readonly=True,
        states={'open': [('readonly', False)]},
        help="This invoice will be paid by this Financial factoring agent.")
