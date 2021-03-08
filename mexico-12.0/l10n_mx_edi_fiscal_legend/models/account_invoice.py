
from lxml import etree
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_legend_ids = fields.Many2many(
        'l10n_mx_edi.fiscal.legend', string='Fiscal Legends',
        help="Legends under tax provisions, other than those contained in the "
        "Mexican CFDI standard.")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.l10n_mx_edi_legend_ids:
            self.l10n_mx_edi_legend_ids = self.partner_id.l10n_mx_edi_legend_ids
        return super(AccountInvoice, self)._onchange_partner_id()

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        """If the CFDI was signed, try to adds the schemaLocation correctly"""
        result = super(AccountInvoice, self)._l10n_mx_edi_create_cfdi()
        cfdi = result.get('cfdi')
        if not cfdi:
            return result
        cfdi = self.l10n_mx_edi_get_xml_etree(cfdi)
        if 'leyendasFisc' not in cfdi.nsmap:
            return result
        cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
            cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
            'http://www.sat.gob.mx/leyendasFiscales',
            'http://www.sat.gob.mx/sitio_internet/cfd/leyendasFiscales/leyendasFisc.xsd')
        result['cfdi'] = etree.tostring(cfdi, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return result

    @api.model
    def create(self, vals):
        if not vals.get('l10n_mx_edi_legend_ids') and vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            vals.update({'l10n_mx_edi_legend_ids': [(6, 0, partner.l10n_mx_edi_legend_ids.ids)]})
        return super().create(vals)
