
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_edi_minimum_wage = fields.Float(
        related='company_id.l10n_mx_edi_minimum_wage',
        string='Mexican minimum salary', readonly=False,
        help='Indicates the current daily amount of the general minimum wage '
        'in Mexico')
    l10n_mx_edi_uma = fields.Float(
        related='company_id.l10n_mx_edi_uma',
        string='Mexican UMA', readonly=False,
        help='Indicates the current UMA in Mexico')
    l10n_mx_edi_umi = fields.Float(
        related='company_id.l10n_mx_edi_umi',
        string='Mexican UMI', readonly=False, help='Indicates the current UMI in Mexico')
    l10n_mx_edi_vacation_bonus = fields.Selection(
        'Vacation Bonus', readonly=False, related='company_id.l10n_mx_edi_vacation_bonus',
        help='Indicate when the company will to pay the vacation bonus.')
    l10n_mx_edi_dynamic_name = fields.Boolean(
        'Dynamic concepts?', readonly=False, related='company_id.l10n_mx_edi_dynamic_name',
        help='If true, the payslip concepts based on inputs could be dynamic.\nFor example: '
        'If employee will to receive 100 MXN by concept of sale commissions, the commission input could have the '
        'name "Commissions for SO12345", and that name will be set on the CFDI.')
