
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_donat_auth = fields.Char(
        'Authorization Number', help='Number of document on which is '
        'informed the civil organization or escrow, the procedence of the '
        'authorization to receive deductible donations, or its corresponding '
        'renovation granted by SAT')
    l10n_mx_edi_donat_date = fields.Date(
        'Authorization Date', help='Date of document on which is '
        'informed the civil organization or escrow, the procedence of the '
        'authorization to receive deductible donations, or its corresponding '
        'renovation granted by SAT')
    l10n_mx_edi_donat_note = fields.Text(
        'Note', help='Field to prove the voucher issued is derived '
        'from a donation')
