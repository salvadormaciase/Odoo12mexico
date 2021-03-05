# Copyright 2016 Vauxoo (Carlos <carlosecv74@gmail.com>,
#                        Osval Reyes <osval@vauxoo.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "POS with COGS moves",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Localization/Mexico",
    "website": "http://www.vauxoo.com/",
    "license": "OEEL-1",
    "depends": [
        "point_of_sale",
        "account_cancel",
    ],
    "data": [
        'views/pos_order_view.xml',
    ],
    "installable": True,
    "auto_install": False,
}
