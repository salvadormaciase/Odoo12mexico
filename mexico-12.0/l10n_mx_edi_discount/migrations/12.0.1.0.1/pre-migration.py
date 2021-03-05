from odoo import SUPERUSER_ID, api


def delete_view(cr):
    # Delete view that remains after Migration the module
    # l10n_mx_edi_cancellation to odoo/enterprise and added
    # l10n_mx_edi_cancellation_complement to Vauxoo/mx, field
    # l10n_mx_edi_cancellation_date not found because it's loaded after
    # l10n_mx_edi_hr_expense
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        view_invoice_form = env.ref(
            'l10n_mx_edi_cancellation.'
            'view_mx_edi_cancellation_invoice_form',
            raise_if_not_found=False)
        if view_invoice_form:
            view_invoice_form.unlink()
        view_config = env.ref(
            'l10n_mx_edi_cancellation.'
            'view_reversal_config_settings',
            raise_if_not_found=False)
        if view_config:
            view_config.unlink()
        view_payment_frm_invoices = env.ref(
            'l10n_mx_edi_cancellation.'
            'view_account_payment_from_invoices_inh',
            raise_if_not_found=False)
        if view_payment_frm_invoices:
            view_payment_frm_invoices.unlink()
        view_payment_inv_form = env.ref(
            'l10n_mx_edi_cancellation.'
            'view_account_payment_invoice_form',
            raise_if_not_found=False)
        if view_payment_inv_form:
            view_payment_inv_form.unlink()
        view_payment = env.ref(
            'l10n_mx_edi_cancellation.'
            'view_account_payment_form_inh_l10n_mx_cancellation',
            raise_if_not_found=False)
        if view_payment:
            view_payment.unlink()


def migrate(cr, version):
    if not version:
        return
    delete_view(cr)
