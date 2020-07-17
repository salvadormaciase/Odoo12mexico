# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
{
    "name": "Discounts by amount",
    "summary": """
Apply discounts by amount (and not only by percentage) in invoice
lines lines and total in the invoice.
    """,
    "version": "12.0.1.0.1",
    "author": "Vauxoo",
    "category": "Accounting",
    "website": "http://www.vauxoo.com/",
    "license": "OEEL-1",
    "depends": [
        "l10n_mx_edi",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "installable": True,
}
