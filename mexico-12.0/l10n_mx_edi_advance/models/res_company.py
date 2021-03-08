
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_product_advance_id = fields.Many2one(
        'product.product', 'Advance product', help='This product will be used '
        'in the advance invoices that are created automatically when is '
        'registered a payment without documents related or with a difference '
        'in favor of the customer.')
    l10n_mx_edi_advance = fields.Selection([
        ('A', 'Invoicing by applying advance with acquittal CFDI'),
        ('B', 'Invoicing by applying an advance with the remaining of pending duties'),  # noqa
        ], 'Process for Advances', help='Process to be used in the advance '
        'generation. Based on the GuiaAnexo20 Document.', default='A')
