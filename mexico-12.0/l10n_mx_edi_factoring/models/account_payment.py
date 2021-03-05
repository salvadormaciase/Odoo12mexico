from odoo import models, api, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    l10n_mx_edi_factoring_id = fields.Many2one(
        "res.partner", "Financial Factor", copy=False,
        help="This payment was received from this factoring.")

    @api.model
    def default_get(self, fields_list):
        rec = super(AccountPayment, self).default_get(fields_list)
        invoice_defaults = self.resolve_2many_commands(
            'invoice_ids', rec.get('invoice_ids'))
        if not invoice_defaults and len(invoice_defaults) != 1:
            return rec
        invoice = self.env['account.invoice'].browse(invoice_defaults[0]['id'])
        if not invoice.l10n_mx_edi_is_required():
            return rec
        # If come from an unique invoice nothing to special to set,
        # the factoring will be the one in the partner if set.
        factoring = invoice.l10n_mx_edi_factoring_id
        if not factoring and rec.get('partner_id'):
            factoring = self.env['res.partner'].browse(rec.get(
                'partner_id')).l10n_mx_edi_factoring_id
        rec['l10n_mx_edi_factoring_id'] = factoring.id
        return rec

    @api.multi
    def post(self):
        """Assign the factoring in the invoices related"""
        for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            record.invoice_ids.write({
                'l10n_mx_edi_factoring_id': record.l10n_mx_edi_factoring_id.id,
            })
        return super(AccountPayment, self).post()


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    l10n_mx_edi_factoring_id = fields.Many2one(
        "res.partner", "Financial Factor", copy=False,
        help="This payment was received from this factoring.")

    @api.model
    def default_get(self, fields_list):
        rec = super(AccountRegisterPayments, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        model = self._context.get('active_model')
        if model != 'account.invoice' or not active_ids:
            return rec
        # If come from an unique invoice nothing to special to set,
        # the factoring will be the one in the partner if set.
        invoice = self.env['account.invoice'].browse(active_ids)
        if not invoice.filtered(lambda i: i.l10n_mx_edi_is_required()):
            return rec
        factoring = invoice.mapped('l10n_mx_edi_factoring_id').ids
        if not factoring and rec.get('partner_id'):
            factoring = self.env['res.partner'].browse(rec.get(
                'partner_id')).l10n_mx_edi_factoring_id.ids
        rec['l10n_mx_edi_factoring_id'] = factoring[0] if factoring else ''
        return rec

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(
            invoices)
        res['l10n_mx_edi_factoring_id'] = self.l10n_mx_edi_factoring_id.id
        return res
