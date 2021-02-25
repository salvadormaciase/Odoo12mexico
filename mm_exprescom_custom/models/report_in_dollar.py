# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ReportViewDollar(models.Model):
    _name = "report.view.dollar"
    _auto = False
    _description = 'Report View in dollar'

    id = fields.Char(string='ids', readonly=True)
    client = fields.Char(comodel_name='res_partner', string='Código Socio', readonly=True)
    name_inv = fields.Char(comodel_name='report.name', string='Nombre', readonly=True)
    invoice = fields.Char(comodel_name='report.invoice.number', string='Factura', readonly=True)
    total_usd = fields.Float(comodel_name=' report.residual', string='Total USD', readonly=True)

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, 'report_view_dollar')
        self._cr.execute(""" CREATE VIEW report_view_dollar AS (
             SELECT
                (account_invoice.id) as id,
                (res_partner.ref) as client,
                (res_partner.name) as name_inv,
                (account_invoice.number) as invoice,
                (account_invoice.residual) as total_usd
            FROM
                account_invoice
            INNER JOIN
                res_partner ON res_partner.id = account_invoice.partner_id
            WHERE
                account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' 
                AND account_invoice.currency_id = 2 AND((CURRENT_DATE) - (account_invoice.date_due)) BETWEEN 1 AND 30
            GROUP BY 
                account_invoice.id,
                res_partner.ref,
                res_partner.name,
                account_invoice.number,
                account_invoice.residual
            ORDER BY 
                name_inv
        )""")
