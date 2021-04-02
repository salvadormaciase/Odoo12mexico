# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10nMXEdiIeduCodes(models.Model):
    _name = 'l10n_mx_edi_iedu.codes'
    _description = """Educational Level Codes"""

    journal_id = fields.Many2one('account.journal', 'Journal')
    l10n_mx_edi_iedu_education_level_id = fields.Many2one(
        'res.partner.category', string='Education Level',
        help='Education Level')
    l10n_mx_edi_iedu_code = fields.Char(
        string='Code', help='Education Level Code')
