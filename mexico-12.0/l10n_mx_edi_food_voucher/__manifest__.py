# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Food Vouchers Complement',
    'version': '12.0.1.0.0',
    "author": "Vauxoo",
    "license": "LGPL-3",
    'category': 'Hidden',
    'summary': 'Mexican Localization for EDI documents',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        "data/voucher_complement.xml",
        "views/res_partner_view.xml",
        "views/account_invoice_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
