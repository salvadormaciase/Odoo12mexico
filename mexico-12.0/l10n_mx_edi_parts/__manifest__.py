# Copyright 2019 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Invoiced Product Units',
    'summary': '''
    Show the part number that have been invoiced from a particular product.
    ''',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '12.0.1.0.0',
    'depends': [
        'l10n_mx_edi',
        'sale_management',
        'sale_purchase',
        'stock',
    ],
    'test': [
    ],
    'data': [
        'data/cfdi.xml',
        'views/report_invoice_document.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
