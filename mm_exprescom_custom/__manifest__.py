# -*- coding: utf-8 -*-
{
    'name': "Personalizaciones Exprescom",

    'summary': """
        Módulo Mit-Mut para presonalizaciones de Exprescom""",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "version": "1.0.0",
    "author": "Mit-Mut",
    "category": "Accounting",

    # any module necessary for this one to work correctly
    "depends": [
        "base","l10n_mx_edi",
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/view_report_dollar.xml',
    ],
    "installable": True,
}
