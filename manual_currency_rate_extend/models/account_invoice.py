# -*- coding: utf-8 -*-
# Copyright 2020 Ketan Kachhela <l.kachhela28@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('manual_currency_exchange_rate')
    def _compute_inverse_currency_rate(self):
        for rec in self:
            if rec.manual_currency_exchange_rate and rec.manual_currency_exchange_rate > 0:
                rec.inverse_currency_rate = 1 / rec.manual_currency_exchange_rate
            else:
                rec.inverse_currency_rate = 1

    inverse_currency_rate = fields.Float(
        string="Inverse Currency Rate",
        digits=(12, 4),
        compute="_compute_inverse_currency_rate")

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        values = super(AccountInvoice, self)._l10n_mx_edi_create_cfdi_values()
        if self.inverse_currency_rate:
            values['rate'] = ('%.6f' % self.inverse_currency_rate) if self.manual_currency_exchange_rate else False
        return values

