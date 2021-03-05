# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_mx_edi_customs_patent = fields.Char(
        'Customs Patent', help='If this partner is a broker, specific the '
        'patent number. Will be used to assign automatically the broker in '
        'the customs.')
