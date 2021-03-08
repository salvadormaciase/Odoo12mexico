from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_isepi = fields.Boolean(
        string='Is an Electronic purse issuer?',
        help='This add the electronic purse emission complement for fuel '
        'consumption')
