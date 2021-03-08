from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        values = super()._l10n_mx_edi_create_cfdi_values()
        if self.company_id.partner_id.commercial_partner_id != self.partner_id.commercial_partner_id:  # noqa
            return values
        values['document_type'] = 'T'
        values['payment_policy'] = None
        values['taxes']['transferred'] = None
        values['taxes']['withholding'] = None
        values['amount_discount'] = None
        values['amount_untaxed'] = values['amount_untaxed'] if self.amount_total else '0'  # noqa
        values['total_discount'] = lambda l, d: False
        # NumRegIdTrib equal to None if Emisor == Receptor (CFDI type == T)
        values['receiver_reg_trib'] = None
        return values

    @api.model
    def _anglo_saxon_sale_move_lines(self, i_line):
        """If it is a 'traslado' invoice then skip inventory account moves"""
        if (self.company_id.partner_id.commercial_partner_id ==
                self.partner_id.commercial_partner_id and
                self.l10n_mx_edi_is_required()):
            return []
        return super()._anglo_saxon_sale_move_lines(i_line)
