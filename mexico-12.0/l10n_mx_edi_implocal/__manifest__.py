# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Other duties and taxes Complement for Mexico',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Hidden',
    'summary': 'Mexican Localization for EDI documents',
    'license': 'LGPL-3',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        "data/l10n_mx_edi_implocal.xml",
        "data/account_tax_data.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
