from odoo import _, api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            if record.invoice_line_ids.filtered(lambda r: r.l10n_mx_edi_voucher_id and r.quantity != 0): # noqa
                record.message_post(
                    body=_(
                        '''<p style="color:red">The quantity in the invoice
                        lines which have an Employee has to be zero.</p>'''),
                    subtype='account.mt_invoice_validated')
                return False
        return super(AccountInvoice, self).invoice_validate()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    l10n_mx_edi_voucher_id = fields.Many2one(
        'res.partner',
        string='Employee',
        help='Employee information, set this if you want to use the Food '
        'Voucher Complement'
    )
