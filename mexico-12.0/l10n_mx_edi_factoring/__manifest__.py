# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI Financial Factor',
    'summary': 'Mexican Localization for EDI documents',
    "version": "12.0.1.0.1",
    "author": "Vauxoo",
    'category': 'Hidden',
    "website": "http://www.vauxoo.com/",
    "license": "OEEL-1",
    'depends': [
        'l10n_mx_edi'
    ],
    'data': [
        'data/payment10.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/res_partner_view.xml',
        'views/l10n_mx_edi_report_payment.xml',
    ],
    'demo': [],
    'installable': True,
}
