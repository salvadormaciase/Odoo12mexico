{
    "name": "Gandalf",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Accounting",
    "website": "http://www.vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    "demo": [],
    "data": [
        'security/ir.model.access.csv',
        'data/service_cron_data.xml',
        'views/res_config_view.xml',
        'views/account_invoice_view.xml',
        'views/account_view.xml',
        'views/account_revaluation_ledger_view.xml',
        'wizard/run_realization_view.xml',
    ],
    "installable": True,
    "auto_install": True,
}
