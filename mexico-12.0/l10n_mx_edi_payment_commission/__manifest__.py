# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Commissions support for EDI payment complement",
    'version': '12.0.1.1.0',
    'license': 'LGPL-3',
    'author': "Vauxoo",
    'category': 'Hidden',
    'depends': [
        'l10n_mx_edi'
    ],
    'data': [
        'data/partner_tags.xml',
        'data/payment10.xml',
        'views/account_payment_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
