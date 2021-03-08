from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_edi_pos_default_partner_id = fields.Many2one(
        'res.partner', 'PoS default partner', related='company_id.l10n_mx_edi_pos_default_partner_id',
        readonly=False)
