# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=api-one-deprecated

import json

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('l10n_mx_edi_origin', 'amount_total')
    def _compute_amount_advances(self):
        for record in self.filtered(
                lambda i: i.company_id.l10n_mx_edi_advance == 'A' and
                i.type == 'out_invoice' and i.l10n_mx_edi_origin and
                i.l10n_mx_edi_origin.startswith('07')):
            if record.state == 'draft':
                adv_amount, _partial_amount, _lines, _reverse_lines, _partial_line = record._l10_mx_edi_prepare_advance_refund_fields()  # noqa
            else:
                credit_note = record.refund_invoice_ids.filtered(
                    lambda i: i._l10n_mx_edi_get_advance_uuid_related() and
                    i.state not in ('draft', 'cancel'))
                adv_amount = sum(credit_note.mapped('amount_total'))
            record.l10n_mx_edi_amount_advances = adv_amount
            record.l10n_mx_edi_amount_residual_advances = record.amount_total - adv_amount  # noqa

    l10n_mx_edi_amount_residual_advances = fields.Monetary(
        'Amount residual with advances', compute='_compute_amount_advances',
        help='save the amount that will be applied as advance when validate '
        'the invoice')
    l10n_mx_edi_amount_advances = fields.Monetary(
        'Amount in advances', compute='_compute_amount_advances',
        help='save the amount that will be applied as advance when validate '
        'the invoice')

    @api.one
    def _get_outstanding_info_JSON(self):
        res = super(AccountInvoice, self)._get_outstanding_info_JSON()
        if self.state != 'draft' or self.type != 'out_invoice':
            return res
        domain = self._l10n_mx_edi_get_advance_aml_domain()
        domain.extend([('invoice_id.state', '=', 'paid')])
        related_advs = self._l10n_mx_edi_get_advance_uuid_related()
        for uuid in related_advs:
            domain.extend([('invoice_id.l10n_mx_edi_cfdi_uuid', 'not like', uuid)])
        lines = self.env['account.move.line'].search(domain)
        if not lines:
            return res
        info = {'title': _('Outstanding credits as Advance'),
                'outstanding': True,
                'content': [],
                'invoice_id': self.id}
        currency_id = self.currency_id
        for line in lines:
            # get the outstanding residual value in invoice currency
            if line.currency_id and line.currency_id == currency_id:
                amount_to_show = abs(line.amount_residual_currency)
            else:
                currency = line.company_id.currency_id
                amount_to_show = currency._convert(
                    abs(line.amount_residual), currency_id, self.company_id,
                    line.date or fields.Date.today())
            taxes = line.tax_ids.compute_all(
                amount_to_show, line.currency_id or line.company_id.currency_id, 1)['taxes']
            amount_to_show += sum([tax.get('amount') for tax in taxes])
            if float_is_zero(
                    amount_to_show, precision_rounding=currency_id.rounding):
                continue
            info['content'].append({
                'journal_name': line.ref or line.move_id.name,
                'amount': amount_to_show,
                'currency': currency_id.symbol,
                'id': line.id,
                'position': currency_id.position,
                'digits': [69, currency_id.decimal_places], })
        if not info['content']:
            return res
        self.outstanding_credits_debits_widget = json.dumps(info)
        self.has_outstanding = True
        return res

    @api.multi
    def assign_outstanding_credit(self, credit_aml_id):
        """Related an advance to the invoice."""
        res = super(AccountInvoice, self).assign_outstanding_credit(credit_aml_id)
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        advance = credit_aml.invoice_id
        for invoice in self.filtered(lambda r: r.state == 'draft'):
            invoice.l10n_mx_edi_origin = invoice._set_cfdi_origin(
                '07', [advance.l10n_mx_edi_cfdi_uuid])
            if invoice.company_id.l10n_mx_edi_advance != 'B':
                continue
            if credit_aml.currency_id and credit_aml.currency_id == invoice.currency_id:  # noqa
                amount = abs(credit_aml.amount_residual_currency)
            else:
                currency = credit_aml.company_id.currency_id
                amount = currency._convert(
                    abs(credit_aml.amount_residual), invoice.currency_id,
                    invoice.company_id, credit_aml.date or fields.Date.today())
            if amount > invoice.amount_untaxed:
                amount = invoice.amount_untaxed
            adv_text = ' - CFDI por remanente de un anticipo'
            invoice_total = invoice.amount_untaxed
            for line in invoice.invoice_line_ids:
                total_discount = amount / invoice_total * line.price_subtotal
                line.write({
                    'name': '%s%s' % (
                        line.name.replace(adv_text, ''), adv_text),
                    'l10n_mx_edi_total_discount': total_discount + line.l10n_mx_edi_total_discount,
                })
            invoice.compute_taxes()
        return res

    def _l10n_mx_edi_is_advance(self):
        """Check if an invoice is an advance"""
        self.ensure_one()
        if self.type != 'out_invoice' or len(self.invoice_line_ids) != 1:
            return False
        advance_product = self.company_id.l10n_mx_edi_product_advance_id
        product = self.invoice_line_ids.product_id
        if not product or product.id != advance_product.id:
            return False
        return True

    def _l10n_mx_edi_get_advance_uuid_related(self):
        """return the advance's uuid applied"""
        self.ensure_one()
        related_docs = self.get_cfdi_related()
        if related_docs.get('type') == '07':
            return related_docs.get('related', [])
        return []

    def _l10n_mx_edi_get_advance_aml_domain(self):
        """Get domain for available advances"""
        self.ensure_one()
        adv_prod = self.company_id.l10n_mx_edi_product_advance_id
        financial_partner = self.partner_id._find_accounting_partner(
            self.partner_id)
        domain = [('account_id', '=', adv_prod.property_account_income_id.id),
                  ('partner_id', '=', financial_partner.id),
                  ('reconciled', '=', False),
                  '|', ('amount_residual', '!=', 0.0),
                  ('amount_residual_currency', '!=', 0.0),
                  ('credit', '>', 0), ('debit', '=', 0)]
        return domain

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        """Set values when the invoice is an advance"""
        res = super(AccountInvoice, self)._onchange_invoice_line_ids()
        if not self._l10n_mx_edi_is_advance():
            return res
        self.update({
            'payment_term_id': self.env.ref(
                'account.account_payment_term_immediate'),
            'l10n_mx_edi_origin': False,
        })
        self.invoice_line_ids.name = 'Anticipo del bien o servicio'
        return res

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self._l10n_mx_edi_is_advance:
            self._onchange_invoice_line_ids()
        return res

    @api.multi
    def invoice_validate(self):
        """Create the credit note for advances and reconcile it with
        the invoice (only when this one has advances and it's signed).
        """
        has_advance = self.filtered(lambda r: r.type == 'out_invoice' and
                                    r.company_id.l10n_mx_edi_advance == 'A' and
                                    r._l10n_mx_edi_get_advance_uuid_related())
        advance_b = self.filtered(lambda r: r.type == 'out_invoice' and
                                  r.company_id.l10n_mx_edi_advance == 'B' and
                                  r._l10n_mx_edi_get_advance_uuid_related())
        res = super(AccountInvoice, has_advance.with_context(
            disable_after_commit=True)).invoice_validate()
        res = super(AccountInvoice, self - has_advance).invoice_validate()
        message = _(
            'This invoice cannot be validated because has an advance related '
            'and the CFDI stamped return an error, please fix the errors in '
            'the CFDI generation and try again.')
        for inv in has_advance:
            if inv.l10n_mx_edi_pac_status != 'signed':
                inv.message_post(body=message)
                inv.action_invoice_cancel()
                inv.action_invoice_draft()
                inv.l10n_mx_edi_origin = ''
                continue
            adv_amount, _partial_amount, lines, _reverse_lines, _partial_line = inv._l10_mx_edi_prepare_advance_refund_fields()  # noqa
            if not adv_amount:
                inv.message_post(body=_(
                    '<p>The credit note was not created because the advance '
                    'was used in another invoice or it is not in this '
                    'system.</p>'
                    '<p>So please, follow one of these actions:</p>'
                    '<li>Cancel this invoice and remove the related advance.'
                    '</li><li>Create the credit note manually.</li>'))
                continue
            refund = self.env['account.invoice.refund'].with_context(
                active_ids=inv.ids).create({
                    'filter_refund': 'cancel',
                    'description': 'Aplicación de anticipos',
                    'date': inv.date_invoice, })
            refund = refund.invoice_refund()
            inv.refund_invoice_ids.write({'l10n_mx_edi_origin': '07|%s' % inv.l10n_mx_edi_cfdi_uuid})
            account = inv.company_id.l10n_mx_edi_product_advance_id.property_account_income_id
            moves = inv.refund_invoice_ids.move_id.line_ids.filtered(lambda line: line.account_id == account)
            moves |= lines.filtered(lambda line: line.account_id == account)
            moves.reconcile()
            inv.message_post_with_view(
                'l10n_mx_edi_advance.l10n_mx_edi_message_advance_refund',
                values={'self': inv, 'origin': inv.refund_invoice_ids},
                subtype_id=self.env.ref('mail.mt_note').id)
        for inv in advance_b:
            adv_amount, _partial_amount, lines, reverse_lines, _partial_line = inv._l10_mx_edi_prepare_advance_refund_fields()  # noqa
            aml_obj = inv.move_id.line_ids.with_context(check_move_validity=False, recompute=False)
            account = inv.company_id.l10n_mx_edi_product_advance_id.categ_id.property_account_income_categ_id or inv.company_id.l10n_mx_edi_product_advance_id.property_account_income_id  # noqa
            move_line_dict = {
                'name': _('Advance'),
                'move_id': inv.move_id,
                'company_id': inv.company_id,
                'quantity': 1,
                'debit': 0,
                'credit': inv.currency_id._convert(
                    adv_amount, inv.company_id.currency_id, inv.company_id, inv.date_invoice),
                'account_id': account.id,
                'invoice_id': inv,
                'partner_id': inv.partner_id,
                'currency_id': inv.currency_id if inv.currency_id != inv.company_id.currency_id else False,
                'amount_currency': -adv_amount if inv.currency_id != inv.company_id.currency_id else 0,
            }
            first_line = aml_obj.new(move_line_dict)
            first_line = aml_obj._convert_to_write(first_line._cache)
            aml_obj.create(first_line)
            move_line_dict.update({
                'debit': inv.currency_id._convert(
                    adv_amount, inv.company_id.currency_id, inv.company_id, inv.date_invoice),
                'credit': 0,
                'account_id': inv.company_id.l10n_mx_edi_product_advance_id.property_account_income_id,
                'amount_currency': adv_amount if inv.currency_id != inv.company_id.currency_id else 0,
            })
            second_line = aml_obj.new(move_line_dict)
            second_line = aml_obj._convert_to_write(second_line._cache)
            second_line = aml_obj.create(second_line)
            inv.finalize_invoice_move_lines(second_line | reverse_lines)
            (second_line | reverse_lines).reconcile()
        return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        """Assign values for a CFDI credit note and advance
            - CFDI origin.
            - Payment method
            - Usage: 'G02' - returns, discounts or bonuses.
        """
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if not invoice.l10n_mx_edi_is_required():
            return values
        if not invoice.l10n_mx_edi_cfdi_uuid:
            raise UserError(_('The invoice is not signed, and the UUID is '
                              'required to relate the documents.'))
        values.update({
            'l10n_mx_edi_payment_method_id':
            invoice.l10n_mx_edi_payment_method_id.id,
            'l10n_mx_edi_usage': 'G02',
        })
        adv_amount, _partial_amount, lines, _reverse_lines, _partial_line = invoice._l10_mx_edi_prepare_advance_refund_fields()  # noqa
        if (invoice.refund_invoice_ids or not adv_amount or
                not invoice._l10n_mx_edi_get_advance_uuid_related()):
            return values
        adv_prod = self.company_id.l10n_mx_edi_product_advance_id
        values['l10n_mx_edi_payment_method_id'] = self.env.ref(
            'l10n_mx_edi.payment_method_anticipos').id
        advances = lines.mapped('invoice_id')
        if not advances:
            return values
        # merge advance lines (when the inv has multi-advance)
        line = self._refund_cleanup_lines(advances[0].invoice_line_ids)
        line_values = line[0][2]
        taxes = advances[0].tax_line_ids.mapped('tax_id')
        percentage = sum(tax.amount for tax in taxes if not tax.price_include)
        price_unit = adv_amount * 100 / (100 + percentage)
        line_values.update({
            'name': 'Aplicación de anticipo',
            'price_unit': price_unit,
            'account_id': adv_prod.property_account_income_id.id,
        })
        values['invoice_line_ids'] = [(0, 0, line_values)]
        # update amount in tax lines
        tax_obj = self.env['account.tax']
        tax_line_ids = self._refund_cleanup_lines(advances[0].tax_line_ids)
        tax_line_ids = [values[2] for values in tax_line_ids]
        for tax_values in tax_line_ids:
            tax = tax_obj.search([
                ('id', '=', tax_values.get('tax_id'))])
            res = tax.compute_all(
                price_unit, invoice.currency_id, 1, adv_prod,
                invoice.partner_id)['taxes'][0]
            tax_values.update({
                'base': res['base'],
                'amount': res['amount'],
                'amount_total': res['amount'],
                'currency_id': invoice.currency_id.id,
            })
        values['tax_line_ids'] = [(0, 0, values) for values in tax_line_ids]
        return values

    @api.multi
    @api.returns('self')
    def advance(self, partner, amount, currency):
        """Create an advance"""
        values = {
            'partner_id': partner.id,
            'currency_id': currency.id,
            'type': 'out_invoice',
            'payment_term_id': self.env.ref(
                'account.account_payment_term_immediate').id,
            'l10n_mx_edi_origin': False,
        }
        advance = self.create(values)
        product = advance.company_id.l10n_mx_edi_product_advance_id
        prod_accounts = product.product_tmpl_id.get_product_accounts()
        advance.invoice_line_ids.create({
            'product_id': product.id,
            'name': 'Anticipo del bien o servicio',
            'account_id': prod_accounts['income'].id,
            'uom_id': product.uom_id.id,
            'quantity': 1,
            'price_unit': 0.0,
            'invoice_id': advance.id,
        })
        ctx = {
            'type': advance.type,
            'journal_id': advance.journal_id.id,
            'default_invoice_id': advance.id}
        advance.with_context(ctx).invoice_line_ids._set_taxes()
        # get amount for price unit if there is a tax
        taxes = advance.invoice_line_ids.invoice_line_tax_ids
        percentage = sum(tax.amount for tax in taxes if not tax.price_include)
        price_unit = amount * 100 / (100 + percentage)
        advance.invoice_line_ids.price_unit = price_unit
        advance.invoice_line_ids.price_tax = amount - price_unit
        advance.invoice_line_ids._compute_price()
        advance._onchange_invoice_line_ids()
        advance._compute_amount()
        return advance

    def _l10_mx_edi_prepare_advance_refund_fields(self):
        """ Helper function to get the amounts and amls to apply in the
        credit note for the advances
        """
        self.ensure_one()
        adv_amount = partial_amount = 0.0
        reverse_lines = self.env['account.move.line']
        partial_line = reverse_lines
        domain = self._l10n_mx_edi_get_advance_aml_domain()
        related_advs = self._l10n_mx_edi_get_advance_uuid_related()
        for uuid in related_advs:
            if uuid != related_advs[-1]:
                domain.extend('|')
            domain.extend([('invoice_id.l10n_mx_edi_cfdi_uuid', 'like', uuid)])
        lines = self.env['account.move.line'].search(domain)
        if not lines:
            return adv_amount, partial_amount, lines, reverse_lines, partial_line  # noqa
        for line in lines:
            if adv_amount >= self.amount_total:
                break
            # get the outstanding residual value in invoice currency
            if line.currency_id and line.currency_id == self.currency_id:
                amount = abs(line.amount_residual_currency)
            else:
                currency = line.company_id.currency_id
                amount = currency._convert(
                    abs(line.amount_residual), self.currency_id,
                    self.company_id, line.date or fields.Date.today())
                if float_is_zero(
                        amount, precision_rounding=self.currency_id.rounding):
                    continue
            adv_amount += amount
            if self.company_id.l10n_mx_edi_advance != 'B':
                taxes = line.tax_ids.compute_all(
                    amount, line.currency_id or line.company_id.currency_id, 1)['taxes']
                adv_amount += sum([tax.get('amount') for tax in taxes])
            adv_discount = 0
            if self.company_id.l10n_mx_edi_advance == 'B':
                adv_discount = self.l10n_mx_edi_total_discount
            reverse_lines |= line
            if adv_amount > self.amount_total + adv_discount:
                partial_amount = adv_amount - self.amount_total + adv_discount
                adv_amount = self.amount_total + adv_discount
                partial_line = line
        return adv_amount, partial_amount, lines, reverse_lines, partial_line
