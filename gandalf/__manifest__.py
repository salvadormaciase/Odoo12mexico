{
    "name": "Gandalf",
    "version": "14.0.1.0.0",
    "author": "Vauxoo",
    "category": "Accounting",
    "website": "http://www.vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/set_configuration.xml',
        'data/service_cron_data.xml',
        'views/res_config_view.xml',
        'views/account_invoice_view.xml',
        'views/account_view.xml',
        'views/account_revaluation_ledger_view.xml',
        'wizard/run_realization_view.xml',
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": True,
}
