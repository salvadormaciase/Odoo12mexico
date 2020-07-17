# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'CFDI Complement for Mexico National Electoral Institute (INE)',
    'version': '12.0.1.0.0',
    'category': 'Hidden',
    'author': 'Vauxoo',
    'license': 'LGPL-3',
    'summary': 'This supplement must be used by individuals or corporations '
    'that provide some good or provide some service to Political Parties and '
    'Civil Associations that are related to people who are independent '
    'candidates and candidates.',
    'depends': [
        "l10n_mx_edi",
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
        "data/l10n_mx_edi_ine.xml",
        "data/l10n_mx_edi_ine_language_install.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
