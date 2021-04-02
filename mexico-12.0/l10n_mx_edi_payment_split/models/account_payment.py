# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import codecs
import json
from collections import defaultdict
from itertools import groupby
import io
import chardet

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.addons.account.models.account_payment import (
    MAP_INVOICE_TYPE_PARTNER_TYPE, MAP_INVOICE_TYPE_PAYMENT_SIGN)
from odoo.tools import float_is_zero
from odoo.tools import pycompat
BOM_MAP = {
    'utf-16le': codecs.BOM_UTF16_LE,
    'utf-16be': codecs.BOM_UTF16_BE,
    'utf-32le': codecs.BOM_UTF32_LE,
    'utf-32be': codecs.BOM_UTF32_BE,
}


class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.register.payments'

    payment_invoice_ids = fields.One2many(
        'account.register.invoices', 'register_id', help='Invoices that were paid in mass')
    dummy_amount = fields.Float(store=False, help='Technical field')
    custom_rate = fields.Float(
        help="If used. This rate will be written in all the invoices to pay",
        store=False, copy=False, digits=dp.get_precision('Rate Precision'))
    csv_file = fields.Binary(copy=False, help='CSV file with invoice and amount.',
                             groups="l10n_mx_edi_payment_split.payment_split_allow_csv_info_import")
    csv_file_name = fields.Char(copy=False, help='CSV file name.')

    @api.onchange('csv_file')
    def l10n_mx_edi_import_invoice_info(self):
        """csv file must be ---> invoice_number,amount,rate"""
        self.ensure_one()
        if not self.csv_file:
            return
        if self.csv_file_name and not self.csv_file_name.lower().endswith('.csv'):
            raise UserError(_("Please use a file with CSV format."))
        csv_data = base64.b64decode(self.csv_file)
        # Check mimetype
        self.update({'payment_invoice_ids': False})
        # Check encoding
        try:
            encoding = chardet.detect(csv_data)['encoding'].lower()
            bom = BOM_MAP.get(encoding)
            if bom and csv_data.startswith(bom):
                encoding = encoding[:-2]
            if encoding != 'utf-8':
                csv_data = csv_data.decode(encoding).encode('utf-8')
            # Separator
            separator = ','
            csv_iterator = pycompat.csv_reader(
                io.BytesIO(csv_data), quotechar='"', delimiter=separator)
        except Exception:
            raise UserError(_("Please use a file with CSV format."))
        register_ids = self.payment_invoice_ids
        for row in csv_iterator:
            invoice = self.invoice_ids.search([('number', '=', row[0]), ('state', '=', 'open')])
            try:
                col_num = len(row)
                amount = float(row[1]) if col_num > 1 else 0
                rate = float(row[2]) if col_num == 3 else 1
            except ValueError:
                continue
            if not invoice or amount <= 0:
                continue
            register_ids |= self.payment_invoice_ids.create({
                'invoice_id': invoice.id,
                'date': invoice.date_invoice,
                'date_due': invoice.date_due,
                'partner_id': invoice.partner_id.id,
                'amount': invoice.residual,
                'payment_currency_amount': amount,
                'rate': rate,
                'payment_currency_id': self.currency_id.id,
                'register_id': self.id,
            })
        if not register_ids:
            raise UserError(_("No invoice info to import. Please make sure you're using a file with CSV format "
                              "and comma (,) separator."))
        self.update({'payment_invoice_ids': [(6, 0, register_ids.ids)]})
        self.invoice_ids = register_ids.mapped('invoice_id')
        self._onchange_payment_invoice()
        # update context
        if register_ids:
            ctx = self._context.copy()
            ctx.update({'active_ids': register_ids.mapped('invoice_id.id'), 'active_id': register_ids[0].id})
            self = self.with_context(ctx)

    @api.model
    def default_get(self, values):
        res = super(AccountRegisterPayments, self).default_get(values)
        payment_currency_id = self.env['res.currency'].browse(res.get('currency_id'))

        invoice_ids = self.env['account.invoice'].browse(self._context.get('active_ids')).sorted('date_due')
        amount_dict = dict(
            (inv.id, payment_currency_id.round(
                self._compute_payment_amount(inv, payment_currency_id) *
                MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type]))
            for inv in invoice_ids)
        amount = abs(payment_currency_id.round(sum(amount_dict.values())))
        res.update({'amount': amount,
                    'group_invoices': False,
                    'dummy_amount': amount})
        cmp_rate = {
            True: lambda a: a,
            False: lambda a: a and 1 / a
        }
        comp_currency = self.env.user.company_id.currency_id
        res['payment_invoice_ids'] = [(0, 0, {
            'invoice_id': inv.id,
            'currency_id': inv.currency_id.id,
            'partner_id': inv.partner_id.id,
            'date': inv.date_invoice,
            'rate': cmp_rate[inv.currency_id == comp_currency](
                payment_currency_id._convert(
                    1, inv.currency_id, inv.company_id,
                    fields.Date.context_today(self), round=False)
                if payment_currency_id != inv.currency_id else 1.00),
            'date_due': inv.date_due,
            'amount': inv.residual,
            'payment_amount': inv.residual,
            'payment_currency_id': payment_currency_id.id,
            'payment_currency_amount': amount_dict[inv.id],
        }) for inv in invoice_ids]
        return res

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        """If there is a custom rate, the value returned by this method
        must be a computes value between the custom rate and the amount to pay"""
        if not invoices:
            invoices = self.invoice_ids

        # Get the payment currency
        if not currency:
            currency = (
                self.currency_id or self.journal_id.currency_id or
                self.journal_id.company_id.currency_id or invoices and
                invoices[0].currency_id)

        payment_currency = currency

        if not (hasattr(self, 'custom_rate') and self.custom_rate):

            # Avoid currency rounding issues by summing the amounts according
            # to the company_currency_id before
            invoice_datas = invoices.read_group(
                [('id', 'in', invoices.ids)],
                ['currency_id', 'type', 'residual_signed',
                 'residual_company_signed'],
                ['currency_id', 'type'], lazy=False)
            total = 0.0
            for invoice_data in invoice_datas:
                sign = MAP_INVOICE_TYPE_PAYMENT_SIGN[invoice_data['type']]
                amount_total = sign * invoice_data['residual_signed']
                invoice_currency = (
                    self.env['res.currency'].browse(
                        invoice_data['currency_id'][0]))
                if payment_currency == invoice_currency:
                    total += amount_total
                else:
                    total += invoice_currency._convert(
                        amount_total,
                        payment_currency,
                        self.env.user.company_id,
                        self.payment_date or fields.Date.today())
            return total

        # Avoid currency rounding issues by summing the amounts according to
        # the company_currency_id before
        total = 0.0
        groups = groupby(invoices, lambda i: i.currency_id)
        cmp_rate = {
            True: lambda a, b: b and a / b,
            False: lambda a, b: a * b
        }
        company_currency = self.env.user.company_id.currency_id
        for payment_currency, payment_invoices in groups:
            amount_total = sum(
                [MAP_INVOICE_TYPE_PAYMENT_SIGN[i.type] * i.residual_signed
                 for i in payment_invoices])
            if payment_currency == currency:
                total += amount_total
                continue
            total += currency.round(
                cmp_rate[company_currency == payment_currency](
                    amount_total, self.custom_rate))
        return total

    @api.onchange('amount')
    def _onchange_amount(self):
        """Perform custom operations only if the amount actually changed

        It may happen that onchanges are executed just before creating
        payments, even when there was no changes, which may screw up amount
        values. For more info, see:
        https://github.com/odoo/odoo/issues/34429
        """
        if self.amount != self.dummy_amount:
            self._onchange_payment_invoice()
        return super(AccountRegisterPayments, self)._onchange_amount()

    @api.onchange('payment_invoice_ids', 'custom_rate')
    def _onchange_payment_invoice(self):
        if self.amount == self.dummy_amount:
            cumulative_amount = sum(
                self.payment_invoice_ids.mapped('payment_currency_amount'))
            amount = self.currency_id.round(cumulative_amount)
            self.update({'amount': amount,
                         'dummy_amount': amount})
            return

        full_amount = self.amount
        for line in self.payment_invoice_ids.sorted('date_due'):
            if float_is_zero(full_amount,
                             precision_rounding=self.currency_id.rounding):
                line.payment_currency_amount = 0.0
                continue
            amount = abs(self.currency_id.round(self._compute_payment_amount(
                line.invoice_id, self.currency_id)))
            if amount <= full_amount:
                full_amount -= amount
                line.update({'payment_currency_amount': amount})
            elif amount > full_amount:
                line.update({'payment_currency_amount': full_amount})
                full_amount = 0.0
        self.dummy_amount = self.amount

    @api.onchange('currency_id', 'payment_date', 'custom_rate')
    def _onchange_currency_at_payment(self):
        cumulative_amount = 0

        cmp_rate = {
            True: lambda a: a,
            False: lambda a: a and 1 / a
        }
        company_currency = self.env.user.company_id.currency_id
        for line in self.payment_invoice_ids:
            amount = abs(self.currency_id.round(self._compute_payment_amount(
                line.invoice_id, self.currency_id)))
            line.payment_currency_amount = amount
            line.payment_currency_id = self.currency_id.id
            cumulative_amount += amount
            if self.currency_id == line.invoice_id.currency_id:
                line.rate = 1.00
                continue
            rate = self.custom_rate
            if not self.custom_rate:
                rate = self.currency_id._convert(
                    1, line.invoice_id.currency_id, line.invoice_id.company_id,
                    self.payment_date, round=False)
                same_currency = line.invoice_id.currency_id == company_currency
                rate = cmp_rate[same_currency](rate)
            line.rate = rate if rate else 1.0

        self.amount = self.currency_id.round(cumulative_amount)

    @api.multi
    def _prepare_payment_vals(self, invoices):
        values = super()._prepare_payment_vals(invoices)
        if not self.partner_id:
            return values
        if self.partner_id.type == 'invoice':
            partner_id = self.partner_id
        else:
            partner_id = self.partner_id.commercial_partner_id
        values.update({'partner_id': partner_id.id})
        return values

    @api.multi
    def create_payments(self):
        payment_obj = self.env['account.payment']
        payments = payment_obj
        for payment_vals in self.get_payments_vals():
            inv_list = {}
            json_data = {
                'data': {
                    'amount': self.amount,
                    'custom_rate': self.custom_rate,
                    'communication': payment_vals.get('communication'),
                    'l10n_mx_edi_partner_bank_id':
                    self.l10n_mx_edi_partner_bank_id.id,
                    'l10n_mx_edi_payment_method_id':
                    self.l10n_mx_edi_payment_method_id.id,
                    'payment_date': self.payment_date.strftime('%d/%m/%Y')
                    if self.payment_date else ''},
                'invoices': []}

            if not payment_vals.get('invoice_ids'):
                continue

            for line in self.payment_invoice_ids:

                # /!\ NOTE: It is possible to use a filtered method here
                if line.invoice_id.id not in payment_vals['invoice_ids'][0][2]:
                    continue

                inv_list[line.invoice_id.id] = {
                    'currency_id': line.invoice_id.currency_id,
                    'type': line.invoice_id.type,
                    'payment_amount': line.payment_amount,
                    'payment_currency_amount': line.payment_currency_amount,
                    'payment_currency_id': line.payment_currency_id.id,
                    'rate': line.rate,
                    'residual': line.invoice_id.residual,
                }
                json_data['invoices'].append({
                    'invoice_id': line.invoice_id.id,
                    'payment_currency_amount': line.payment_currency_amount,
                    'rate': line.rate,
                    'residual': line.invoice_id.residual,
                    'payment_amount': line.payment_amount,
                    'currency_id': line.currency_id.id,
                    'amount': line.amount,
                    'date_due': line.date_due.strftime('%d/%m/%Y')
                    if line.date_due else '',
                    'date': line.date.strftime('%d/%m/%Y')
                    if line.date else '',
                    'partner_id': line.partner_id.id})

            payments += payment_obj.create(payment_vals)
        payments.with_context(invoice_partial_payment=inv_list).post()
        for payment in payments:
            payment_obj.json_attachment(json_data, payment)

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    @api.multi
    def _compute_show_communication_field(self):
        """Always show the communication field

         Even if invoices are not grouped.
         """
        for record in self:
            record.show_communication_field = True

    @api.onchange('group_invoices')
    def _onchange_group_invoices(self):
        # /!\ NOTE: Odoo include this change at
        # https://github.com/vauxoo/odoo/commit/47f176f5d8e66d9de5a829983bee94e328237115
        # We don't use it
        self.multi = False


