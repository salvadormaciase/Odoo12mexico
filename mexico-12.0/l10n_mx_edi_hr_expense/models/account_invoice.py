# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    date_invoice = fields.Date(track_visibility='onchange')
    l10n_mx_edi_expense_id = fields.Many2one(
        'hr.expense', 'Expense',
        help='Stores the expense related with this invoice')
    l10n_mx_edi_expense_sheet_id = fields.Many2one(
        'hr.expense.sheet', string='Expense Sheet',
        related='l10n_mx_edi_expense_id.sheet_id', store=True,
        help='Stores the expense sheet related with this invoice')

    @api.multi
    def action_invoice_open(self):
        res = super().action_invoice_open()
        message = _(
            'The amount total in the CFDI is (%s) and that value is different '
            'to the invoice total (%s), that values must be consistent. '
            'Please review the invoice lines and try again. You can contact '
            'your manager to change the minimum allowed for this difference '
            'in the journal.\n\nCFDI with UUID: %s')
        label = self.env.ref(
            'l10n_mx_edi_hr_expense.tag_omit_invoice_amount_check')
        partners = self.mapped('partner_id').filtered(
            lambda par: label not in par.category_id)
        invoices = self.filtered(lambda inv: inv.l10n_mx_edi_cfdi_amount and
                                 inv.partner_id in partners)
        for invoice in invoices.filtered(lambda inv: inv.type in (
                'in_invoice', 'in_refund')):
            diff = invoice.journal_id.l10n_mx_edi_amount_authorized_diff
            if not abs(invoice.amount_total - invoice.l10n_mx_edi_cfdi_amount) > diff:  # noqa
                continue
            currency = invoice.currency_id
            raise UserError(message % (
                formatLang(self.env, invoice.l10n_mx_edi_cfdi_amount, currency_obj=currency),  # noqa
                formatLang(self.env, invoice.amount_total, currency_obj=currency),  # noqa
                invoice.l10n_mx_edi_cfdi_uuid))
        for invoice in invoices.filtered(lambda inv: inv.type in (
                'out_invoice', 'out_refund')):
            diff = invoice.journal_id.l10n_mx_edi_amount_authorized_diff
            if not abs(invoice.amount_total - invoice.l10n_mx_edi_cfdi_amount) > diff:  # noqa
                continue
            currency = invoice.currency_id
            invoice.message_post(body=message % (
                formatLang(self.env, invoice.l10n_mx_edi_cfdi_amount, currency_obj=currency),  # noqa
                formatLang(self.env, invoice.amount_total, currency_obj=currency),  # noqa
                invoice.l10n_mx_edi_cfdi_uuid))
        return res

    @api.multi
    def action_view_expense(self):
        self.ensure_one()
        expense = self.env['hr.expense'].search([
            ('l10n_mx_edi_invoice_id', '=', self.id)], limit=1)
        if not expense:
            raise UserError(_('This invoice was not created from an expense'))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense',
            'target': 'current',
            'res_id': expense.id
        }

    @api.multi
    def _reclassify_journal_entries(
            self, account_id=None, product_id=None, date=None):
        """Reclassify data in the invoice"""
        for inv in self.filtered(lambda inv: inv.type in ('in_invoice',
                                                          'in_refund')):
            temporal_date = date or inv.date
            error_message_lock_date = _(
                "You can not modify the account move in a date before lock "
                "date: %s")

            # /!\ NOTE: Let us check that we are allowed to modify an invoice
            # in a previous period.
            granted_permission, lock_date = (
                self.env['account.move']._allow_to_modify_account_move(
                    inv.date, inv.company_id))
            if not granted_permission:
                raise UserError(error_message_lock_date % lock_date)
            if date:
                # /!\ NOTE: Let us check that we are allowed to move an
                # invoice to a previous period.
                granted_permission, lock_date = (
                    self.env['account.move']._allow_to_modify_account_move(
                        date, inv.company_id))
                if not granted_permission:
                    raise UserError(error_message_lock_date % lock_date)

            inv.date = temporal_date
            first_inv_state = inv.state
            first_inv_residual = inv.residual

            values = {}
            message_log = []
            if account_id:
                values['account_id'] = account_id.id
                message_log.append(
                    _('<li>The account was changed to: %s.</li>')
                    % account_id.display_name)
            if product_id:
                values['product_id'] = product_id.id
                message_log.append(
                    _('<li>The product was changed to: %s.</li>')
                    % product_id.display_name)
            if values:
                inv.invoice_line_ids.write(values)
            if not inv.move_id:
                continue

            if date:
                message_log.append(_('<li>The date was changed to: %s.</li>')
                                   % temporal_date.strftime('%d/%m/%Y'))
                lines = inv.move_id.line_ids.filtered(
                    lambda l: l.account_id == inv.account_id)
                apr_ids = (lines.mapped('matched_debit_ids') |
                           lines.mapped('matched_credit_ids'))
                apr_list = self._unreconcile_apr(lines, apr_ids)
                move_id = inv.move_id
                move_id.line_ids.remove_move_reconcile()

                if inv.currency_id != inv.company_currency_id:
                    move_id.button_cancel()
                    inv.write({'move_id': False})
                    move_id.unlink()
                    inv.action_move_create()
                else:
                    self._process_move_line(inv, temporal_date, values)

                for aml_to_check in apr_list:
                    aml_to_check = aml_to_check[1]
                    if not aml_to_check.exists():
                        # /!\ NOTE: If this APR is part of a reconciliation
                        # with a FX Diff then aml_to_check could have been
                        # destroyed.
                        continue
                    inv.with_context(
                        check_move_validity=False).register_payment(
                            aml_to_check)
            else:
                self._process_move_line(inv, temporal_date, values)

            if (first_inv_state != inv.state or
               first_inv_residual != inv.residual):
                msg = (_("This invoice %s could not be processed because there"
                         "was an error in applying the payments that it has "
                         "assigned and we could not automatically leave it in "
                         "the initial state before performing this process.")
                       % inv.number)
                raise UserError(msg)
            if message_log:
                inv.message_post(body="<ul> %s </ul>" % (''.join(message_log)))

    def _unreconcile_apr(self, lines, apr_ids):
        apr_list = []
        for apr in apr_ids:
            if not apr.exists():
                continue
            if apr.debit_move_id in lines:
                aml_in_inv = apr.debit_move_id
                aml_to_check = apr.credit_move_id
            elif apr.credit_move_id in lines:
                aml_in_inv = apr.credit_move_id
                aml_to_check = apr.debit_move_id
            apr_list.append((aml_in_inv, aml_to_check))
            apr.with_context(check_move_validity=False).unlink()
        return apr_list

    def _process_move_line(self, inv, temporal_date, values):
        state = inv.move_id.state
        if state == 'posted':
            inv.move_id.button_cancel()
        inv.move_id.date = temporal_date
        tax_accounts = inv.tax_line_ids.mapped('account_id')
        lines = inv.move_id.line_ids.filtered(
            lambda l: l.account_id != inv.account_id and
            l.account_id not in tax_accounts)
        values['date'] = temporal_date
        lines.write(values)
        if state == 'posted':
            inv.move_id.action_post()
