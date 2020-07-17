# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Mexico Localization Customs for DIOT',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        'account',
        'l10n_mx_edi_customs',
        'l10n_mx_import_taxes',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'views/customs_view.xml',
        'views/account_invoice_view.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [
        'demo/account_account_demo.xml',
    ],
    'qweb': [
    ],
    'installable': True,
}
