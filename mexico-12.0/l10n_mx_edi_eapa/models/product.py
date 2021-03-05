# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_mx_edi_art_complement = fields.Selection([
        ('eapa', 'Alienation of Works of Plastic Arts and Antiques'),
        ('pee', 'Payment in Kind')
    ], help='Choose the complemento to use', string='Art Complement')
    l10n_mx_edi_good_type = fields.Selection([
        ('01', 'Picture'),
        ('02', 'Engraved'),
        ('03', 'Sculpture'),
        ('04', 'Others')], help='If this is an art, assign which art type is '
        'this good.', string='Good type')
    l10n_mx_edi_other_good_type = fields.Char(
        'Good type',
        help="If the 'Good Type' is '04', assign the type of this art.")
    l10n_mx_edi_acquisition = fields.Selection([
        ('01', 'Purchase'),
        ('02', 'Donation'),
        ('03', 'Heritage'),
        ('04', 'Legacy'),
        ('05', 'Others')], 'Acquisition',
        help='Assign the way like was acquired this good')
    l10n_mx_edi_other_good_type = fields.Char(
        'Other good type', help="If the 'Acquisition' is '05', assign the "
        "acquisition way to this art.")
    l10n_mx_edi_tax_paid = fields.Float(
        'Tax paid', help='Assign the tax amount paid by the acquisition')
    l10n_mx_edi_acquisition_date = fields.Date(
        'Acquisition date', help='Indicate the acquisition date.')
    l10n_mx_edi_characteristic = fields.Selection([
        ('01', 'Signed'),
        ('02', 'Dated'),
        ('03', 'Framed'),
        ('04', 'Armelladas'),
        ('05', 'Wiring'),
        ('06', 'Serial number'),
        ('07', '2 or more characteristics')], 'Characteristic',
        help='Characteristic of the piece according with the SAT catalog.')
    l10n_mx_edi_pik_dimension = fields.Char(
        string='Piece of Art Dimensions',
        help='Dimensions of the piece of art'
    )
