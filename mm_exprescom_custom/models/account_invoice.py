# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    em_mm_desc = fields.Float(string='Descuento (%)')

