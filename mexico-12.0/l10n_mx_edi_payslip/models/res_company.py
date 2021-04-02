# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_edi_minimum_wage = fields.Float(
        'Mexican minimum Wage',
        help='Indicates the current daily amount of the general minimum wage '
        'in Mexico')
    l10n_mx_edi_uma = fields.Float(
        'Mexican UMA', help='Indicates the current UMA in Mexico')
    l10n_mx_edi_umi = fields.Float(
        'Mexican UMI', help='Indicates the current UMI in Mexico')
    l10n_mx_edi_vacation_bonus = fields.Selection([
        ('on_holidays', 'On Holidays'),
        ('on_anniversary', 'On Anniversary'),
        ('on_christmas_bonus', 'On Christmas'),
    ], 'Vacation Bonus', default='on_holidays', help='Indicate when the company will to pay the vacation bonus.')
    l10n_mx_edi_dynamic_name = fields.Boolean(
        'Dynamic concepts?', help='If true, the payslip concepts based on inputs could be dynamic.\nFor example: '
        'If employee will to receive 100 MXN by concept of sale commissions, the commission input could have the '
        'name "Commissions for SO12345", and that name will be set on the CFDI.')
