
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_complement_type = fields.Selection(
        selection=[
            ('destruction', 'Destruction Certificate'),
            ('renew', 'Vehicle Renew and Substitution'),
            ('sale', 'Sale of vehicles'),
            ('pfic', 'Natural person member of the coordinated')
        ],
        string='Vehicle Complement',
        help='Select one of those complements if you want it to be available '
        'for invoice')
