# -*- coding: utf-8 -*-
{
    'name': "mm currency rate inverted",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sr_manual_currency_exchange_rate'],

    # always loaded
    'data': [
        'views/res_currency_rate_mm.xml',
        'data/server_action_currency_rate.xml',
        'data/server_action_sale_order.xml',
        'views/inherited_sale_order_mm.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}