
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_property_licence = fields.Char(
        'Licence Number', help='Permission number, licence or authorization '
        'of construction provided by the borrower of the partial construction '
        'services. If this is the address in construction assign here the '
        'licence number.')
