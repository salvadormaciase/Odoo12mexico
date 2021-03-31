# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CurrencyRateInvertedSaleOrder(models.Model):

    _inherit = 'sale.order'

    mm_currency_rate_so = fields.Float(
        string="Currency Rate",
        digits=(12, 4))




