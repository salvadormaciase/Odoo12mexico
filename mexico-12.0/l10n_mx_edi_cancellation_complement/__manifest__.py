# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "EDI Cancellation for Mexican Localization (Complement)",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'LGPL-3',
    'category': 'Hidden',
    'version': '12.0.1.0.0',
    'depends': [
        'l10n_mx_edi_cancellation',
    ],
    'data': [
        'security/res_groups.xml',
        'data/server_action_data.xml',
        'views/account_invoice_view.xml',
        'wizard/cancellation_with_reversal_move_view.xml',
        'views/account_payment_view.xml',
        'views/res_config_settings_view.xml',
        'views/mail_templates.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
