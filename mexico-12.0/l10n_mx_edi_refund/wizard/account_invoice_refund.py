# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Way',
        help='Indicates the way the invoice was/will be paid, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc. Leave empty '
        'if unkown and the XML will show "Unidentified".',
        default=lambda self: self.env.ref('l10n_mx_edi.payment_method_otros',
                                          raise_if_not_found=False))

    def _get_usage_selection(self):
        return self.env['account.invoice'].fields_get().get(
            'l10n_mx_edi_usage').get('selection')

    l10n_mx_edi_usage = fields.Selection(
        _get_usage_selection, 'Usage', default='P01',
        help='Used in CFDI 3.3 to express the key to the usage that will '
        'gives the receiver to this invoice. This value is defined by the '
        'customer. \nNote: It is not cause for cancellation if the key set is '
        'not the usage that will give the receiver of the document.')

    l10n_mx_edi_origin_type = fields.Selection([
        ('01', 'Nota de crédito'),
        ('02', 'Nota de débito de los documentos relacionados'),
        ('03', 'Devolución de mercancía sobre facturas o traslados previos'),
        ('04', 'Sustitución de los CFDI previos'),
        ('07', 'CFDI por aplicación de anticipo'),
    ], 'CFDI Origin Type', default='01',
        help='In some cases like payments, credit notes, debit notes, '
        'invoices re-signed or invoices that are redone due to payment in '
        'advance will need a new origin type.')

    @api.onchange('filter_refund')
    def _onchange_filter_refund(self):
        method = self.filter_refund
        self.l10n_mx_edi_origin_type = '03' if method == 'cancel' else '01'
        self.l10n_mx_edi_usage = 'G02' if method != 'refund' else 'P01'

    @api.multi
    def compute_refund(self, mode='refund'):
        ctx = dict(
            self._context, method=mode,
            payment_refund=self.read(['l10n_mx_edi_payment_method_id'])[0][
                'l10n_mx_edi_payment_method_id'][0],
            usage_refund=self.read([
                'l10n_mx_edi_usage'])[0]['l10n_mx_edi_usage'],
            origin_refund=self.read(['l10n_mx_edi_origin_type'])[0][
                'l10n_mx_edi_origin_type'])
        res = super(AccountInvoiceRefund, self.with_context(
            ctx)).compute_refund(mode)
        return res
