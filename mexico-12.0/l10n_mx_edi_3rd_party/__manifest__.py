# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Third Party Complement for the Mexican Localization',
    'version': '12.0.1.0.0',
    'summary': 'Sell products on behalf of 3rd parties',
    'author': 'Vauxoo',
    'category': 'Hidden',
    'license': 'LGPL-3',
    'website': 'http://www.vauxoo.com/',
    'depends': [
        'l10n_mx_edi_customs',
        'base_automation',
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/1.1/3rd_party_template.xml',
        'data/base_automation.xml',
        'views/account_invoice_view.xml',
        'views/mrp_bom_view.xml',
        'views/product_view.xml',
        'views/res_city_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
