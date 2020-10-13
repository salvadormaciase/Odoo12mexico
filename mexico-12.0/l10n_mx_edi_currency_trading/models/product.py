
from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    l10n_mx_edi_ct_type = fields.Selection(
        selection=[
            ('purchase', 'Purchase'),
            ('sale', 'Sale'),
        ], string='Exchange operation type',
        help="When this product is intended to be used to trade currencies, "
        "specifies the type of operation, i.e. if it's a purchase or sale.\n"
        "If set, this field will be used to create and fill the complement's "
        "XML node into the CFDI. If this field is not set in any of the "
        "invoice products, the complement will not be used and the XML node "
        "will not be included.")
