# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def l10n_mx_edi_get_iedu_etree(self, cfdi):
        """Get the Complement node from the cfdi.
        :param cfdi: The cfdi as etree
        :type cfdi: etree
        :return: the iedu node
        :rtype: etree
        """
        if not hasattr(cfdi, 'Complemento'):
            return None
        attribute = '//iedu:instEducativas'
        namespace = {'iedu': 'http://www.sat.gob.mx/iedu'}
        node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
        return node[0] if node else None


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    l10n_mx_edi_iedu_id = fields.Many2one(
        'res.partner', string='Student', help="Student information for IEDU "
        "complement:\n Make sure that the student have set CURP.")
