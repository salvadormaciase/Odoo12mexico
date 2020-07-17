# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI Complement Destruction Certificate, Vehicle Renew and '
    'Substitution, Used Vehicle Sale, Natural person member of the '
    'coordinated, and Vehicle Sale concept complement.',
    'version': '12.0.1.0.0',
    "author": "Vauxoo",
    "license": "LGPL-3",
    'category': 'Hidden',
    'summary': 'Mexican Localization for EDI documents',
    'depends': [
        'fleet',
        'l10n_mx_edi',
    ],
    'data': [
        "data/certificate_destruction.xml",
        "data/renew_and_substitution.xml",
        "data/fleet_data.xml",
        "data/sale_vehicles.xml",
        "data/pfic.xml",
        "data/concept_sale_vehicles.xml",
        "data/fleet_service_type.xml",
        "views/account_invoice_view.xml",
        "views/fleet_vehicle_views.xml",
        "views/res_company_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
