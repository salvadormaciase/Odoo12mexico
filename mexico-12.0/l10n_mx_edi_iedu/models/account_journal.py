# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_mx_edi_iedu_code_ids = fields.One2many(
        'l10n_mx_edi_iedu.codes', 'journal_id', string="Education levels",
        help="All educational levels and their codes must be configured in "
        "this field.")
