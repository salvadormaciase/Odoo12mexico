# coding: utf-8
# Copyright 2019 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Download Invoices",
    "summary": """
        Adds the ability to download your XML signed file and to send
        via email the signed XML and PDF files of the electronic invoice.
    """,
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Website",
    "website": "http://www.vauxoo.com/",
    "license": "OEEL-1",
    "depends": [
        "sale",
        "website",
    ],
    "demo": [
    ],
    "data": [
        "views/templates.xml",
        "views/sale_portal_templates.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
}
