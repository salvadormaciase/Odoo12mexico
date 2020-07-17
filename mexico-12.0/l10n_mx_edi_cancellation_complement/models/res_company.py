from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_cancellation_with_reversal_customer = fields.Boolean(
        help='Enable the cancellation of payments from '
        'previous periods with reversal entries (For Customer).')
    l10n_mx_cancellation_with_reversal_supplier = fields.Boolean(
        help='Enable the cancellation of payments from '
        'previous periods with reversal entries (For Supplier).')
