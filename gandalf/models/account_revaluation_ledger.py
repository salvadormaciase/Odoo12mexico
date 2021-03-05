import logging

from datetime import timedelta, date as dt
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from .account import s2d, d2s, get_day_one

_logger = logging.getLogger(__name__)


class AccountRevaluationLedger(models.Model):
    _name = 'account.revaluation.ledger'
    _description = 'Keeps track of revaluations on accounts'

    date = fields.Date(help='Date of Revaluation')
    account_id = fields.Many2one(
        'account.account',
        help='Account to Reevaluate')
    invoice_id = fields.Many2one(
        'account.move',
        help='Account to Reevaluate',
        index=True)
    partner_id = fields.Many2one(
        'res.partner',
        help='Accounting Partner related to invoice')
    cumulative_fx = fields.Float(
        string='Cumulative Diff.',
        help='Cumulative Foreign Exchange Difference Amount')
    fx_amount = fields.Float(
        string='Difference',
        help='Foreign Exchange Difference Amount')
    balance = fields.Float(
        help='Non-reevaluated Balance at date')
    foreign_balance = fields.Float(
        help='Balance in Foreign Currency at date')
    reevaluated_balance = fields.Float(
        help='Reevaluated Balance at date')
    group_id = fields.Many2one(
        'account.group',
        related='account_id.group_id',
        help='Group of the Account')
    invoice_type = fields.Selection(
        related='invoice_id.move_type',
        store=True,
        readonly=True,
        help='Type of the Invoice when invoice is related to a Ledger Item')
    # /!\ TODO:  @hbto this state is to be changed to the new state in the account.move for invoices
    invoice_state = fields.Selection(
        related='invoice_id.payment_state',
        store=True,
        readonly=True,
        help='State of the Invoice when invoice is related to a Ledger Item')

    def get_dates(
            self, inv_date, inv_state, dates, stop_date, init_date=dt.min,
            is_inv=True):
        """ This method return a list of dates to be used to create realization
        entries. There are several cases that we can depict here.
        @params:
            inv_date: Accounting Date of invoice.
            inv_state: invoice state.
            dates: a set of dates for the payment of the invoice. it may
            include inv_date.
            stop_date: maximum date to be used as realization date.
            init_date: an optional date that can be passed if used all dates
            minor than it will discarded.
        @returns:
            date_range: a list of dates which will be used to create journal
            entries. if min_date and max_date spans across several months each
            final date of every month will be include in date_range. date_range
            may include inv_date when a payment_date is minor than inv_date.
            date_range will an empty list in the event of min_date and max_date
            being minor than init_date. Paid or Cancel Invoices max_date cannot
            be greater than stop_date. On Open Invoices stop date will be the
            max_date.
        !!! TODO: @hbto finish documentation of this method by providing an
        example
        """
        inv_date, stop_date, init_date = [
            s2d(x) for x in [inv_date, stop_date, init_date]]

        dates = {s2d(x) for x in dates}

        skip_check = False
        if is_inv:
            pay_min_date = min(dates) if dates else False
            month_end = get_day_one(inv_date) + relativedelta(months=1, days=-1)  # noqa
            skip_check = (not pay_min_date or inv_date < pay_min_date) and month_end == inv_date  # noqa

        dates |= {inv_date}
        if inv_state == 'not_paid':
            dates |= {stop_date}

        min_date = min(dates)
        min_date = inv_date if min_date < inv_date else min_date
        min_date = init_date if min_date < init_date else min_date

        max_date = max(dates)
        max_date = stop_date if stop_date <= max_date else max_date

        if max_date < min_date:
            return []

        anchor = 1
        anchor_date = get_day_one(min_date)
        next_date = anchor_date + relativedelta(months=anchor, days=-1)
        date_range = []
        while next_date <= max_date:
            anchor += 1
            if skip_check and inv_date == next_date:
                # /!\ NOTE_SKIP: In case that we have an invoice which has no
                # previous payment or that its payments are after invoice date
                # and invoice date happens to be at the of one month we are not
                # going to use that date to reevaluate the invoice because
                # sometimes it leads to revaluation with decimals that are
                # undesirable.
                next_date = anchor_date + relativedelta(months=anchor, days=-1)
                continue
            date_range.append(next_date)
            next_date = anchor_date + relativedelta(months=anchor, days=-1)

        # /!\ NOTE_SKIP applies here too.
        skip_check = skip_check and inv_date == max_date

        if not skip_check and max_date not in date_range:
            date_range.append(max_date)

        return [s2d(x) for x in date_range]

    @api.model
    def _remove_previous_revaluation(
            self, date, invoice_id=False, account_id=False):
        # /!\ NOTE: self includes several invoices, We are going to remove
        # their realization entries. Which ones:
        # - Only Invoices whose Accounting Date is minor than Request Date.
        # Now, of those realizations that the invoices have we are going to
        # remove only those that:
        # - Are within Same Year and Month, i.e. Realization Entry Date =
        # '2018-11-20' and Realization Request Date = '2018-11-28', then
        # Realization will be removed. There should be only one realization per
        # month.
        # - Are after the Request Date, i.e. Realization Entry Date =
        # '2018-12-15' and Realization Request Date = '2018-11-28', then
        # Realization will be removed.
        if not any([invoice_id, account_id]):
            raise UserError(
                _('You have to either use an invoice or an account'))
        anchor_date = get_day_one(date)
        obj = invoice_id or account_id
        move_ids = (
            obj.mapped('realization_move_ids')
            .filtered(lambda x: x.date >= anchor_date))
        move_ids.mapped('line_ids').remove_move_reconcile()
        move_ids.button_cancel()
        move_ids.unlink()
        return True

    @api.model
    def prepare_realization_move(
            self, date, invoice_id=False, account_id=False):
        if not any([invoice_id, account_id]):
            raise UserError(
                _('You have to either use an invoice or an account'))
        date = d2s(date)
        domain = [('date', '=', date)]
        label = _('Monetary Revaluation at %s on %s')
        if invoice_id:
            currency_id = invoice_id.currency_id.id
            domain += [('invoice_id', '=', invoice_id.id)]
            label = label % (date, invoice_id.name)
            journal_id = (
                invoice_id.company_id.invoice_realization_journal_id or
                invoice_id.company_id.currency_exchange_journal_id)
        if account_id:
            currency_id = account_id.currency_id.id
            domain += [('account_id', '=', account_id.id)]
            label = label % (date, account_id.name)
            journal_id = (
                account_id.company_id.account_realization_journal_id or
                account_id.company_id.currency_exchange_journal_id)

        ledger = self.search(domain)
        if not ledger:
            return {}

        account_ids = {x: x for x in ledger.mapped('account_id')}

        if invoice_id:
            position_id = invoice_id.company_id.invoice_realization_position_id
            if position_id:
                account_ids = position_id.map_accounts(account_ids)
        if account_id:
            position_id = account_id.company_id.account_realization_position_id
            if position_id:
                account_ids = position_id.map_accounts(account_ids)

        line_ids = []
        for ldg in ledger:
            name = '%s - [%s]' % (label, ldg.account_id.id)
            acc_id = account_ids[ldg.account_id].id
            line_ids += self._prepare_realization_lines(
                ldg.fx_amount, date, name, acc_id, journal_id,
                currency_id, ldg.partner_id.id)

        return self._prepare_realization_move(
            date, label, journal_id, invoice_id, account_id, line_ids)

    @api.model
    def _prepare_realization_move(
            self, date, label, journal_id, invoice_id, account_id, line_ids):
        return {
            'journal_id': journal_id.id,
            'ref': label,
            'date': date,
            'realization_invoice_id': invoice_id and invoice_id.id,
            'realization_account_id': account_id and account_id.id,
            'line_ids': line_ids,
            'move_type': 'entry',
        }

    @api.model
    def _prepare_realization_lines(
            self, amount, date, label, account_id, journal_id, currency_id,
            partner_id):

        base_line = {
            'name': label,
            'partner_id': partner_id,
            'currency_id': currency_id,
            'amount_currency': 0.0,
            'date': date,
            'debit': 0.0,
            'credit': 0.0,
        }
        debit_line = base_line.copy()
        credit_line = base_line.copy()

        gain_account = journal_id.company_id.income_currency_exchange_account_id
        loss_account = journal_id.company_id.expense_currency_exchange_account_id
        if amount > 0:
            debit_account_id = loss_account.id
            credit_account_id = account_id
        else:
            debit_account_id = account_id
            credit_account_id = gain_account.id

        debit_line.update({
            'credit': abs(amount),
            'account_id': debit_account_id,
        })

        credit_line.update({
            'debit': abs(amount),
            'account_id': credit_account_id,
        })

        return [(0, 0, debit_line), (0, 0, credit_line)]

    def create_revaluation_move(self, dates, invoice_id=False, account_id=False):  # noqa
        am_obj = self.env['account.move']
        self._remove_previous_revaluation(
            min(dates), invoice_id=invoice_id, account_id=account_id)
        for date in dates:
            move_vals = self.prepare_realization_move(
                date, invoice_id=invoice_id, account_id=account_id)
            if not move_vals:
                continue
            am_obj.create(move_vals)

    def remove_revaluation_ledger(self, date, account_id, invoice_id):
        date = get_day_one(date)
        return self.search([
            ('account_id', '=', account_id),
            ('invoice_id', '=', invoice_id),
            ('date', '>=', date),
        ]).unlink()

    def get_cumulative_fx_at_date(self, date, account_id, invoice_id):
        date = s2d(date)
        return self.search([
            ('account_id', '=', account_id),
            ('invoice_id', '=', invoice_id),
            ('date', '<=', date),
        ], limit=1, order='date desc').cumulative_fx

    def get_previous_cumulative_fx(self, date, account_id, invoice_id):
        date = s2d(date)
        return self.search([
            ('account_id', '=', account_id),
            ('invoice_id', '=', invoice_id),
            ('date', '<', date),
        ], limit=1, order='date desc').cumulative_fx

    @api.model
    def cron_monthly_realization(
            self, on_day, init_date=None, realized=False, do_ledger=True,
            do_entry=None, do_commit=False):
        """This method will run on_day-th of month and then it will run the
        realization process with last day of previous month"""

        # /!\ NOTE: Bare in mind not to use days further than 28. Otherwise you
        # will risk to skip this cron job.
        date = s2d(fields.Date.today())
        if date.day != on_day:
            _logger.info(
                'Not yet %s-th of month `cron_monthly_realization`', (on_day,))
            return False

        date -= timedelta(days=on_day)

        _logger.info(
            'Processing on %s - `cron_monthly_realization`',
            (d2s(date),))
        # /!\ NOTE: In cron job method we explicitly avoid passing the
        # init_date argument as this is an action that we expect to ocurre in
        # the very previous month, from the first day of the previous month
        # until the last day of the previous month.
        return self.process_realization(
            'both', date=date, init_date=init_date, realized=realized,
            do_ledger=do_ledger, do_entry=do_entry, do_commit=do_commit)

    @api.model
    def process_realization(
            self, apply, date=None, init_date=None, realized=False,
            do_ledger=True, do_entry=None, do_commit=False):
        _logger.info('Entering method `process_realization`')

        date = s2d(date if date else fields.Date.today())

        if apply in ('both', 'invoice'):
            query = """
                SELECT DISTINCT am.id
                FROM account_move am
                INNER JOIN res_company rc ON rc.id = am.company_id
                WHERE
                    am.currency_id != rc.currency_id
                    AND am.date <= %s
                    AND am.state = 'posted'
                    AND am.move_type IN ('in_invoice', 'in_refund', 'out_invoice', 'out_refund')
                """
            if not realized:
                query += ' AND NOT am.fully_realized'
            self._cr.execute(query, (date,))

            invoice_ids = [x[0] for x in self._cr.fetchall()]
            if invoice_ids:
                (self.env['account.move']
                 .with_context(prefetch_fields=False)
                 .browse(invoice_ids)
                 .create_realization_entries(
                     date, init_date, do_ledger=do_ledger, do_entry=do_entry,
                     do_commit=do_commit))
        if apply in ('both', 'account'):
            query = """
                SELECT DISTINCT aa.id
                FROM account_account aa
                INNER JOIN res_company rc ON rc.id = aa.company_id
                WHERE
                    aa.realizable_account = TRUE
                    AND aa.currency_id != rc.currency_id
                    AND aa.currency_id IS NOT NULL
                    AND (
                        aa.deprecated = FALSE OR
                        aa.deprecated IS NULL)
                """
            self._cr.execute(query)

            account_ids = [x[0] for x in self._cr.fetchall()]
            if account_ids:
                (self.env['account.account']
                 .with_context(prefetch_fields=False)
                 .browse(account_ids)
                 .create_realization_entries(
                     date, init_date, do_ledger=do_ledger, do_entry=do_entry,
                     do_commit=do_commit))
        _logger.info('Exiting method `process_realization`')
        return True
