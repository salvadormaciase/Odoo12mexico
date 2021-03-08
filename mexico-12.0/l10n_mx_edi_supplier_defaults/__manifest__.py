# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': "Information fields for Purchase with Mexican Localization",

    'summary': """
        Add information fields to use in purchase orders""",
    'version': '12.0.1.0.0',
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'category': 'Uncategorized',
    'license': "LGPL-3",
    'depends': [
        'purchase',
        'l10n_mx_edi'
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/purchase_views.xml',
        'views/purchase_order_templates.xml',
    ],
    'demo': [
    ],

    'installable': True,
}
