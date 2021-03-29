from odoo import _, api, models


class AttachXmlsWizard(models.TransientModel):
    _inherit = 'attach.xmls.wizard'

    @api.model
    def _get_xml_data(self, xml):
        """Return data from XML"""
        res = super(AttachXmlsWizard, self)._get_xml_data(xml)
        if not self._context.get('l10n_mx_edi_cfdi_third'):
            return res
        vat_emitter = (self.env.user.company_id.vat or '').upper()
        if vat_emitter == res[0]:
            return res
        res = list(res)
        res[0] = vat_emitter
        return tuple(res)

    @api.multi
    def create_invoice(self, xml, supplier, currency_id, taxes,
                       account_id=False):
        res = super(AttachXmlsWizard, self).create_invoice(
            xml=xml, supplier=supplier, currency_id=currency_id, taxes=taxes,
            account_id=account_id)
        if not self._context.get('l10n_mx_edi_cfdi_third') or not res.get(
                'key'):
            return res
        invoice = self.env['account.invoice'].browse(res['invoice_id'])
        if invoice.company_id.vat == invoice.l10n_mx_edi_cfdi_supplier_rfc:
            return res
        invoice.message_post(
            body=_('This invoice was generated with a CFDI from thirds'))
        return res

    @api.multi
    def _prepare_invoice_lines_data(self, xml, account_id, taxes):
        res = super(AttachXmlsWizard, self)._prepare_invoice_lines_data(
            xml=xml, account_id=account_id, taxes=taxes)
        notary = self.env['account.invoice'].l10n_mx_edi_get_notary_etree(xml)
        if not self._context.get('l10n_mx_edi_cfdi_third') or not notary:
            return res
        return [(0, 0, {
            'account_id': account_id,
            'name':  _('CFDI Thirds'),
            'quantity': 1.0,
            'price_unit': float(
                notary[0].DatosOperacion.get('MontoOperacion')),
        })]
