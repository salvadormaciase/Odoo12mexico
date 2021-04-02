# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "EDI Transfer with External Trade",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'AGPL-3',
    'category': 'Hidden',
    'version': '12.0.1.0.0',
    'depends': [
        'l10n_mx_edi_transfer',
        'l10n_mx_edi_external_trade',
    ],
    'data': [
        'data/3.3/cfdi_transfer.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
