from suds.client import Client
from odoo import models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def check_vat_mx(self, vat):
        res = super(ResPartner, self).check_vat_mx(vat)
        if not res:
            return res
        return self.l10n_mx_check_vat_lco(vat)

    def l10n_mx_check_vat_lco(self, vat):
        """If the VAT is valid for Mexico, check if its valid in the LCO"""
        lco = self.env['ir.config_parameter'].sudo().get_param('l10n_mx_edi_omit_lco', False)
        if vat in ['XAXX010101000', 'XEXX010101000'] or lco:
            return True
        url = 'https://facturacion.finkok.com/servicios/soap/satinc.wsdl'
        company = self.mapped('company_id') or self.env.user.company_id
        pac_info = self.env['account.invoice']._l10n_mx_edi_finkok_info(company, 'sign')
        username = pac_info['username']
        password = pac_info['password']
        try:
            client = Client(url, timeout=20)
            response = client.service.check(username, password, vat)
        except Exception:
            return True
        if getattr(response, 'error', None):
            return True
        if not getattr(response, 'exist', None):
            return False
        return True

    def _construct_constraint_msg(self, country_code):
        res = super(ResPartner, self)._construct_constraint_msg(country_code)
        if country_code != 'mx':
            return res
        lco = self.env['ir.config_parameter'].sudo().get_param('l10n_mx_edi_omit_lco', False)
        if lco:
            return res
        return _('%s\nIf the format is correct, ensure that the VAT is in the SAT LCO.') % res
