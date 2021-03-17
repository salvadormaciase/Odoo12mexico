
from odoo import api, models, _
from odoo.tools import date_utils
import io
import zipfile
import base64


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def l10n_mx_edi_action_reinvoice(self):
        """Allows generating a new invoice with the current date from the
        customer portal."""
        mx_date = self.env[
            'l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date()
        ctx = {'disable_after_commit': True}
        for invoice in self.filtered(lambda inv: inv.state != 'draft'):
            if mx_date <= date_utils.end_of(invoice.date_invoice, 'month'):
                # Get the credit move line to reconcile with a new invoice
                payment_move_lines = invoice.payment_move_line_ids
                invoice.action_invoice_cancel()
                invoice.refresh()
                invoice.action_invoice_draft()
                invoice.write({
                    'date_invoice': mx_date.strftime("%Y-%m-%d")
                })
                invoice.refresh()
                invoice.with_context(**ctx).action_invoice_open()
                invoice.refresh()
                # Now reconcile the payment
                if payment_move_lines:
                    invoice.register_payment(payment_move_lines)
                continue

            # Case B: Create a new invoice and pay with a Credit Note
            # Create a Credit Note from old invoice
            refund_invoice = invoice.refund(
                date_invoice=mx_date, date=mx_date,
                description=_('Re-invoiced from %s') % invoice.number,
                journal_id=invoice.journal_id.id)
            refund_invoice.action_invoice_open()
            # Get the credit move line to reconcile with a new invoice
            refund_move_line = refund_invoice.move_id.line_ids.filtered(
                'credit')
            # Create a new invoice
            new_invoice = invoice.copy({'date_invoice': mx_date})
            new_invoice.action_invoice_open()
            # Now reconcile the the new invoice with the credit note
            new_invoice.assign_outstanding_credit(refund_move_line.id)

    def get_cfdi_att(self, attachment_type):
        attachment_name = self.l10n_mx_edi_cfdi_name.replace('.xml', attachment_type)
        domain = [
            ('res_id', '=', self.id),
            ('res_model', '=', self._name),
            ('name', '=', attachment_name)]
        return self.env['ir.attachment'].search(domain, limit=1)

    def _get_zipped_cfdi(self):
        xml_attachments = self.l10n_mx_edi_retrieve_attachments()
        zip_ids = self.get_cfdi_att(attachment_type='.zip')
        for record in zip_ids:
            if record.mimetype == 'application/zip':
                return record
        pdf_attachment = self.get_cfdi_att(attachment_type='.pdf')
        xml_attachment = xml_attachments and xml_attachments[0]
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as zipped_invoice:
            if xml_attachment:
                zipped_invoice.writestr(xml_attachment.name, base64.b64decode(xml_attachment.datas))
            if pdf_attachment:
                zipped_invoice.writestr(pdf_attachment.name, base64.b64decode(pdf_attachment.datas))
            if xml_attachment and pdf_attachment:
                zip_name = xml_attachment.name.replace('.xml', '.zip')
            elif xml_attachment:
                zip_name = xml_attachment.name.replace('.xml', '.zip')
            elif pdf_attachment:
                zip_name = self.l10n_mx_edi_cfdi_name.replace('.xml', '.zip')
            zipped_invoice.close()
            values = {
                'name': zip_name,
                'type': 'binary',
                'mimetype': 'application/zip',
                'public': False,
                'datas_fname': zip_name,
                'res_id': pdf_attachment.res_id,
                'res_model': 'account.invoice',
                'datas': base64.b64encode(zip_stream.getvalue()),
            }
        attachment = self.env['ir.attachment'].create(values)
        return attachment
