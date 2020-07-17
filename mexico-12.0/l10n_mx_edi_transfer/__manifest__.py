# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI Transfer',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Hidden',
    'license': 'LGPL-3',
    'summary': 'CFDI to Transfers',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        'data/3.3/cfdi_transfer.xml',
        'views/l10n_mx_edi_report_invoice.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
