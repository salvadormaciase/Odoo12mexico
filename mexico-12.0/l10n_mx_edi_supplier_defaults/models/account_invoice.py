from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        self.l10n_mx_edi_payment_method_id = self.purchase_id.l10n_mx_edi_payment_method_id  # noqa
        self.l10n_mx_edi_usage = self.purchase_id.l10n_mx_edi_usage
        return super(AccountInvoice, self).purchase_order_change()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.env.context.get('from_purchase_order_change'):
            return res
        self.l10n_mx_edi_payment_method_id = self.partner_id.l10n_mx_edi_supplier_payment_method_id  # noqa
        self.l10n_mx_edi_usage = self.partner_id.l10n_mx_edi_supplier_usage
        return res
