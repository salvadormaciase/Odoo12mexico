from odoo import models
from odoo.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def get_transaction_currency(self):
        return (
            self.payment_id.currency_id
            or self.move_id.currency_id
            or self.currency_id
            or self.company_id.currency_id)

    def get_paid_balances_at_date(self, to_date):
        """Compute paid amounts at the specified date, for bot company & payment currency"""
        self.ensure_one()
        company = self.company_id
        company_currency = company.currency_id
        transaction_currency = self.get_transaction_currency()
        rounding = company_currency.rounding
        journal_exchange = company.currency_exchange_journal_id
        paid_balance = 0
        paid_currency_balance = 0

        # /!\ TODO: This method could need a big overhauling. It depends on how the changes in APR affect it.

        aprs = (
            self.mapped('matched_debit_ids') |
            self.mapped('matched_credit_ids'))
        # /!\ NOTE: We are excluding APRs with transaction exchange differences
        for apr in aprs:
            if (self == apr.debit_move_id
                    and apr.credit_move_id.journal_id != journal_exchange
                    and apr.credit_move_id.date <= to_date):
                if apr.credit_amount_currency:
                    if apr.credit_move_id.amount_currency:
                        # /!\ NOTE: We do this computation because odoo does it
                        # at invoice rate we want actual payment valuation.
                        # That's the reason we don't take apr.amount here. That
                        # could be another story when aml.amount_currency is
                        # zero.
                        paid_balance += (
                            apr.credit_amount_currency /
                            apr.credit_move_id.amount_currency *
                            apr.credit_move_id.balance)
                    else:
                        # /!\ NOTE: When the aml.amount_currency is zero odoo
                        # proposes a value that is actually presented as the
                        # valuated payment when dealing with payments in a
                        # different currency than the invoice.
                        paid_balance += apr.amount
                    paid_currency_balance += apr.credit_amount_currency
                else:
                    if float_is_zero(
                            apr.amount, precision_rounding=rounding):
                        # /!\ NOTE: Nothing to here. This is in practice a
                        # payment which both in company currency and
                        # invoice currency does not provide any value.
                        continue
                    if apr.credit_move_id.amount_currency:
                        paid_currency_balance += (
                            apr.amount *
                            apr.credit_move_id.amount_currency /
                            apr.credit_move_id.balance)
                    else:
                        paid_currency_balance += company_currency._convert(
                            apr.amount, transaction_currency,
                            company, apr.credit_move_id.date)
                    paid_balance += apr.amount
            elif (self == apr.credit_move_id
                    and apr.debit_move_id.journal_id != journal_exchange
                    and apr.debit_move_id.date <= to_date):
                if apr.debit_amount_currency:
                    if apr.debit_move_id.amount_currency:
                        # /!\ NOTE: We do this computation because odoo does it
                        # at invoice rate we want actual payment valuation.
                        # That's the reason we don't take apr.amount here. That
                        # could be another story when aml.amount_currency is
                        # zero.
                        paid_balance += (
                            apr.debit_amount_currency /
                            apr.debit_move_id.amount_currency *
                            apr.debit_move_id.balance)
                    else:
                        # /!\ NOTE: When the aml.amount_currency is zero odoo
                        # proposes a value that is actually presented as the
                        # valuated payment when dealing with payments in a
                        # different currency than the invoice.
                        paid_balance += apr.amount
                    paid_currency_balance += apr.debit_amount_currency
                else:
                    if float_is_zero(apr.amount, precision_rounding=rounding):
                        # /!\ NOTE: Nothing to here. This is in practice a
                        # payment which both in company currency and
                        # invoice currency does not provide any value.
                        continue
                    if apr.debit_move_id.amount_currency:
                        paid_currency_balance += (
                            apr.amount *
                            apr.debit_move_id.amount_currency /
                            apr.debit_move_id.balance)
                    else:
                        paid_currency_balance += company_currency._convert(
                            apr.amount, transaction_currency,
                            company, apr.debit_move_id.date)
                    paid_balance += apr.amount

        return paid_balance, paid_currency_balance
