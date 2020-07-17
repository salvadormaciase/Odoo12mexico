from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_cancellation_with_reversal_customer = fields.Boolean(
        related='company_id.l10n_mx_cancellation_with_reversal_customer',
        readonly=False, help='Enable the cancellation of payments from '
        'previous periods with reversal entries (For Customer).')
    l10n_mx_cancellation_with_reversal_supplier = fields.Boolean(
        related='company_id.l10n_mx_cancellation_with_reversal_supplier',
        readonly=False, help='Enable the cancellation of payments from '
        'previous periods with reversal entries (For Supplier).')
