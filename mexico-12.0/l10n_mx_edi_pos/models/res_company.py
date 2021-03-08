from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_pos_default_partner_id = fields.Many2one(
        'res.partner', 'PoS default partner', domain="[('customer','=',True), ('vat','=','XAXX010101000')]",
        help="Select a partner with General Public RFC on this field if you want to create individual invoices "
             "for each PoS order, in consequence each invoice will have its own XML CFDI attachment. If this "
             "field is not set, the default partner feature is disabled, so new uninvoiced PoS orders will be "
             "grouped on a common CFDI when the PoS session is closed."
    )
