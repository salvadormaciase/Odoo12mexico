# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CurrencyRateInverted(models.Model):

    _inherit = 'res.currency.rate'

    mm_currency_rate = fields.Float(
        string="Currency Rate",
        digits=(12, 4))


