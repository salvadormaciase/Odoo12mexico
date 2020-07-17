# -*- coding: utf-8 -*-


def set_advance_process(cr):
    cr.execute('''
        UPDATE
            res_company
        SET
            l10n_mx_edi_advance = 'A'
        WHERE
            l10n_mx_edi_product_advance_id IS NOT NULL;
        ''')


def migrate(cr, version):
    if not version:
        return

    set_advance_process(cr)
