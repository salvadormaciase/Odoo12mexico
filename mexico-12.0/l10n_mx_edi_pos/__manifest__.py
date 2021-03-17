# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican POS Management System",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Point of Sale",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "point_of_sale",
        "l10n_mx_edi_partner_defaults",
    ],
    "demo": [
    ],
    "data": [
        "data/3.3/cfdi.xml",
        "views/account_view.xml",
        "views/point_of_sale_view.xml",
        "views/report_xml_session.xml",
        "views/assets.xml",
        "views/res_config_settings_views.xml",
    ],
    'external_dependencies': {
        'python': [
            'num2words'
        ],
    },
    "installable": True,
    "auto_install": False,
    'qweb': ['static/src/xml/pos.xml'],
    'images': [
        'images/main_screenshot.png'
    ],
}
