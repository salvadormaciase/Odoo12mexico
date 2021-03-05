# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': "Stock Landed Cost On Average Costing Method",
    'version': "12.0.0.0",
    'summary': "This module used to calculate stock landed cost on average costing method",
    'category': 'Warehouse',
    'description': """
    Average costing method
    landed cost
    landed cost on average costing
    costing method
    average cost
    extra cost add on average costing
    Transportation cost
    fright cost
    insurance cost
    duty cost
    clearance cost
    custom cost
    shipment to buyer place cost added in average costing method
    valuation
    real time valuation
    automated valuation
    stock valuation
    inventory valuation
    
    """,
    'author': "Sitaram",
    'website': "sitaramsolutions.com",
    'depends': ['base','sale_management','stock','stock_landed_costs'],
    'data': [
        'views/inherited_product.xml'
    ],
    'live_test_url':'https://youtu.be/UDQ1nafE62A',
    'images': ['static/description/banner.png'],
    "price": 39,
    "currency": 'EUR',
    'demo': [],
    "license": "AGPL-3",
    'installable': True,
    'auto_install': False,
}
