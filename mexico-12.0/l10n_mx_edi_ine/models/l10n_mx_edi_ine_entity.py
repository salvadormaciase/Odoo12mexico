# -*- coding: utf-8 -*-

from odoo import fields, models


class L10nMxEdiIneEntity(models.Model):
    _name = 'l10n_mx_edi_ine.entity'
    _description = 'Entity'

    l10n_mx_edi_ine_entity_id = fields.Many2one(
        'res.country.state',
        string='Entity Code',
        help='Attribute required to register the key of the entity '
        'to which the expense applies. Set this when Process Type is Campaign '
        'or Pre-campaign',
        domain=lambda self: [(
            "country_id", "=", self.env.ref('base.mx').id)])
    l10n_mx_edi_ine_scope = fields.Selection(
        selection=[
            ('local', 'Local'),
            ('federal', 'Federal')
        ],
        string='Scope',
        help='Registers the type of scope of a process of type Campaign or '
        'Pre-campaign. Set this when Process Type is Campaign or Pre-campaign')
    l10n_mx_edi_ine_accounting = fields.Char(
        string='Accounting',
        help='Number assigned to your accounting to make the corresponding '
        'revenue or expenditure records in the Comprehensive Inspection '
        'System. Set this when Process Type is Campaign or Pre-campaign, or '
        'when Process Type is Ordinary and Committee Type is State Executive.'
        'Please use a comma to separate the accounting numbers when yo need '
        'to provide several numbers for one Entity'
    )
    invoice_id = fields.Many2one('account.invoice')
