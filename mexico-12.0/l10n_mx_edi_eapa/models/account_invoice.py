
from lxml import etree
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        """If the CFDI was signed, try to adds the schemaLocation for Donations"""
        result = super(AccountInvoice, self)._l10n_mx_edi_create_cfdi()
        cfdi = result.get('cfdi')
        if not cfdi:
            return result
        cfdi = self.l10n_mx_edi_get_xml_etree(cfdi)
        if 'obrasarte' in cfdi.nsmap:
            cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
                cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
                'http://www.sat.gob.mx/arteantiguedades',
                'http://www.sat.gob.mx/sitio_internet/cfd/arteantiguedades/obrasarteantiguedades.xsd')
        elif 'pagoenespecie' in cfdi.nsmap:
            cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
                cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
                'http://www.sat.gob.mx/pagoenespecie',
                'http://www.sat.gob.mx/sitio_internet/cfd/pagoenespecie/pagoenespecie.xsd')
        result['cfdi'] = etree.tostring(cfdi, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return result
