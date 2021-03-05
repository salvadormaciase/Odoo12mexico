from lxml import etree
from odoo import api, fields, models


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

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        """If the CFDI was signed, try to adds the schemaLocation for Donations"""
        result = super(AccountInvoice, self)._l10n_mx_edi_create_cfdi()
        cfdi = result.get('cfdi')
        if not cfdi:
            return result
        cfdi = self.l10n_mx_edi_get_xml_etree(cfdi)
        if 'tpe' not in cfdi.nsmap:
            return result
        cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
            cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
            'http://www.sat.gob.mx/TuristaPasajeroExtranjero',
            'http://www.sat.gob.mx/sitio_internet/cfd/TuristaPasajeroExtranjero/TuristaPasajeroExtranjero.xsd')
        result['cfdi'] = etree.tostring(cfdi, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return result
