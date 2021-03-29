# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI Complement for Mexico fuel consumption',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Hidden',
    'summary': 'Mexican Localization for EDI documents',
    'license': 'LGPL-3',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        "data/fuel_billing.xml",
        "data/l10n_mx_edi_fuel_ecc.xml",
        "data/l10n_mx_edi_fuel_cc.xml",
        "data/res_partner_category.xml",
        "views/account_invoice_view.xml",
        "views/product_view.xml",
        "views/res_company_view.xml",
    ],
    'demo': [
        "demo/l10n_mx_edi_fuel_demo.xml",
    ],
    'installable': True,
    'auto_install': False,
}
