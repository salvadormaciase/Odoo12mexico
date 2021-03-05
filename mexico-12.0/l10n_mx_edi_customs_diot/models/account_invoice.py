# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    l10n_mx_edi_customs_id = fields.Many2one(
        'l10n_mx_edi.customs', 'Custom',
        help='Custom in which this invoice income in the company.')
    l10n_mx_edi_customs_extra_id = fields.Many2one(
        'l10n_mx_edi.customs', 'Customs Extra',
        help='Custom in which this invoice income in the company.')
    l10n_mx_edi_customs_total = fields.Monetary(
        'Customs Total', compute='_compute_customs_total',
        store=True, currency_field='company_currency_id',
        help='On invoices with customs saves the amount total in the company '
        'currency based in the customs rate.')
    l10n_mx_edi_freight = fields.Monetary(
        'Freight', track_visibility='onchange',
        currency_field='currency_id',
        help='Freight cost in the invoice if was imported.')
    l10n_mx_edi_customs_base = fields.Monetary(
        'Base', compute='_compute_customs_total',
        currency_field='currency_id', store=True,
        help='On invoices with customs saves the amount total less the '
        'freight.')

    @api.depends('l10n_mx_edi_customs_id.rate', 'amount_total')
    def _compute_customs_total(self):
        for record in self.filtered('l10n_mx_edi_customs_id'):
            record.l10n_mx_edi_customs_total = (
                record.amount_total * record.l10n_mx_edi_customs_id.rate)
            record.l10n_mx_edi_customs_base = record.amount_total - record.l10n_mx_edi_freight  # noqa
