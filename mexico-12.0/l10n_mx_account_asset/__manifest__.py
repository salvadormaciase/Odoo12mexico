# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Asset - Sale of Assets According to IFRS',
    'summary': '''
    This module adds a new button on Asset That will allow to sell it according
    to IFRS standards.''',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'LGPL-3',
    'category': 'Installer',
    'version': '12.0.1.0.0',
    'depends': [
        'account_asset',
    ],
    'data': [
        'data/ir_actions.xml',
        'views/account_asset_views.xml',
    ],
    'demo': [
        'demo/l10n_mx_account_asset_demo.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
