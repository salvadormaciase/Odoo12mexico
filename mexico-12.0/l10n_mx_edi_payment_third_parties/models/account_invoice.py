# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _l10n_mx_edi_get_total_third_part(self):
        amount = 0
        for invoice in self.filtered(
                lambda inv: inv.company_id.vat !=
                inv.l10n_mx_edi_cfdi_supplier_rfc):
            cfdi = invoice.l10n_mx_edi_get_xml_etree()
            notary = invoice.l10n_mx_edi_get_notary_etree(cfdi)
            amount += float(notary[0].DatosOperacion.get('MontoOperacion')
                            if notary else cfdi.get('Total'))
        return amount

    @api.model
    def l10n_mx_edi_get_notary_etree(self, cfdi):
        """Get the notary complement from the CFDI"""
        if not hasattr(cfdi, 'Complemento'):
            return []
        attribute = '//notariospublicos:NotariosPublicos'
        namespace = {
            'notariospublicos': 'http://www.sat.gob.mx/notariospublicos'}
        node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
        return node
