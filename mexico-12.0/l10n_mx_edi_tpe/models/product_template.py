from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_mx_edi_tpe_track = fields.Selection([
        ('airway', 'Airway'),
        ('seaway', 'Seaway'),
        ('terrestrial', 'Terrestrial'),
    ],
        string='Track',
        help='Attribute required to express if it is via Air, Maritime or '
        'Terrestrial.')
