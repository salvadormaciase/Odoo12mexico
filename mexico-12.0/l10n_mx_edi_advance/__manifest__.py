# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "EDI Advances for Mexican Localization",

    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'AGPL-3',
    'category': 'Hidden',
    'version': '12.0.3.0.0',
    'depends': [
        'l10n_mx_edi',
        'l10n_mx_edi_uuid',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/mail_templates.xml',
        'views/res_config_settings_views.xml',
        'data/account_data.xml',
        'data/account_journal_data.xml',
        'data/uom_data.xml',
        'data/product_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
