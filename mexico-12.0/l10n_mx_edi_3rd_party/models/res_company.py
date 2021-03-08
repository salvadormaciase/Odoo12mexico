# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_locality_id = fields.Many2one(
        'l10n_mx_edi.res.locality', string='Locality',
        related='partner_id.l10n_mx_edi_locality_id',
        help='Municipality configured for this company')
