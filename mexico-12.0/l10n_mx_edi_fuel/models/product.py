from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_mx_edi_fuel_billing = fields.Boolean(
        string="Need fuel billing?",
        help="Add complements for fuel consumption when invoicing this "
        "product")
