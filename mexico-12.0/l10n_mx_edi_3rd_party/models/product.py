# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    l10n_mx_edi_property_tax = fields.Char(
        string='Property Taxes Account', copy=False,
        help="If this product is a lease, specifies the property taxes "
        "account which the property was registered with, in the cadastral "
        "system of the state.\n"
        "If this field is set and the 3rd party complement is used for this "
        "product, an extra sub-node will be included in the CFDI into te "
        "complement node, specifying the property taxes account.")
