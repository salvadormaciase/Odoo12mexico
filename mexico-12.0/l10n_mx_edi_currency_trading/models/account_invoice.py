
from lxml import etree
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.constrains('state')
    def _check_only_one_ct_type(self):
        for invoice in self.filtered(lambda r: r.state == 'open'):
            fld = 'invoice_line_ids.product_id.l10n_mx_edi_ct_type'
            ct_types = set(invoice.mapped(fld)) - {False}
            if len(ct_types) > 1:
                raise ValidationError(_(
                    "This invoice contains products with different exchange "
                    "operation types.\n"
                    "It is not possible to bill currency purchases and sales "
                    "within the same invoice."))

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        """If the CFDI was signed, try to adds the schemaLocation for Donations"""
        result = super(AccountInvoice, self)._l10n_mx_edi_create_cfdi()
        cfdi = result.get('cfdi')
        if not cfdi:
            return result
        cfdi = self.l10n_mx_edi_get_xml_etree(cfdi)
        if 'divisas' not in cfdi.nsmap:
            return result
        cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
            cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
            'http://www.sat.gob.mx/divisas',
            'http://www.sat.gob.mx/sitio_internet/cfd/divisas/divisas.xsd')
        result['cfdi'] = etree.tostring(cfdi, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return result
