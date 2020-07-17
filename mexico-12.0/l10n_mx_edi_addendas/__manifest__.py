# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2017 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Yennifer Santiago <yennifer@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#                Julio Serna Hernandez <julio@vauxoo.com>
############################################################################
{
    'name': 'Mexican Addendas',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'license': 'LGPL-3',
    'category': '',
    "version": "12.0.1.0.0",
    'depends': [
        'base_automation',
        'l10n_mx_edi',
    ],
    'test': [],
    'data': [
        'data/cfdi.xml',
        'views/res_config_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
