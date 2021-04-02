# Copyright 2020 Vauxoo

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_in_blocklist = fields.Selection([
        ('normal', 'No information'),
        ('done', 'Ok'),
        ('blocked', 'Blocked'),
    ],
        string="Partner State",
        help="This field is set as 'Blocked' if the partner is in the "
        "Definitive list published buy the SAT, 'Ok' if the partner is not in "
        "the list or 'No information' if the partner has not being consulted "
        "yet.",
        default="normal",
        copy=False,
    )
