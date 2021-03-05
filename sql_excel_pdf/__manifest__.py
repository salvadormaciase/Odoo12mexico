# -*- coding: utf-8 -*-

{
    'name' : 'SQL to Excel and PDF',
    'version' : '12.0.1.0.0',
    'summary': 'Generate Excel and PDF reports using SQL query',
    'description': """Generate Excel and PDF reports using SQL query. Categorise and tag SQL reports for quick retrieval.""",
    'author':'S&V',
    'images' : ['static/description/banner.png'],
    'category': 'Extra Tools',
    'depends' : ['base','mail'],
    'data': [
        'security/sql_security.xml',
        'security/ir.model.access.csv',
        'report/sql_reports.xml',
        'report/sql_pdf_templates.xml',
        'views/sql_views.xml',
    ],
    'website': 'https://www.sandv.biz',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 71,
    'currency': 'EUR',
    'support': 'odoo@sandv.biz'

}
