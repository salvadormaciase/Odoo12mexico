from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_factoring_id = fields.Many2one(
        "res.partner", "Financial Factor", copy=False,
        help="This partner is allowed to receive payments with a financial"
        " factoring, if set the factoring will be proposed by default when"
        " receive a payment. In case the rights to collect this invoice "
        "are relinquished to this Partner. Payment Complement will be issued"
        "on his/her/its name, if not set payments will belong to the proper "
        "partner as usual.")
    l10n_mx_edi_factoring = fields.Boolean(
        'Factoring',
        help="Used to identify if this partner is a factoring")
