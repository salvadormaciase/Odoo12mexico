import logging

from datetime import date as dt, datetime

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


def s2d(date):
    return fields.Date.from_string(date) if isinstance(date, str) else date


def d2s(date):
    return fields.Date.to_string(date) if isinstance(date, (datetime, dt)) else date  # noqa


def get_day_one(date):
    date = s2d(date)
    return dt(date.year, date.month, 1)


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.depends('realization_move_ids')
    def _compute_realization_move_ids_nbr(self):
        for rec in self:
            rec.realization_move_ids_nbr = len(rec.realization_move_ids)

    def _compute_revaluation_ledger_ids_nbr(self):
        realizable_account = self.filtered(lambda x: x.realizable_account)
        for inv in realizable_account:
            inv.revaluation_ledger_ids_nbr = len(inv.revaluation_ledger_ids)

    realizable_account = fields.Boolean(
        help='When wizard for Monetary Realization is run this account will '
        'be considere for realization')
    realization_move_ids_nbr = fields.Integer(
        compute='_compute_realization_move_ids_nbr',
        string='# of Realization Entries',
        help='Quantity of Realization Entries this Account has')
    realization_move_ids = fields.One2many(
        'account.move',
        'realization_account_id',
        string='Realization Entries',
        readonly=True,
        help='Realization Journal Entries for this Account')
    revaluation_ledger_ids_nbr = fields.Integer(
        compute='_compute_revaluation_ledger_ids_nbr',
        string='# of Revaluation Ledger Items',
        help='Quantity of Revaluation Ledger Items this Invoice has')
    revaluation_ledger_ids = fields.One2many(
        'account.revaluation.ledger',
        'account_id',
        domain=[('invoice_id', '=', False)],
        readonly=True,
        help='Ledger of Revaluation for this Invoice')
    date_last_ledger = fields.Date(
        'Last Ledger Date',
        help='Date on which last ledger was created')

    @api.multi
    def action_view_realization_move(self):

        if self._context.get('realization_move'):
            action = self.env.ref('account.action_move_line_form').read()[0]
            record_ids = self.realization_move_ids.ids
        if self._context.get('revaluation_ledger'):
            action = self.env.ref(
                'gandalf.action_account_revaluation_ledger').read()[0]
            record_ids = self.revaluation_ledger_ids.ids

        action['domain'] = [('id', 'in', record_ids)]

        if len(record_ids) == 1:
            action['res_id'] = record_ids[0]
            action['view_mode'] = 'form'
        return action

    @api.model
    def get_fx_on_account(self, date, previous_cumulative_fx):
        self.ensure_one()
        aml_obj = self.env['account.move.line']
        company_currency_id = self.company_id.currency_id
        journal_ids = (
            self.company_id.account_realization_journal_id |
            self.company_id.currency_exchange_journal_id).ids

        # /!\ TODO: @hbto change this to readgroup
        cur_ids = (
            self.env['res.currency'].search([])
            .filtered(lambda x: x.id != company_currency_id.id))

        domain = [
            ('account_id', '=', self.id),
            ('journal_id', 'not in', journal_ids),
            ('date', '<=', date), ]

        initial_balance = reevaluated_balance = foreign_balance = 0
        for cur_id in cur_ids:
            aml_ids = aml_obj.search(
                domain + [('currency_id', '=', cur_id.id)])
            initial_balance += sum(aml_ids.mapped('balance'))
            currency_balance = sum(aml_ids.mapped('amount_currency'))
            # /!\ NOTE: Normalizing balance on currency account
            foreign_balance += cur_id._convert(
                currency_balance, self.currency_id,
                self.company_id, date)
            reevaluated_balance += cur_id._convert(
                currency_balance, company_currency_id,
                self.company_id, date)

        cumulative_fx = self.company_id.currency_id.round(
            reevaluated_balance - initial_balance)
        return dict(
            date=date,
            cumulative_fx=cumulative_fx,
            account_id=self.id,
            balance=initial_balance,
            foreign_balance=foreign_balance,
            reevaluated_balance=reevaluated_balance,
            fx_amount=cumulative_fx - previous_cumulative_fx,
        )

    @api.multi
    def create_account_realization_ledger(self, dates):
        self.ensure_one()
        arl_obj = self.env['account.revaluation.ledger']
        min_date = min(dates)
        cumulative_fx = arl_obj.get_previous_cumulative_fx(
            min_date, self.id, False)
        arl_obj.remove_revaluation_ledger(min_date, self.id, False)
        for date in dates:
            fx_dict = self.get_fx_on_account(date, cumulative_fx)
            cumulative_fx = fx_dict.get('cumulative_fx', 0.0)
            arl_obj.create(fx_dict)
        self.write({'date_last_ledger': max(dates)})

    @api.multi
    def realize_account_ledger(self, dates):
        self.ensure_one()
        self.create_account_realization_ledger(dates)

    @api.multi
    def realize_account_entry(self, dates):
        self.ensure_one()
        arl_obj = self.env['account.revaluation.ledger']
        arl_obj.create_revaluation_move(dates, account_id=self)

    @api.multi
    def realize_account(
            self, stop_date, init_date, do_ledger=True, do_entry=None,
            do_commit=False):
        self.ensure_one()

        arl_obj = self.env['account.revaluation.ledger']
        dates = arl_obj.get_dates(
            init_date, 'open', {init_date}, stop_date, init_date, False)
        if not dates:
            return

        # /!\ NOTE: do_entry is a wild card that can be used by technical
        # people to override the way Journal Entries are created.
        if do_entry is None:
            do_entry = self.company_id.create_realization_entry_on_accounts

        with self.env.norecompute():
            if do_ledger:
                self.realize_account_ledger(dates)
            if do_entry:
                self.realize_account_entry(dates)
        self.recompute()

        if do_commit:
            # pylint: disable=invalid-commit
            self._cr.commit()
        return

    @api.multi
    def create_realization_entries(
            self, stop_date=False, init_date=False, do_ledger=True,
            do_entry=None, do_commit=False):

        if not self.ids:
            return
        _logger.info('Entering method `create_realization_entries`')

        stop_date = fields.Date.today() if not stop_date else stop_date
        stop_date = s2d(stop_date)

        if not init_date:
            # /!\ NOTE: if not init_date is set it will be set at the first day
            # of the month of stop_date.
            init_date = get_day_one(stop_date)
        init_date = s2d(init_date)

        count = 0
        total = len(self)
        for acc in self:
            count += 1
            _logger.info(
                'Processing acc_id: %(acc_id)s - %(count)s / %(total)s',
                {'acc_id': acc.id, 'count': count, 'total': total})
            if not acc.realizable_account:
                continue
            if acc.deprecated:
                continue
            if not acc.currency_id:
                continue
            if acc.currency_id == acc.company_id.currency_id:
                continue
            acc.realize_account(
                stop_date, init_date, do_ledger=do_ledger, do_entry=do_entry,
                do_commit=do_commit)
