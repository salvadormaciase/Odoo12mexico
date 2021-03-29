# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class MXAccountReport(models.AbstractModel):
    _name = 'account.report'
    _inherit = 'account.report'

    def l10n_mx_edi_add_digital_stamp(self, path_xslt, cfdi):
        """Add digital stamp certificate attributes in XML report"""
        return self.env['l10n_mx.trial.report']._l10n_mx_edi_add_digital_stamp(
            path_xslt, cfdi)
