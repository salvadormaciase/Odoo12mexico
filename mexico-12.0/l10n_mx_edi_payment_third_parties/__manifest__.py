# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': "Payment complement to third parts",
    'summary': """
        Allow generate the payment complement by third parts""",
    'version': "12.0.1.0.0",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'category': 'Accounting',
    'license': 'LGPL-3',
    'depends': [
        'l10n_mx_edi',
        'l10n_mx_edi_customer_bills',
    ],
    'data': [
        'data/payment10.xml',
        'wizards/attach_xmls_wizard_view.xml',
    ],
    'installable': True,
}
