# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    l10n_mx_edi_3rd_party_id = fields.Many2one(
        'res.partner', string='On Behalf of',
        help="If this product is being sold on behalf of a 3rd party, "
        "specifies who the sale is on behalf of.\n"
        "If set, the complement 3rd party will be used and the node "
        "will be filled according to the value set on this field.")
    # TODO: create logic to add more than one date per customs
    l10n_mx_edi_customs_date = fields.Date(
        string='Customs Expedition Date', copy=False,
        help="If this is an imported good, specifies the expedition date of "
        "the customs document that covers the importation of the good.")
    l10n_mx_edi_customs_name = fields.Char(
        string="Customs Office", copy=False,
        help="If this is an imported good, specifies the customs office by "
        "which the importation of the good was made.")
