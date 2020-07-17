# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from suds.client import Client

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

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
        res = super(AccountPayment, self)._l10n_mx_edi_finkok_cancel(pac_info)
        url = pac_info['url']
        username = pac_info['username']
        password = pac_info['password']
        for pay in self:
            uuid = pay.l10n_mx_edi_cfdi_uuid
            company = pay.company_id
            try:
                client = Client(url, timeout=20)
                response = client.service.get_receipt(
                    username, password, company.vat, uuid)
            except Exception as e:
                pay.l10n_mx_edi_log_error(str(e))
                continue
            if not getattr(response, 'date', None):
                continue
            date = response.date
            pay.l10n_mx_edi_cancellation_date = date.split('T')[0]
            pay.l10n_mx_edi_cancellation_time = date.split('T')[1][:8]
        return res

    @api.multi
    @api.returns('self')
    def is_from_previous_periods(self):
        date = self.env[
            'l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date()
        date = date.replace(day=1)
        date = date - timedelta(days=1)
        return self.filtered(lambda p: p.payment_date <= (
            p.company_id.period_lock_date or date))

    @api.multi
    def l10n_mx_edi_cancel_with_reversal(self, date=False, journal_id=None):
        to_cancel = self.filtered(
            lambda p: p.state not in ('draft', 'cancelled'))
        payments = to_cancel.is_from_previous_periods()
        # normal cancel for current period
        (self - payments).cancel()
        # Set none no signed payments
        payments.filtered(lambda p: p.l10n_mx_edi_pac_status in (
            'retry', 'to_sign')).write({'l10n_mx_edi_pac_status': 'none'})
        # search accounts for tax and cash basis.
        taxes = self.env['account.tax'].search([])
        basis_account_ids = taxes.mapped('cash_basis_base_account_id')
        basis_account_ids |= taxes.mapped('cash_basis_account_id')
        basis_account_ids |= taxes.mapped('account_id')
        basis_account_ids |= taxes.mapped('refund_account_id')
        for pay in payments:
            amls = pay.move_line_ids
            moves = amls.mapped('move_id')
            if moves.mapped('reverse_entry_id'):
                pay.message_post(body=_(
                    'This cancellation was skipped because the account move '
                    'has a reversed move already.'))
                continue
            amls.remove_move_reconcile()
            res = moves.reverse_moves(date=date, journal_id=journal_id)
            reversed_moves = moves.browse(res)
            for r_move in reversed_moves:
                amls_to_delete = r_move.line_ids.filtered(
                    lambda a: a.account_id.id in basis_account_ids.ids)
                if not amls_to_delete:
                    continue
                r_move.line_ids.remove_move_reconcile()
                r_move.button_cancel()
                amls_to_delete.unlink()
                r_move.post()
                amls_to_reconcile = (amls + r_move.line_ids).filtered(
                    lambda a: a.account_id.reconcile or
                    a.account_id.internal_type == 'liquidity')
                amls_to_reconcile.reconcile()
            pay.message_post_with_view(
                'l10n_mx_edi_cancellation.cancellation_with_reversal_move',
                values={'self': pay, 'origin': reversed_moves},
                subtype_id=self.env.ref('mail.mt_note').id)
        for record in payments.filtered(lambda r: r.l10n_mx_edi_is_required()):
            record._l10n_mx_edi_cancel()

    @api.multi
    def cancel(self):
        """Cancel method with reversal entries"""
        to_cancel = self.filtered(
            lambda p: p.state not in ('draft', 'cancelled'))
        payments = to_cancel.is_from_previous_periods()
        # normal cancel
        if not payments:
            return super(AccountPayment, self).cancel()
        # cancel with previous period
        has_group = self.env.user.has_group(
            'l10n_mx_edi_cancellation_complement.allow_cancel_with_reversal_move')  # noqa
        warning = _('You have no permission to cancel payments from previous '
                    'periods')
        if 'customer' in payments.mapped('partner_type') and payments.filtered(
                'company_id.l10n_mx_cancellation_with_reversal_customer'):
            if not has_group:
                raise UserError(warning)
            return self.env.ref(
                'l10n_mx_edi_cancellation_complement.action_reversal_move_view_to_cancel').read()[0]  # noqa
        if 'supplier' in payments.mapped('partner_type') and payments.filtered(
                'company_id.l10n_mx_cancellation_with_reversal_supplier'):
            if not has_group:
                raise UserError(warning)
            return self.env.ref(
                'l10n_mx_edi_cancellation_complement.action_reversal_move_view_to_cancel').read()[0]  # noqa
        return super(AccountPayment, payments).cancel()


class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.register.payments'

    l10n_mx_edi_origin = fields.Char(
        string='CFDI Origin', copy=False,
        help='In some cases the payment must be regenerated to fix data in it.'
        ' In that cases is necessary to fill this with one of these formats: '
        '\n04|UUID1, UUID2, ...., UUIDn.\nor\nUUID1, UUID2, ..., UUIDn\n'
        'Example:\n"04|89966ACC-0F5C-447D-AEF3-3EED22E711EE,89966ACC-0F5C-447D-AEF3-3EED22E711EE"\nor\n"89966ACC-0F5C-447D-AEF3-3EED22E711EE,89966ACC-0F5C-447D-AEF3-3EED22E711EE"')  # noqa

    @api.multi
    def _prepare_payment_vals(self, invoices):
        """Set CFDI origin"""
        values = super(AccountRegisterPayments, self)._prepare_payment_vals(
            invoices)
        if not self.l10n_mx_edi_origin:
            return values
        origin = (
            self.l10n_mx_edi_origin if self.l10n_mx_edi_origin.startswith(
                '04|') else '04|' + self.l10n_mx_edi_origin)
        values.update({'l10n_mx_edi_origin': origin})
        return values
