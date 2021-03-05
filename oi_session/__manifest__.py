# -*- coding: utf-8 -*-
{
    'name': "Inactive Sessions Timeout",

    'summary': """""",

    'description': """
        
    """,

    'author': "Openinside",
    'website': "https://www.open-inside.com",
    "license": "OPL-1",
    "price" : 29.99,
    "currency": 'EUR',    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '12.0.1.1.4',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'view/ir_session.xml',
        'view/action.xml',
        'view/menu.xml'
    ],
    
    'post_init_hook' : 'post_init_hook',
    
    'external_dependencies' : {
        'python' : [],
    },
    'odoo-apps' : True,
    'images':[
            'static/description/cover.png'
        ],       
}