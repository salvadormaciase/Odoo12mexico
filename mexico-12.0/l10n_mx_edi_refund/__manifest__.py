# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "EDI Refund for Mexican Localization",
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'license': 'LGPL-3',
    'category': 'Hidden',
    'version': '12.0.1.0.1',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        'wizard/account_invoice_refund_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
