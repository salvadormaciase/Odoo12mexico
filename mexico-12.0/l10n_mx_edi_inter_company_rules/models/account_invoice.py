from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        records = self.env[self._name]
        records_so = self.env[self._name]
        for invoice in self.filtered(lambda i: i.type in ['out_invoice', 'out_refund']):
            company = self.env['res.company']._find_company_from_partner(invoice.partner_id.id)
            if not company or company.rule_type not in ('invoice_and_refund', 'so_and_po'):
                continue
            if company.rule_type == 'invoice_and_refund' and not invoice.auto_generated:
                records += invoice
                continue
            records_so += invoice
        if not records + records_so:
            return super(AccountInvoice, self).invoice_validate()
        result = super(AccountInvoice, self.with_context(disable_after_commit=True)).invoice_validate()
        for invoice in records:
            related = self.sudo().search([('auto_invoice_id', '=', invoice.id)])
            if not related:
                continue
            filename = ('%s-%s-MX-Invoice-%s.xml' % (
                related.journal_id.code, related.reference or '', company.vat or '')).replace('/', '')
            related.l10n_mx_edi_cfdi_name = filename
            invoice.l10n_mx_edi_retrieve_last_attachment().sudo().copy({
                'res_id': related.id,
                'name': filename,
            })
        for invoice in records_so:
            sale = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')
            if not sale:
                continue
            related = self.env['purchase.order'].sudo().search([('auto_sale_order_id', '=', sale.id)])
            if not related:
                continue
            bill = related.invoice_ids
            if bill:
                filename = ('%s-%s-MX-Invoice-%s.xml' % (
                    bill.journal_id.code, bill.reference or '', bill.company_id.vat or '')).replace('/', '')
                bill.l10n_mx_edi_cfdi_name = filename
                invoice.l10n_mx_edi_retrieve_last_attachment().sudo().copy({
                    'res_id': bill.id,
                    'name': filename,
                })
                continue
            invoice.l10n_mx_edi_retrieve_last_attachment().sudo().copy({
                'res_id': related.id,
                'res_model': 'purchase.order'
            })
        return result
