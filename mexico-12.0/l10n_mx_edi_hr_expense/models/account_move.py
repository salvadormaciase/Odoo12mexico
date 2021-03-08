# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def _allow_to_modify_account_move(self, date_to_check, company_id):
        lock_date = max(company_id.period_lock_date or date.min,
                        company_id.fiscalyear_lock_date or date.min)
        if self.user_has_groups('account.group_account_manager'):
            lock_date = company_id.fiscalyear_lock_date
        if date_to_check <= (lock_date or date.min):
            return False, lock_date
        return True, lock_date
