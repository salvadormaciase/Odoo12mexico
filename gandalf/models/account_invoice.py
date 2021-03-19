from datetime import date as dt
import logging

from odoo import models, fields, api
from odoo.tools import float_is_zero

from .account import s2d, get_day_one

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_realization_move_ids_nbr(self):
        for inv in self:
            inv.realization_move_ids_nbr = len(inv.realization_move_ids)

    @api.depends('realization_move_ids')
    def _compute_realization_move_ids(self):
        def check_full_revaluation(date, account_id, inv_id):
            rounding = inv_id.company_id.currency_id.rounding
            ledger = arl_obj.get_cumulative_fx_at_date(
                date, account_id, inv_id.id)
            booked = sum(
                self
                .mapped('realization_move_ids.line_ids')
                .filtered(
                    lambda x: x.date <= date and
                    x.account_id.id == account_id).mapped('balance'))
            return float_is_zero(ledger - booked, precision_rounding=rounding)
        res = {}
        arl_obj = self.env['account.revaluation.ledger']

        for inv in self:
            res[inv] = {}
            journal_id = inv.company_id.currency_exchange_journal_id
            move_ids = inv.realization_move_ids
            pay_ids = inv.payment_move_line_ids
            date = max(move_ids.mapped('date') or [dt.min])

            pay_date = max(
                (inv.move_id.line_ids | pay_ids)
                .filtered(lambda x: x.journal_id != journal_id)
                .mapped('date') or [dt.min])

            res[inv]['date_last_realization'] = date

            # /!\ NOTE: An invoice is to be considered fully realized if all
            # the following conditions are met:
            # - It is paid or cancelled.
            # - It has payments
            # - It has realization entries
            # - It yields same values for ledger and booked realization
            # - Its Last realization date is equal to its last payment date or
            # invoice date. Invoice date is included because invoice date can
            # be greater than payment date.
            res[inv]['fully_realized'] = (
                inv.state in ('paid', 'cancel') and
                pay_ids and
                move_ids and
                date == pay_date and
                check_full_revaluation(pay_date, inv.account_id.id, inv))
        for inv, val in res.items():
            inv.date_last_realization = val.get('date_last_realization')
            inv.fully_realized = val.get('fully_realized')

    @api.depends('revaluation_ledger_ids')
    def _compute_revaluation_ledger_ids_nbr(self):
        for inv in self:
            ledger_ids = inv.revaluation_ledger_ids
            inv.revaluation_ledger_ids_nbr = len(ledger_ids)
            inv.date_last_ledger = max(ledger_ids.mapped('date') or [dt.min])

    realization_move_ids_nbr = fields.Integer(
        compute='_compute_realization_move_ids_nbr',
        string='# of Realization Entries',
        help='Quantity of Realization Entries this Invoice has')
    realization_move_ids = fields.One2many(
        'account.move',
        'realization_invoice_id',
        string='Realization Entries',
        readonly=True,
        help='Realization Journal Entries for this Invoice')
    revaluation_ledger_ids_nbr = fields.Integer(
        compute='_compute_revaluation_ledger_ids_nbr',
        store=True,
        string='# of Revaluation Ledger Items',
        help='Quantity of Revaluation Ledger Items this Invoice has')
    revaluation_ledger_ids = fields.One2many(
        'account.revaluation.ledger',
        'invoice_id',
        readonly=True,
        help='Ledger of Revaluation for this Invoice')
    fully_realized = fields.Boolean(
        compute='_compute_realization_move_ids',
        store=True,
        help='When all the Realization Entries for this invoice have been '
        'created this field is marked')
    date_last_realization = fields.Date(
        'Last Realization Date',
        compute='_compute_realization_move_ids',
        store=True,
        help='Date on which last realization was run')
    date_last_ledger = fields.Date(
        'Last Ledger Date',
        compute='_compute_revaluation_ledger_ids_nbr',
        store=True,
        help='Date on which last ledger was created')

    @api.multi
    def action_view_realization_move(self):

        if self._context.get('revaluation_ledger'):
            action = self.env.ref(
                'gandalf.action_account_revaluation_ledger').read()[0]
            record_ids = self.revaluation_ledger_ids.ids
        if self._context.get('realization_move'):
            action = self.env.ref('account.action_move_line_form').read()[0]
            record_ids = self.realization_move_ids.ids

        action['domain'] = [('id', 'in', record_ids)]

        if len(record_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = record_ids[0]
        return action

    @api.model
    def get_fx_on_invoice(self, to_date, previous_cumulative_fx, account_id):
        self.ensure_one()

        sign = 1 if self.type in ('in_invoice', 'out_refund') else -1
        amls = self.move_id.line_ids.filtered(
            lambda l: l.account_id.id == account_id)
        res = self.env['account.move.line'].read_group(
            [('id', 'in', amls.ids)],
            ['balance', 'amount_currency'], [], lazy=False)

        initial_balance = res[0]['balance']
        initial_currency_balance = res[0]['amount_currency']
        paid_balance = 0.0
        paid_currency_balance = 0.0
        for aml in amls:
            pay_balances = aml.get_paid_balances_at_date(to_date)
            paid_balance += pay_balances[0]
            paid_currency_balance += pay_balances[1]
        company_currency = self.company_id.currency_id
        residual_balance = initial_balance + sign * paid_balance
        residual_currency_balance = (
            initial_currency_balance + sign * paid_currency_balance)
        reevaluated_residual = self.currency_id._convert(
            residual_currency_balance, company_currency,
            self.company_id, to_date)

        cumulative_fx = company_currency.round(reevaluated_residual - residual_balance)
        residual_balance = initial_balance + sign * paid_balance
        return dict(
            date=to_date,
            invoice_id=self.id,
            cumulative_fx=cumulative_fx,
            account_id=self.account_id.id,
            balance=residual_balance,
            reevaluated_balance=reevaluated_residual,
            foreign_balance=residual_currency_balance,
            fx_amount=cumulative_fx - previous_cumulative_fx,
            partner_id=self.commercial_partner_id.id,
        )

    @api.model
    def get_fx_on_tax(self, date, previous_cumulative_fx, account_id):
        self.ensure_one()
        am_obj = self.env['account.move']
        tax_aml_ids = self.env['account.move.line']

        res = self.env['account.move.line'].read_group(
            [('id', 'in', self.move_id.line_ids.ids), ('account_id', '=', account_id)],
            ['balance', 'amount_currency'], [], lazy=False)

        journal_id = self.company_id.currency_exchange_journal_id
        sign = -1 if self.type in ('in_invoice', 'out_refund') else 1

        initial_balance = res[0]['balance']
        initial_currency_balance = res[0]['amount_currency']
        paid_balance = paid_currency_balance = 0

        inv_lines = self.move_id.line_ids.filtered(
            lambda l: l.account_id.id == self.account_id.id)

        # /!\ NOTE: We are excluding APRs with foreign exchange differences
        apr_ids = (
            inv_lines.mapped('matched_debit_ids') |
            inv_lines.mapped('matched_credit_ids')).filtered(
                lambda apr: (
                    (apr.debit_move_id in inv_lines and
                     apr.credit_move_id.journal_id != journal_id) or
                    (apr.credit_move_id in inv_lines and
                     apr.debit_move_id.journal_id != journal_id)))

        tax_aml_ids |= am_obj.search([
            ('tax_cash_basis_rec_id', 'in', apr_ids.ids)]).mapped('line_ids')
        tax_aml_ids |= self.move_id.reverse_entry_id.line_ids

        tax_aml_ids = tax_aml_ids.filtered(
            lambda l: l.account_id.id == account_id and l.date <= date)

        if sign > 0:
            tax_aml_ids = tax_aml_ids.filtered(
                lambda x: x.balance > 0 or x.amount_currency > 0)
        else:
            tax_aml_ids = tax_aml_ids.filtered(
                lambda x: x.balance < 0 or x.amount_currency < 0)

        paid_balance += sum(tax_aml_ids.mapped('balance'))
        paid_currency_balance += sum(tax_aml_ids.mapped('amount_currency'))

        company_currency_id = self.company_id.currency_id
        residual_balance = initial_balance + paid_balance
        residual_currency_balance = (
            initial_currency_balance + paid_currency_balance)
        reevaluated_residual = self.currency_id._convert(
            residual_currency_balance, company_currency_id,
            self.company_id, date)

        cumulative_fx = self.company_id.currency_id.round(
            reevaluated_residual - residual_balance)
        return dict(
            date=date,
            invoice_id=self.id,
            cumulative_fx=cumulative_fx,
            account_id=account_id,
            balance=residual_balance,
            reevaluated_balance=reevaluated_residual,
            foreign_balance=residual_currency_balance,
            fx_amount=cumulative_fx - previous_cumulative_fx,
            partner_id=self.partner_id.commercial_partner_id.id,
        )

    @api.multi
    def create_invoice_realization_ledger(self, apply, dates, account_id):
        fnc = self.get_fx_on_invoice if apply == 'inv' else self.get_fx_on_tax
        arl_obj = self.env['account.revaluation.ledger']
        min_date = min(dates)
        cumulative_fx = arl_obj.get_previous_cumulative_fx(
            min_date, account_id, self.id)
        arl_obj.remove_revaluation_ledger(min_date, account_id, self.id)
        for date in dates:
            fx_dict = fnc(date, cumulative_fx, account_id)
            cumulative_fx = fx_dict.get('cumulative_fx', 0.0)
            arl_obj.create(fx_dict)

    @api.multi
    def realize_invoice_ledger(self, dates):
        self.ensure_one()
        self.create_invoice_realization_ledger(
            'inv', dates, self.account_id.id)
        tax_account_ids = (self.move_id.line_ids.filtered(
            lambda x: x.tax_line_id.tax_exigibility == 'on_payment')
            .mapped('account_id'))
        for account in tax_account_ids:
            self.create_invoice_realization_ledger('tax', dates, account.id)

    @api.multi
    def realize_invoice_entry(self, dates):
        self.ensure_one()
        arl_obj = self.env['account.revaluation.ledger']
        arl_obj.create_revaluation_move(dates, invoice_id=self)

    @api.multi
    def realize_invoice(
            self, stop_date, init_date, do_ledger=True, do_entry=None,
            do_commit=False):
        self.ensure_one()

        arl_obj = self.env['account.revaluation.ledger']
        journal_id = self.company_id.currency_exchange_journal_id
        inv_date = self.move_id.line_ids[0].date
        dates = set(
            self.payment_move_line_ids
            .filtered(
                lambda x: x.journal_id != journal_id).mapped('date'))
        dates = arl_obj.get_dates(
            inv_date, self.state, dates, stop_date, init_date)

        if not dates:
            return

        # /!\ NOTE: do_entry is a wild card that can be used by technical
        # people to override the way Journal Entries are created.
        if do_entry is None:
            do_entry = self.company_id.create_realization_entry_on_invoices
        if (self.company_id.apply_only_on_receivable_payable and
                self.account_id.internal_type not in
                ('receivable', 'payable')):
            return

        with self.env.norecompute():
            if do_ledger:
                self.realize_invoice_ledger(dates)
            if do_entry:
                self.realize_invoice_entry(dates)
        self.recompute()

        if do_commit:
            # pylint: disable=invalid-commit
            self._cr.commit()
        return

    @api.multi
    def create_realization_entries(
            self, stop_date=False, init_date=False, do_ledger=True,
            do_entry=None, do_commit=False):

        _logger.info('Entering method `create_realization_entries`')
        if not stop_date:
            stop_date = fields.Date.today()
        stop_date = s2d(stop_date)

        # /!\ NOTE: if not init_date is set it will be set at the first day of
        # the month of stop_date
        if not init_date:
            init_date = get_day_one(stop_date)
        init_date = s2d(init_date)

        count = 0
        total = len(self)
        for inv in self:
            count += 1
            _logger.info(
                'Processing inv_id: %(inv_id)s - %(count)s / %(total)s',
                {'inv_id': inv.id, 'count': count, 'total': total})
            if inv.currency_id == inv.company_currency_id:
                continue
            if not inv.move_id:
                continue
            inv.realize_invoice(
                stop_date, init_date, do_ledger=do_ledger, do_entry=do_entry,
                do_commit=do_commit)

    @api.multi
    def action_cancel(self):
        move_ids = self.mapped('realization_move_ids')
        self.mapped('revaluation_ledger_ids').unlink()
        move_ids.mapped('line_ids').remove_move_reconcile()
        move_ids.button_cancel()
        move_ids.unlink()
        return super(AccountInvoice, self).action_cancel()
