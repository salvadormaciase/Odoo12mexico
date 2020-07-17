# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    l10n_mx_edi_niv = fields.Char(
        'NIV', help='Indicate the Vehicle identification number')
    l10n_mx_edi_motor = fields.Char(
        'No. Motor', help='Indicate the motor number if is found')
    l10n_mx_edi_circulation_no = fields.Char(
        'Folio circulation card', help='Indicate the folio number of the '
        'circulation card')
    l10n_mx_edi_landing = fields.Char(
        'Landing', help='If the vehicle destroyed was imported, indicate the '
        'number of landing document that protect the importation.')
    l10n_mx_edi_landing_date = fields.Date(
        'Landing date', help='If the vehicle destroyed was imported, indicate '
        'the date of landing document that protect the importation')
    l10n_mx_edi_aduana = fields.Char(
        'Aduana', help='If the vehicle destroyed was imported, indicate the '
        'aduana that was regularized the legal status in the country of the '
        'product destroyed')
    l10n_mx_edi_fiscal_folio = fields.Char(
        string='Fiscal Folio',
        help='CFDI number issued by the Authorized Destruction Center'
    )
    l10n_mx_edi_int_advice = fields.Char(
        string='Intention Advise Number',
        help='Folio number of the acknowledgment of receipt of the notice of '
        'intention to access the destruction program.'
    )
