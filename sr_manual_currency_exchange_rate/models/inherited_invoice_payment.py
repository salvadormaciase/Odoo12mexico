# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import models, fields, api, _
from itertools import groupby

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund':-1,
    'in_invoice':-1,
    'out_refund': 1,
}


class AccountPayments(models.Model):
    _inherit = 'account.payment'

    apply_manual_currency_exchange = fields.Boolean(string='Apply Manual Currency Exchange')
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate')
    active_manual_currency_rate = fields.Boolean('active Manual Currency', default=False)

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(AccountPayments, self)._onchange_journal()
        # Custom Code by Sitaram Solutions Start
        self.currency_id = self.invoice_ids and self.invoice_ids[0].currency_id.id
        # Custom Code by Sitaram Solutions end
        return res
        
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        # Custom method by Sitaram Solutions
        if self.currency_id:
            if self.company_id.currency_id != self.currency_id:
                self.active_manual_currency_rate = True
            else:
                self.active_manual_currency_rate = False
        else:
            self.active_manual_currency_rate = False

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayments, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
            # Custom Code by Sitaram Solutions Start
            rec['active_manual_currency_rate'] = invoice['active_manual_currency_rate']
            rec['apply_manual_currency_exchange'] = invoice['apply_manual_currency_exchange']
            rec['manual_currency_exchange_rate'] = invoice['manual_currency_exchange_rate']
            # Custom Code by Sitaram Solutions End
        return rec


    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        '''Compute the total amount for the payment wizard.

        :param invoices: If not specified, pick all the invoices.
        :param currency: If not specified, search a default currency on wizard/journal.
        :return: The total amount to pay the invoices.
        '''

        # Get the payment invoices
        if not invoices:
            invoices = self.invoice_ids

        # Get the payment currency
        if not currency:
            currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoices and invoices[0].currency_id

        # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
        total = 0.0
        groups = groupby(invoices, lambda i: i.currency_id)
        for payment_currency, payment_invoices in groups:
            amount_total = sum([MAP_INVOICE_TYPE_PAYMENT_SIGN[i.type] * i.residual_signed for i in payment_invoices])
            if payment_currency == currency:
                total += amount_total
            else:
                #Custom code by sitaram solution start
                if self.active_manual_currency_rate and self.apply_manual_currency_exchange:
                    total += amount_total / self.manual_currency_exchange_rate
                #Custom code by sitaram solution end
                else:
                    total += payment_currency._convert(amount_total, currency, self.env.user.company_id, self.payment_date or fields.Date.today())
        return total


    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        #custom code by sitaram solutions start
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date, manual_rate=self.manual_currency_exchange_rate, active_manual_currency=self.apply_manual_currency_exchange,)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        #custom code by sitaram solutions end
        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date,  manual_rate=self.invoice_ids[0].manual_currency_exchange_rate, active_manual_currency=self.invoice_ids[0].apply_manual_currency_exchange)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)

        return move


