from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_tpe_transit_date = fields.Date(
        string='Transit Date',
        help='Attribute required to express the date of arrival or '
        'departure of the means of transport used. It is expressed in the '
        'form aaaa-mm-dd'
    )
    l10n_mx_edi_tpe_transit_time = fields.Float(
        string='Transit Time',
        help='Attribute required to express the time of arrival or departure '
        'of the means of transport used. It is expressed in the form hh:mm:ss'
    )
    l10n_mx_edi_tpe_transit_type = fields.Selection([
        ('arrival', 'Arrival'),
        ('departure', 'Departure'),
    ],
        string='Transit Type',
        help='Attribute required to incorporate the operation performed'
    )
    l10n_mx_edi_tpe_partner_id = fields.Many2one(
        'res.partner',
        string='Transport Company',
        help='Attribute required to indicate the transport company of entry '
        'into national territory or transfer to the outside'
    )
