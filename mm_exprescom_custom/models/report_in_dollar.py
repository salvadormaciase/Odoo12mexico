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
    total_usd_30 = fields.Float(comodel_name=' report.residual30', string='Total USD 1-30 Dias', readonly=True)
    total_usd_60 = fields.Float(comodel_name=' report.residual60', string='Total USD 31-60 Dias', readonly=True)
    total_usd_90 = fields.Float(comodel_name=' report.residual90', string='Total USD 61-90 Dias', readonly=True)
    total_usd_120 = fields.Float(comodel_name=' report.residual120', string='Total USD 91-120 Dias', readonly=True)
    total_usd_old = fields.Float(comodel_name=' report.residualold', string='Total USD 121-Mas Antiguo Dias', readonly=True)

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, 'report_view_dollar')
        self._cr.execute(""" CREATE VIEW report_view_dollar AS (
            SELECT 
                (res_partner.id) as id,
                (res_partner.ref) as client, 
                (res_partner.name) as name_inv, 
                sum(account_invoice.residual) as total_usd,
                (SELECT sum (account_invoice.residual)
                    FROM account_invoice
                    INNER JOIN res_partner T4 ON T4.id = account_invoice.partner_id
                    WHERE T4.ref = res_partner.ref AND account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' AND account_invoice.currency_id = 2 AND
                    ((CURRENT_DATE) - (account_invoice.date_due)) BETWEEN 1 AND 30) as total_usd_30,
                (SELECT sum (account_invoice.residual)
                    FROM account_invoice
                    INNER JOIN res_partner T6 ON T6.id = account_invoice.partner_id
                    WHERE T6.ref = res_partner.ref AND account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' AND account_invoice.currency_id = 2 AND
                    ((CURRENT_DATE) - (account_invoice.date_due)) BETWEEN 31 AND 60) as total_usd_60,
                (SELECT sum (account_invoice.residual)
                    FROM account_invoice
                    INNER JOIN res_partner T8 ON T8.id = account_invoice.partner_id
                    WHERE T8.ref = res_partner.ref AND account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' AND account_invoice.currency_id = 2 AND
                    ((CURRENT_DATE) - (account_invoice.date_due)) BETWEEN 61 AND 90) as total_usd_90,
                (SELECT sum (account_invoice.residual)
                    FROM account_invoice
                    INNER JOIN res_partner T10 ON T10.id = account_invoice.partner_id
                    WHERE T10.ref = res_partner.ref AND account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' AND account_invoice.currency_id = 2 AND
                    ((CURRENT_DATE) - (account_invoice.date_due)) BETWEEN 91 AND 120) as total_usd_120,
                (SELECT sum (account_invoice.residual)
                    FROM account_invoice
                    INNER JOIN res_partner T12 ON T12.id = account_invoice.partner_id
                    WHERE T12.ref = res_partner.ref AND account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' AND account_invoice.currency_id = 2 AND
                    ((CURRENT_DATE) - (account_invoice.date_due)) > 120) as total_usd_old
            FROM account_invoice
            INNER JOIN res_partner ON res_partner.id = account_invoice.partner_id
            WHERE account_invoice.type = 'out_invoice' AND account_invoice.state = 'open' AND account_invoice.currency_id = 2
            GROUP BY 
                res_partner.id,
                res_partner.ref,
                res_partner.name
            ORDER BY 
                name_inv
        )""")


#
#
# self._cr.execute(""" CREATE VIEW report_view_dollar AS (
#              SELECT
#                 (account_invoice.id) as id,
#                 (res_partner.ref) as client,
#                 (res_partner.name) as name_inv,
#                 (account_invoice.number) as invoice,
#                 (account_invoice.residual) as total_usd
#             FROM
#                 account_invoice
#             INNER JOIN
#                 res_partner ON res_partner.id = account_invoice.partner_id
#             WHERE
#                 account_invoice.type = 'out_invoice' AND account_invoice.state = 'open'
#                 AND account_invoice.currency_id = 2 AND((CURRENT_DATE) - (account_invoice.date_due)) BETWEEN 1 AND 30
#             GROUP BY
#                 account_invoice.id,
#                 res_partner.ref,
#                 res_partner.name,
#                 account_invoice.number,
#                 account_invoice.residual
#             ORDER BY
#                 name_inv
#         )""")