class AccountRegisterInvoices(models.TransientModel):
    _name = 'account.register.invoices'
    _description = 'A model to hold invoices being paid in payment register'
    _order = 'date_due ASC'

    @api.depends('payment_currency_amount', 'rate')
    def _compute_amount(self):
        for record in self:
            currency_amount = record.currency_id.round(
                record.payment_currency_amount)
            record.payment_amount = currency_amount
            if record.register_id.currency_id != record.invoice_id.currency_id:
                cmp_rate = {
                    True: lambda a: a,
                    False: lambda a: a and 1 / a
                }
                same = True
                if record.env.user.company_id.currency_id != record.invoice_id.currency_id:
                    same = False
                record.payment_amount = record.currency_id.round(
                    currency_amount * cmp_rate[same](record.rate))

    @api.multi
    def _inverse_amount(self):
        return

    invoice_id = fields.Many2one(
        'account.invoice', help='Invoice being paid')
    currency_id = fields.Many2one(
        'res.currency', help='Currency of this invoice',
        related='invoice_id.currency_id',)
    date = fields.Date(help="Invoice Date")
    date_due = fields.Date(string='Due Date',
                           help="Maturity Date in the invoice")
    partner_id = fields.Many2one(
        'res.partner', help='Partner involved in payment')
    amount = fields.Float(string='Due Amount', help='Amount to pay')
    payment_amount = fields.Monetary(
        store=True, compute='_compute_amount', inverse='_inverse_amount',
        currency_field='currency_id',
        help='Amount being paid')
    payment_currency_amount = fields.Monetary(
        currency_field='payment_currency_id',
        help='Amount in currency of payment')
    rate = fields.Float(
        help="Payment rate of this Document",
        copy=False, digits=dp.get_precision('Rate Precision'))
    payment_currency_id = fields.Many2one(
        'res.currency', help='Currency which this payment is being done')
    register_id = fields.Many2one(
        'account.register.payments',
        help='Technical field to connect to Bulk Invoice',
        copy=False)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def get_line_vals(self, line):
        pay_currency_id = self.currency_id
        inv_currency_id = line['currency_id']
        com_currency_id = self.company_id.currency_id
        difference_amount = {
            True: lambda a, b: a['residual'],
            False: lambda a, b: (
                a['residual'] * a['rate'] if b else a['residual'] / a['rate'])
            if a['rate'] else a['payment_currency_amount']
        }
        same_cur = line['currency_id'].id == line['payment_currency_id']
        company_cur = com_currency_id.id == line['payment_currency_id']
        amount = line['payment_amount']
        pay_amount = line['payment_currency_amount']
        if (self.payment_difference_handling == 'reconcile' and
                self.payment_difference):
            pay_amount = difference_amount[same_cur](line, company_cur)
            amount = line['residual']
        sign = -1 if self.payment_type == 'inbound' else 1
        amount_currency = 0
        currency_id = self.env['res.currency']
        if (pay_currency_id == inv_currency_id and
                pay_currency_id == com_currency_id):
            debit = 0 if self.payment_type == 'inbound' else pay_amount
            credit = pay_amount if self.payment_type == 'inbound' else 0

        elif (com_currency_id == inv_currency_id and
                pay_currency_id != inv_currency_id):
            debit = 0 if self.payment_type == 'inbound' else amount
            credit = amount if self.payment_type == 'inbound' else 0
            amount_currency = pay_amount * sign
            currency_id = pay_currency_id

        elif (com_currency_id == pay_currency_id and
                pay_currency_id != inv_currency_id):
            debit = 0 if self.payment_type == 'inbound' else pay_amount
            credit = pay_amount if self.payment_type == 'inbound' else 0
            amount_currency = amount * sign
            currency_id = inv_currency_id

        elif (com_currency_id != pay_currency_id and
                (pay_currency_id == inv_currency_id or
                 pay_currency_id != inv_currency_id)):
            amount = pay_currency_id._convert(
                pay_amount, com_currency_id, self.company_id,
                self.payment_date, round=True)
            debit = 0 if self.payment_type == 'inbound' else amount
            credit = amount if self.payment_type == 'inbound' else 0
            amount_currency = pay_amount * sign
            currency_id = pay_currency_id

        return debit, credit, amount_currency, currency_id

    @api.multi
    def _l10n_mx_edi_invoice_payment_data(self):
        """All-in-all this is a full override of original method in the l10n_mx
        method. ABSA uses a quite different approach for total_curr variable
        by computing payment_currency_amount using aml.amount_currency instead
        of free conversion of the amount_payment
        """
        self.ensure_one()
        total_paid = total_curr = total_currency = 0
        for invoice in self.invoice_ids:
            amount = [p for p in invoice._get_payments_vals() if (
                p.get('account_payment_id', False) == self.id or not p.get(
                    'account_payment_id') and (not p.get(
                        'invoice_id') or p.get('invoice_id') == invoice.id))]
            amount_payment = sum([data.get('amount', 0.0) for data in amount])
            if self._context.get('invoice_partial_payment', False):
                payment_currency_amount = sum(
                    abs(aml.amount_currency if self.currency_id != self.company_id.currency_id else aml.balance)
                    for aml in invoice.payment_move_line_ids.filtered(lambda x: x.payment_id == self))
                total_paid += amount_payment
                total_currency += amount_payment if invoice.currency_id == self.currency_id else 0
                total_curr += payment_currency_amount
            else:
                amount_payment = amount_payment if sum(
                    [p.get('amount') for p in invoice._get_payments_vals()]) <= invoice.amount_total else \
                    invoice.amount_total
                total_paid += amount_payment if invoice.currency_id != self.currency_id else 0
                total_currency += amount_payment if invoice.currency_id == self.currency_id else 0
                total_curr += invoice.currency_id.with_context(
                    date=self.payment_date)._convert(
                        amount_payment, self.currency_id, self.company_id, self.payment_date, round=False)
        return dict(
            total_paid=total_paid,
            total_curr=total_curr,
            total_currency=total_currency)

    @api.multi
    def _create_multiline_payment_entry(self, payment_amnt):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        move = self.env['account.move'].create(self._get_move_vals())

        payment_lines = self._context.get('invoice_partial_payment')
        total_debit = total_credit = paid_amount = 0
        difference_amount = {
            True: lambda a, b: a['residual'],
            False: lambda a, b: (
                a['residual'] * a['rate'] if b else a['residual'] / a['rate'])
            if a['rate'] else a['payment_currency_amount']
        }
        with self.env.norecompute():
            payment_diff = (
                self.payment_difference_handling == 'reconcile' and
                self.payment_difference)
            all_counterpart = aml_obj
            for inv in (self.invoice_ids.browse(payment_lines.keys()) &
                        self.invoice_ids):
                partial = payment_lines[inv.id]
                amount = partial['payment_currency_amount']
                if payment_diff:
                    same_cur = (
                        partial['currency_id'].id ==
                        partial['payment_currency_id'])
                    company_cur = (
                        partial['payment_currency_id'] ==
                        self.env.user.company_id.currency_id.id)
                    amount = difference_amount[same_cur](partial, company_cur)

                debit, credit, amount_currency, currency_id = (
                    self.get_line_vals(partial))

                paid_amount += amount
                total_debit += debit
                total_credit += credit

                # Write line corresponding to invoice payment
                counterpart_aml_dict = self._get_shared_move_line_vals(
                    debit, credit, amount_currency, move.id)
                counterpart_aml_dict.update(
                    self._get_counterpart_move_line_vals(inv))
                counterpart_aml_dict['currency_id'] = currency_id.id
                counterpart_aml_dict['account_id'] = inv.account_id.id
                counterpart_aml_dict['partner_id'] = inv.partner_id.commercial_partner_id.id
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                all_counterpart |= counterpart_aml

                # Reconcile with the invoices and write off
                inv.register_payment(counterpart_aml)
            sign = 1 if self.payment_type == 'inbound' else -1
            offset = sign * payment_amnt + paid_amount
            # Writing the full amount of money for the liquidity part
            debit, credit, amount_currency, currency_id = (
                aml_obj.with_context(date=self.payment_date).
                _compute_amount_fields(
                    payment_amnt, self.currency_id, self.company_id.currency_id
                ))

            credit_debit = total_credit - total_debit
            debit = credit_debit if credit_debit > 0 else 0
            credit = -credit_debit if credit_debit < 0 else 0
            if payment_diff or (self.payment_difference_handling == 'open' and not float_is_zero(offset, precision_rounding=self.currency_id.rounding)):  # noqa
                debit, credit, amount_currency, currency_id = (
                    aml_obj.with_context(date=self.payment_date).
                    _compute_amount_fields(
                        -payment_amnt, self.currency_id,
                        self.company_id.currency_id))
                amount_currency = -amount_currency

            if self.currency_id == self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(
                debit, credit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(
                self._get_liquidity_move_line_vals(payment_amnt))
            aml_obj.create(liquidity_aml_dict)

            # This is the quantity of money that was left without being applied
            # on payments
            # /!\ NOTE: Forgive me father for I have sinned. This piece of code
            # really-really need an extreme make-over. For me it seems to have
            # too much junk!!!. Junk that I have previously added!!!
            aml_bal = sum((aml.debit - aml.credit) for aml in move.line_ids)
            if not float_is_zero(
                    offset, precision_rounding=self.currency_id.rounding):

                fdebit, fcredit, amount_currency, currency_id = (
                    aml_obj.with_context(date=self.payment_date).
                    _compute_amount_fields(
                        self.payment_difference, self.currency_id,
                        self.company_id.currency_id))

                debit, credit, amount_currency, currency_id = (
                    aml_obj.with_context(date=self.payment_date).
                    _compute_amount_fields(
                        offset, self.currency_id,
                        self.company_id.currency_id))

                balance = abs(aml_bal)

                debit = fdebit and balance
                credit = fcredit and balance

                amount_currency = (
                    -abs(amount_currency)
                    if credit else abs(amount_currency))

                # Write line corresponding to invoice payment
                counterpart_aml_dict = self._get_shared_move_line_vals(
                    debit, credit, amount_currency, move.id, False)
                counterpart_aml_dict.update(
                    self._get_counterpart_move_line_vals(False))
                counterpart_aml_dict['currency_id'] = currency_id
                if self.payment_difference_handling == 'reconcile':
                    counterpart_aml_dict['name'] = self.writeoff_label
                    counterpart_aml_dict['account_id'] = self.writeoff_account_id.id
                counterpart_aml = aml_obj.create(counterpart_aml_dict)

        self.recompute()

        move.post()
        return move

    @api.multi
    def _create_payment_entry(self, amount):
        if self._context.get('invoice_partial_payment'):
            return self._create_multiline_payment_entry(amount)
        return super(AccountPayment, self)._create_payment_entry(amount)

    @api.multi
    def json_attachment(self, json_data, record):
        """This method will create an attachment that contains the json from
        an imported record
        """
        attachment_datas = json.dumps(json_data, indent=1)
        encoded = base64.b64encode(attachment_datas.encode('ascii'))
        filename = 'json-%s.json' % (record.name)
        self.env['ir.attachment'].create({
            'datas': encoded,
            'res_id': record.id,
            'res_model': record._name,
            'mimetype': 'application/zip',
            'name': filename,
            'datas_fname': filename,
        })


class AccountAbstractPayment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    @api.model
    def default_get(self, fields_list):  # noqa # pylint: disable=method-required-super
        """ default_get(fields) -> default_values

        Return default values for the fields in ``fields_list``. Default
        values are determined by the context, user defaults, and the model
        itself.

        :param fields_list: a list of field names
        :type fields_list: list
        :return: a dictionary mapping each field name to its corresponding default value, if it has one.
        :rtype: dict

        """
        # trigger view init hook
        self.view_init(fields_list)

        defaults = {}
        parent_fields = defaultdict(list)
        ir_defaults = self.env['ir.default'].get_model_defaults(self._name)

        for name in fields_list:
            # 1. look up context
            key = 'default_' + name
            if key in self._context:
                defaults[name] = self._context[key]
                continue

            # 2. look up ir.default
            if name in ir_defaults:
                defaults[name] = ir_defaults[name]
                continue

            field = self._fields.get(name)

            # 3. look up field.default
            if field and field.default:
                defaults[name] = field.default(self)
                continue

            # 4. delegate to parent model
            if field and field.inherited:
                field = field.related_field
                parent_fields[field.model_name].append(field.name)

        # convert default values to the right format
        defaults = self._convert_to_write(defaults)

        # add default values for inherited fields
        for model, names in parent_fields.items():
            defaults.update(self.env[model].default_get(names))

        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.invoice':
            return defaults

        invoices = self.env['account.invoice'].browse(active_ids)

        # Check all invoices are open
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_(
                "You can only register payments for open invoices"))

        # Check all invoices are only one supplier
        if len(invoices.filtered(lambda x:
                                 x.type == 'in_invoice'
                                 ).mapped('partner_id.vat')) > 1:
            raise UserError(_(
                "You can't register payments for multiple suppliers"))

        # Look if we are mixin multiple commercial_partner or customer invoices
        # with vendor bills
        multi = any(
            inv.commercial_partner_id != invoices[0].commercial_partner_id
            or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] !=
            MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
            or inv.account_id != invoices[0].account_id
            or inv.partner_bank_id != invoices[0].partner_bank_id
            for inv in invoices)

        currency = invoices[0].currency_id

        total_amount = self._compute_payment_amount(
            invoices=invoices, currency=currency)

        defaults.update({
            'amount': abs(total_amount),
            'currency_id': currency.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': (False if multi else
                           invoices[0].commercial_partner_id.id),
            'partner_type': (False if multi else
                             MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]),
            'communication': '',
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        return defaults

    @api.onchange('currency_id')
    def _onchange_currency(self):
        """Adding domain according to currency used"""
        res = super(AccountAbstractPayment, self)._onchange_currency() or {}
        currency = (
            self.currency_id.id
            if self.currency_id != self.env.user.company_id.currency_id
            else False)
        domain = [('type', 'in', ('bank', 'cash')),
                  ('currency_id', '=', currency)]
        res['domain'] = {'journal_id': domain}

        # Doesn't take the first available journal of selected currency as the
        # default one
        res.get('value', {}).pop('journal_id', None)

        # If current journal doesn't match selected currency, clear it
        if self.journal_id.currency_id.id != currency:
            self.journal_id = False

        return res

    def _compute_journal_domain_and_types(self):
        """This is to avoid any journal to be set automatically"""
        res = super(AccountAbstractPayment,
                    self)._compute_journal_domain_and_types()
        res['journal_types'].update([False])
        return res
