# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _
from odoo.tools.xml_utils import _check_with_xsd

import logging
import re
import base64
import json
import requests
import random
import string

from lxml import etree
from lxml.objectify import fromstring
from datetime import datetime
from io import BytesIO
from zeep import Client
from zeep.transports import Transport
from json.decoder import JSONDecodeError

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        ''' Doesn't check if the config is correct so you need to call _l10n_mx_edi_check_config first.

        :param invoice:
        :return:
        '''

        cfdi_values = {
            **self._l10n_mx_edi_get_common_cfdi_values(invoice),
            'document_type': 'I' if invoice.move_type == 'out_invoice' else 'E',
            'currency_name': invoice.currency_id.name,
            'payment_method_code': (invoice.l10n_mx_edi_payment_method_id.code or '').replace('NA', '99'),
            'payment_policy': invoice.l10n_mx_edi_payment_policy,
        }

        # ==== Invoice Values ====

        invoice_lines = invoice.invoice_line_ids.filtered(lambda inv: not inv.display_type)

        if invoice.currency_id == invoice.company_currency_id:
            cfdi_values['currency_conversion_rate'] = None
        elif invoice.active_manual_currency_rate and invoice.manual_currency_exchange_rate:
            sign = 1 if invoice.move_type in ('out_invoice', 'out_receipt', 'in_refund') else -1
            cfdi_values['currency_conversion_rate'] = sign * invoice.inverse_currency_rate
        else:
            sign = 1 if invoice.move_type in ('out_invoice', 'out_receipt', 'in_refund') else -1
            total_amount_currency = sign * invoice.amount_total
            total_balance = invoice.amount_total_signed
            cfdi_values['currency_conversion_rate'] = total_balance / total_amount_currency

        if invoice.partner_bank_id:
            digits = [s for s in invoice.partner_bank_id.acc_number if s.isdigit()]
            acc_4number = ''.join(digits)[-4:]
            cfdi_values['account_4num'] = acc_4number if len(acc_4number) == 4 else None
        else:
            cfdi_values['account_4num'] = None

        if cfdi_values['customer'].country_id.l10n_mx_edi_code != 'MEX' and cfdi_values['customer_rfc'] not in ('XEXX010101000', 'XAXX010101000'):
            cfdi_values['customer_fiscal_residence'] = cfdi_values['customer'].country_id.l10n_mx_edi_code
        else:
            cfdi_values['customer_fiscal_residence'] = None

        # ==== Invoice lines ====

        cfdi_values['invoice_line_values'] = []
        for line in invoice_lines:
            cfdi_values['invoice_line_values'].append(self._l10n_mx_edi_get_invoice_line_cfdi_values(invoice, line))

        # ==== Totals ====

        cfdi_values['total_amount_untaxed_wo_discount'] = sum(vals['total_wo_discount'] for vals in cfdi_values['invoice_line_values'])
        cfdi_values['total_amount_untaxed_discount'] = sum(vals['discount_amount'] for vals in cfdi_values['invoice_line_values'])

        # ==== Taxes ====

        cfdi_values['tax_details_transferred'] = {}
        cfdi_values['tax_details_withholding'] = {}
        for vals in cfdi_values['invoice_line_values']:
            for tax_res in vals['tax_details_transferred']:
                cfdi_values['tax_details_transferred'].setdefault(tax_res['tax'], {
                    'tax': tax_res['tax'],
                    'tax_type': tax_res['tax_type'],
                    'tax_amount': tax_res['tax_amount'],
                    'tax_name': tax_res['tax_name'],
                    'total': 0.0,
                })
                cfdi_values['tax_details_transferred'][tax_res['tax']]['total'] += tax_res['total']
            for tax_res in vals['tax_details_withholding']:
                cfdi_values['tax_details_withholding'].setdefault(tax_res['tax'], {
                    'tax': tax_res['tax'],
                    'tax_type': tax_res['tax_type'],
                    'tax_amount': tax_res['tax_amount'],
                    'tax_name': tax_res['tax_name'],
                    'total': 0.0,
                })
                cfdi_values['tax_details_withholding'][tax_res['tax']]['total'] += tax_res['total']

        cfdi_values['tax_details_transferred'] = list(cfdi_values['tax_details_transferred'].values())
        cfdi_values['tax_details_withholding'] = list(cfdi_values['tax_details_withholding'].values())
        cfdi_values['total_tax_details_transferred'] = sum(vals['total'] for vals in cfdi_values['tax_details_transferred'])
        cfdi_values['total_tax_details_withholding'] = sum(vals['total'] for vals in cfdi_values['tax_details_withholding'])

        return cfdi_values

    # -------------------------------------------------------------------------
    # CFDI Generation: Payments
    # -------------------------------------------------------------------------

    def _l10n_mx_edi_export_payment_cfdi(self, move):
        ''' Create the CFDI attachment for the journal entry passed as parameter being a payment used to pay some
        invoices.

        :param move:    An account.move record.
        :return:        A dictionary with one of the following key:
        * cfdi_str:     A string of the unsigned cfdi of the invoice.
        * error:        An error if the cfdi was not successfuly generated.
        '''

        invoice_vals_list = []
        for partial, amount, invoice_line in move._get_reconciled_invoices_partials():
            invoice = invoice_line.move_id

            if not invoice.l10n_mx_edi_cfdi_request:
                continue

            invoice_vals_list.append({
                'invoice': invoice,
                'exchange_rate': invoice.amount_total / abs(invoice.amount_total_signed),
                'payment_policy': invoice.l10n_mx_edi_payment_policy,
                'number_of_payments': len(invoice._get_reconciled_payments()) + len(invoice._get_reconciled_statement_lines()),
                'amount_paid': amount,
                **self._l10n_mx_edi_get_serie_and_folio(invoice),
            })

        mxn_currency = self.env["res.currency"].search([('name', '=', 'MXN')], limit=1)
        if move.currency_id == mxn_currency:
            rate_payment_curr_mxn = None
        else:
            rate_payment_curr_mxn = move.currency_id._convert(1.0, mxn_currency, move.company_id, move.date, round=False)

        payment_method_code = move.l10n_mx_edi_payment_method_id.code
        is_payment_code_emitter_ok = payment_method_code in ('02', '03', '04', '05', '06', '28', '29', '99')
        is_payment_code_receiver_ok = payment_method_code in ('02', '03', '04', '05', '28', '29', '99')
        is_payment_code_bank_ok = payment_method_code in ('02', '03', '04', '28', '29', '99')

        partner_bank = move.partner_bank_id.bank_id
        if not partner_bank.country or partner_bank.country.code != 'MX':
            partner_bank_vat = 'XEXX010101000'
        else:
            partner_bank_vat = partner_bank.l10n_mx_edi_vat

        payment_account_ord = re.sub(r'\s+', '', move.partner_bank_id.acc_number or '') or None
        payment_account_receiver = re.sub(r'\s+', '', move.journal_id.bank_account_id.acc_number or '') or None

        receivable_lines = move.line_ids.filtered(lambda line: line.account_internal_type == 'receivable')
        currencies = receivable_lines.mapped('currency_id')
        amount = abs(sum(receivable_lines.mapped('amount_currency')) if len(currencies) == 1 else sum(receivable_lines.mapped('balance')))

        cfdi_values = {
            **self._l10n_mx_edi_get_common_cfdi_values(move),
            'invoice_vals_list': invoice_vals_list,
            'currency': currencies[0] if len(currencies) == 1 else move.currency_id,
            'amount': amount,
            'rate_payment_curr_mxn': rate_payment_curr_mxn,
            'emitter_vat_ord': is_payment_code_emitter_ok and partner_bank_vat,
            'bank_vat_ord': is_payment_code_bank_ok and partner_bank.name,
            'payment_account_ord': is_payment_code_emitter_ok and payment_account_ord,
            'receiver_vat_ord': is_payment_code_receiver_ok and move.journal_id.bank_account_id.bank_id.l10n_mx_edi_vat,
            'payment_account_receiver': is_payment_code_receiver_ok and payment_account_receiver,
        }

        cfdi_payment_datetime = datetime.combine(fields.Datetime.from_string(move.date), datetime.strptime('12:00:00', '%H:%M:%S').time())
        cfdi_values['cfdi_payment_date'] = cfdi_payment_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        if cfdi_values['customer'].country_id.l10n_mx_edi_code != 'MEX':
            cfdi_values['customer_fiscal_residence'] = cfdi_values['customer'].country_id.l10n_mx_edi_code
        else:
            cfdi_values['customer_fiscal_residence'] = None

        cfdi = self.env.ref('l10n_mx_edi.payment10')._render(cfdi_values)

        decoded_cfdi_values = move._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi)
        cfdi_cadena_crypted = cfdi_values['certificate'].sudo().get_encrypted_cadena(decoded_cfdi_values['cadena'])
        decoded_cfdi_values['cfdi_node'].attrib['Sello'] = cfdi_cadena_crypted

        return {
            'cfdi_str': etree.tostring(decoded_cfdi_values['cfdi_node'], pretty_print=True, xml_declaration=True, encoding='UTF-8'),
        }
