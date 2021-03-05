# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_edi_customs_partner_id = fields.Many2one(
        'res.partner', 'Customs Partner',
        help='This partner will be used to send the tax entries for extra '
        'customs costs. Example: Tax for IGI, DTA, etc.')
