# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI Payment Split',
    'summary': 'Allow split payments into multi-invoices',
    'author': 'Vauxoo',
    'license': 'LGPL-3',
    'version': '12.0.1.0.0',
    'category': 'Hidden',
    'depends': [
        'l10n_mx_edi_payment'
    ],
    'data': [
        'data/payment10.xml',
        'data/res_currency_data.xml',
        'security/security.xml',
        'views/account_payment.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
