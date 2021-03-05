# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        values = super()._l10n_mx_edi_create_cfdi_values()
        if (values['document_type'] != 'T' or
                not self.l10n_mx_edi_external_trade):
            return values
        # Transfer reason (only support '01', '02')
        related = self.get_cfdi_related()
        if related and related['type'] == '05':
            values['reason_transfer'] = '01'
        else:
            values['reason_transfer'] = '02'
        return values
