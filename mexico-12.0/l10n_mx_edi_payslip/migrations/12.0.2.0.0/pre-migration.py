# coding: utf-8

from odoo import SUPERUSER_ID, api


def update_noupdate_rules(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    inputs = [
        'l10n_mx_edi_payslip.hr_rule_input_perception_023_e',
        'l10n_mx_edi_payslip.hr_rule_input_perception_023_g',
    ]
    for rule_input in inputs:
        rule = env.ref(rule_input, False)
        if rule:
            rule.unlink()
    cr.execute("""
        UPDATE ir_model_data
        SET noupdate = False
        WHERE model = 'hr.salary.rule' AND module = 'l10n_mx_edi_payslip';
    """)


def migrate(cr, version):
    if not version:
        return
    update_noupdate_rules(cr)
