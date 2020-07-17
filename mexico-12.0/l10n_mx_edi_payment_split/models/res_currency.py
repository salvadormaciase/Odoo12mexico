# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Updated by Vauxoo 2019

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class ResCurrency(models.Model):
    _inherit = 'res.currency.rate'

    rate = fields.Float(digits=dp.get_precision('Rate Precision'))
