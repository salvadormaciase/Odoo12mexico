from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        ctx = {}
        if new_aml_dicts:
            ctx.update({'new_aml_dicts': new_aml_dicts})
        return super(AccountBankStatementLine, self.with_context(**ctx)).process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)

    def _l10n_mx_edi_get_payment_extra_data(self, invoice_ids=None):
        self.ensure_one()
        res = super(AccountBankStatementLine, self)._l10n_mx_edi_get_payment_extra_data(invoice_ids)
        if not self._context.get('new_aml_dicts'):
            return res
        aml_dicts = self._context.get('new_aml_dicts')[0]
        res.update({
            'writeoff_label': aml_dicts.get('name'),
            'writeoff_account_id': aml_dicts.get('account_id'),
            'l10n_mx_edi_is_commission': True,
        })
        return res
