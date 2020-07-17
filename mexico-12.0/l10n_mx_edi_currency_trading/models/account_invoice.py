# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.constrains('state')
    def _check_only_one_ct_type(self):
        for invoice in self.filtered(lambda r: r.state == 'open'):
            fld = 'invoice_line_ids.product_id.l10n_mx_edi_ct_type'
            ct_types = set(invoice.mapped(fld)) - {False}
            if len(ct_types) > 1:
                raise ValidationError(_(
                    "This invoice contains products with different exchange "
                    "operation types.\n"
                    "It is not possible to bill currency purchases and sales "
                    "within the same invoice."))
