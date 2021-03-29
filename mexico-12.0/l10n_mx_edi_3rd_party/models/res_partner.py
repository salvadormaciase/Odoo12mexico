# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_locality_id = fields.Many2one(
        'l10n_mx_edi.res.locality', string='Locality',
        help='Optional attribute used in the XML which defines the locality '
        'of the given location')

    @api.onchange('l10n_mx_edi_locality_id')
    def _onchange_l10n_mx_edi_locality_id(self):
        self.l10n_mx_edi_locality = self.l10n_mx_edi_locality_id.name
