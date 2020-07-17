# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_property = fields.Many2one(
        'res.partner', 'Address Property in Construction',
        help='Use this field when the invoice require the '
        'complement to "Partial construction services". This value will be '
        'used to indicate the information of the property in which are '
        'provided the partial construction services.')
