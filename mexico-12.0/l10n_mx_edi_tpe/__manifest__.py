# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Foreign Passenger Tourist Complement',
    'version': '12.0.1.0.0',
    "author": "Vauxoo",
    "license": "LGPL-3",
    'category': 'Hidden',
    'summary': 'Mexican Localization for EDI documents',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        "data/tourist_foreign.xml",
        "views/account_invoice_view.xml",
        "views/product_template_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
