# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI Complement Retailer',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'license': 'LGPL-3',
    'category': 'Hidden',
    'summary': 'Mexican Localization for EDI documents',
    'depends': [
        'l10n_mx_edi_customs',
    ],
    'data': [
        "data/retailer1_3_1.xml",
        "wizards/retailer_invoice_wizard.xml",
        "views/account_invoice_view.xml",
    ],
    'installable': True,
    'auto_install': False,
}
