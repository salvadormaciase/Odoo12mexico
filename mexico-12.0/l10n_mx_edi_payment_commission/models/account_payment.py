from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    l10n_mx_edi_is_commission = fields.Boolean(
        help='This must be True if the amount difference is because the bank take that amount to commissions.')


class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.register.payments'

    l10n_mx_edi_is_commission = fields.Boolean(
        help='This must be True if the amount difference is because the bank take that amount to commissions.')

    @api.multi
    def _prepare_payment_vals(self, invoices):
        """Any field that is going to be passed from this model to
        account.payment needs to be added in this dictionary"""
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
        res.update({
            'l10n_mx_edi_is_commission': self.l10n_mx_edi_is_commission,
        })
        return res
