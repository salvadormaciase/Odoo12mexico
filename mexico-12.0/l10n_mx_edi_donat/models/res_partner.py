
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_donations = fields.Boolean(
        'Need donations?',
        help='Use this field when the invoice require the complement to '
        '"Donations". This value will be used to indicate the use of the '
        'information from the document that authorize to receive '
        'deductible donations, granted by SAT')
