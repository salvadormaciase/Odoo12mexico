# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Odoo Mexican Localization Reports - General Ledger",
    "summary": """
        Electronic accounting reports
            - General Ledger
    """,
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Accounting",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "l10n_mx_edi",
        "l10n_mx_edi_bank",
        "l10n_mx_reports",
        "l10n_mx_edi_payment_bank",
    ],
    "demo": [
    ],
    "data": [
        "data/account_financial_report_data.xml",
        "data/templates/cfdimoves.xml",
        "views/search_template_view.xml",
        "views/report_financial.xml",
    ],
    "installable": True,
    "auto_install": True,
}
