# Copyright 2020 Vauxoo
# License LGPL-3 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'MX EDI sale coupon',
    'summary': '''
    Allow generate EDI documents with sale coupons
    ''',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'LGPL-3',
    'category': 'Installer',
    'version': '12.0.1.0.0',
    'depends': [
        'l10n_mx_edi_discount',
        'l10n_mx_edi_sale_coupon',
    ],
    'test': [
    ],
    'data': [
        'data/cfdiv33.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
