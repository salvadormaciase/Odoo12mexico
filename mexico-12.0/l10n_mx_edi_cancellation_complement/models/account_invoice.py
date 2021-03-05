# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from suds.client import Client

from odoo import _, api, fields, models
from odoo.tools import date_utils


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_cancellation_date = fields.Date(
        'Cancellation Date', readonly=True, copy=False,
        help='Save the cancellation date of the CFDI in the SAT')
    l10n_mx_edi_cancellation_time = fields.Char(
        'Cancellation Time', readonly=True, copy=False,
        help='Save the cancellation time of the CFDI in the SAT')

    @api.multi
    def _l10n_mx_edi_finkok_cancel(self, pac_info):
        """Extend the cancel method to get the cancellation date from the
        acuse"""
        res = super(AccountInvoice, self)._l10n_mx_edi_finkok_cancel(pac_info)
        url = pac_info['url']
        username = pac_info['username']
        password = pac_info['password']
        for inv in self:
            uuid = inv.l10n_mx_edi_cfdi_uuid
            company = inv.company_id
            try:
                client = Client(url, timeout=20)
                response = client.service.get_receipt(
                    username, password, company.vat, uuid)
            except Exception as e:
                inv.l10n_mx_edi_log_error(str(e))
                continue
            if not getattr(response, 'date', None):
                continue
            date = response.date
            inv.l10n_mx_edi_cancellation_date = date.split('T')[0]
            inv.l10n_mx_edi_cancellation_time = date.split('T')[1][:8]
        return res

    @api.multi
    def action_invoice_draft(self):
        inv_mx = self.filtered(
            lambda inv: inv.company_id.country_id == self.env.ref('base.mx'))
        if not inv_mx:
            return super(AccountInvoice, self).action_invoice_draft()
        to_draft = inv_mx.filtered(
            lambda inv: inv.type in ('in_refund', 'in_invoice') or (
                not inv.move_id or not inv.move_id.reverse_entry_id))
        for inv in inv_mx - to_draft:
            inv.message_post(body=_(
                '<p>Odoo recommends not reusing this invoice (set to draft) '
                'to create a new one, due to the fact that this was cancelled '
                'in another period.</p><p><b>It is recommended</b> that you '
                'create a new record (or duplicate this one) and leave this '
                'invoice for you actual administrative control.</p><p>'
                '<b>Remember</b> to add the CFDI origin in the new invoice.'
                '</p>'))
        inv_no_mx = self - inv_mx
        return super(
            AccountInvoice, inv_no_mx + to_draft).action_invoice_draft()

    @api.multi
    def action_invoice_cancel(self):
        """All Mexican invoices are considered."""
        inv_mx = self.filtered(
            lambda inv: inv.company_id.country_id == self.env.ref('base.mx'))
        if not inv_mx:
            return super(AccountInvoice, self).action_invoice_cancel()
        inv_paid = inv_mx.filtered(
            lambda inv: inv.state not in ['draft', 'open'])
        for inv in inv_paid:
            inv.message_post(body=_(
                'Invoice must be in draft or open state in order to be '
                'cancelled.'))
        invoices = inv_mx - inv_paid
        date_mx = self.env[
            'l10n_mx_edi.certificate'].sudo().get_mx_current_datetime()
        if self._context.get('force_cancellation_date'):
            date_mx = fields.Datetime.from_string(
                self._context['force_cancellation_date'])
        in_period = invoices.filtered(
            lambda inv: inv.date_invoice and
            inv.date_invoice >= date_utils.start_of(
                date_mx, 'month').date() and
            inv.date_invoice <= date_utils.end_of(date_mx, 'month').date())
        for inv in invoices - in_period:
            inv.move_id.reverse_moves(date_mx)
            inv.state = 'cancel'
            inv._l10n_mx_edi_cancel()
        inv_no_mx = self - inv_mx
        return super(
            AccountInvoice, in_period + inv_no_mx).action_invoice_cancel()
