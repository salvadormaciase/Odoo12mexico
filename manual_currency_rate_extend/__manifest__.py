# -*- coding: utf-8 -*-
# Copyright 2020 Ketan Kachhela <l.kachhela28@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Show Inverse Currency Rate',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to maintain an exchange rate using the inversion method',
    'author': '',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sr_manual_currency_exchange_rate',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'l10n_mx_edi',
        #'account_edi'
    ],
    'data': [
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml'
    ],
    "installable": True
}
