# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo Oscar Alcala <oscar@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Ecommerce for Mexico",
    "summary": """
        Adds the fields related to the Mexico localisation to all
        frontend forms that are related to a partner creation/modification
    """,
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Localization/Mexico",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        'l10n_mx_edi',
        'website_sale',
    ],
    "demo": [
    ],
    "data": [
        'data/form_fields.xml',
        'views/templates.xml',
    ],
    "installable": True,
    "auto_install": False,
}
