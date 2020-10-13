
from odoo import fields, models


class FiscalLegend(models.Model):
    _name = 'l10n_mx_edi.fiscal.legend'
    _description = 'Fiscal Legend'

    name = fields.Char(
        string='Legend Text', required=True,
        help="Text to specify the fiscal legend.")
    tax_provision = fields.Char(
        help="Specifies the Law, Resolution or Tax Disposition that regulates "
        "this legend. It must be expressed in capital letters without "
        "punctuation (e.g. ISR).")
    rule = fields.Char(
        help="Specifies the Article number or rule that regulates the "
        "obligation of this legend.")
