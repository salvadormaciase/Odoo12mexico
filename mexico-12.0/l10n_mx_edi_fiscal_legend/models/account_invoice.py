# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_legend_ids = fields.Many2many(
        'l10n_mx_edi.fiscal.legend', string='Fiscal Legends',
        help="Legends under tax provisions, other than those contained in the "
        "Mexican CFDI standard.")
