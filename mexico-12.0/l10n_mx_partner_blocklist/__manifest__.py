# coding: utf-8
# Copyright 2020 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Partner blocklist for Mexican Localization',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'summary': 'Manage the partner blocklist provided by the SAT and avoid '
    'sell to block partners',
    'license': 'LGPL-3',
    'category': 'Hidden',
    "version": "12.0.1.0.0",
    'depends': [
        'l10n_mx_edi',
        'sale_management',
        'purchase',
        'contacts',
    ],
    'test': [],
    'data': [
        'security/blocklist_groups.xml',
        'security/ir.model.access.csv',
        'data/cron_partner_blacklist.xml',
        'data/partner_blocklist_status.xml',
        'data/ir_config_parameter.xml',
        'views/res_partner_view.xml',
        'views/res_partner_blacklist.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
