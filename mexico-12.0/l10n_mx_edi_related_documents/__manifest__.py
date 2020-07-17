# Copyright 2020 Vauxoo
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': "EDI Related Documents",
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'license': 'LGPL-3',
    'category': 'Hidden',
    'version': '12.0.1.0.0',
    'depends': [
        'l10n_mx_edi',
        'l10n_mx_edi_uuid',
    ],
    'data': [
        'views/account_invoice.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
