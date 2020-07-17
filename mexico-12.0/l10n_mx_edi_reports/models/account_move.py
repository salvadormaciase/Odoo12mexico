# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _get_cfdi_rate(self):
        """Get the rate with the same logic that is assigned in the CFDI
        generated in the document related"""
        self.ensure_one()
        cfdi = self.invoice_id or self.payment_id
        mxn = self.env.ref('base.MXN')
        if not cfdi or cfdi.currency_id == mxn:
            return False
        date = cfdi.date_invoice if self.invoice_id else cfdi.payment_date
        ctx = dict(company_id=cfdi.company_id.id, date=date)
        mxn = mxn.with_context(ctx)
        return cfdi.currency_id.with_context(ctx).compute(1, mxn)
