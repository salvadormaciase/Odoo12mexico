# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_np_partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        help="Buyer or buyers information"
    )
