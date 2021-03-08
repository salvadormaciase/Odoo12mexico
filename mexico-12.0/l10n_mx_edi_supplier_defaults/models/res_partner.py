# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    def _get_usage_selection(self):
        return self.env['account.invoice'].fields_get().get(
            'l10n_mx_edi_usage').get('selection')

    l10n_mx_edi_supplier_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method', string="Vendor Payment Way",
        help='This payment method will be used by default in purchase orders '
        'and vendor bills.', default=lambda self: self.env.ref(
            'l10n_mx_edi.payment_method_otros', raise_if_not_found=False))

    l10n_mx_edi_supplier_usage = fields.Selection(
        _get_usage_selection, 'Vendor Usage', default='P01',
        help='This usage will be used instead of the default one for purchase '
        'orders and vendor bills.')
