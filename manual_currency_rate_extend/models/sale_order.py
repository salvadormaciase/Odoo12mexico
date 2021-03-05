# -*- coding: utf-8 -*-
# Copyright 2020 Ketan Kachhela <l.kachhela28@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
