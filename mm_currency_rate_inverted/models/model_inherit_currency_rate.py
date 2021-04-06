# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CurrencyRateInverted(models.Model):

    _inherit = 'res.currency.rate'

    mm_currency_rate = fields.Float(
        string="Currency Rate",
        digits=(12, 4))

    line_weight = fields.Float(string='Line Weight (Kg)', compute='_compute_line_weight')

    def _compute_line_weight(self):
        line_weight = self.env.context.keys()

