# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
{
    'name': "EDI Educational Institutions (IEDU) Complement "
            "for the Mexican Localization",
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Hidden',
    'license': 'LGPL-3',
    'website': "http://www.vauxoo.com",
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        "security/ir.model.access.csv",
        "data/iedu_template.xml",
        "data/partner_tags_data.xml",
        "views/account_invoice_view.xml",
        "views/report_invoice.xml",
        "views/account_journal_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
