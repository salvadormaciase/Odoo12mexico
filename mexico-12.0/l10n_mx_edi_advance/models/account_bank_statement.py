# -*- coding: utf-8 -*-

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(self, counterpart_aml_dicts=None,
                               payment_aml_rec=None, new_aml_dicts=None):
        res = super(AccountBankStatementLine, self.with_context(
            l10n_mx_edi_manual_reconciliation=False)).process_reconciliation(
                counterpart_aml_dicts=counterpart_aml_dicts,
                payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)
        if not self.l10n_mx_edi_is_required():
            return res
        for payment in res.mapped('line_ids.payment_id'):
            is_required = payment.l10n_mx_edi_advance_is_required(
                payment.amount)
            if is_required:
                payment._l10n_mx_edi_generate_advance(is_required)
        return res
