# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class City(models.Model):
    _inherit = 'res.city'

    l10n_mx_edi_code = fields.Char(
        'Code', help='Code given by the SAT to this city')
