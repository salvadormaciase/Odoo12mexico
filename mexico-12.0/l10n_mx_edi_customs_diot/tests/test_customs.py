# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class EdiCustoms(TransactionCase):
    def setUp(self):
        super(EdiCustoms, self).setUp()
        self.customs = self.env['l10n_mx_edi.customs']
        inv_obj = self.env['account.invoice']
        self.journal = inv_obj.with_context(
            type='in_invoice')._default_journal()
        self.journal.update_posted = True
        self.partner = self.env.ref('base.res_partner_3')
        self.company = self.env.ref('base.main_company')

    def test_revert_custom(self):
        custom = self.create_customs()
        custom.approve_custom()
        self.assertEquals('confirmed', custom.state,
                          'State not updated correctly')
        invoice = custom.sat_invoice_id
        invoice.company_id.tax_cash_basis_journal_id.update_posted = True
        payment = invoice.payment_move_line_ids.mapped('payment_id')
        invoice.journal_id.update_posted = True
        custom.revert_custom()
        self.assertEquals('draft', custom.state,
                          'The custom not was reverted.')
        self.assertEquals('cancel', invoice.state,
                          'The invoice not was cancelled.')
        self.assertEquals('cancelled', payment.state,
                          'The payment not was cancelled.')

    def test_diot_flow(self):
        """Prepare the DIOT report and review their values.
        1. Create a foreign supplier invoice
        2. Create a customs and assign the previous invoice
        3. Get DIOT report and verify that values are corrects"""
        invoice = self.generate_invoice()
        # Prepare data
        tax = self.env['account.tax']
        tax_imp = self.env.ref('l10n_mx_edi_customs_diot.tax_imp_16')
        tax_16 = tax.search([('name', '=', 'IVA(16%) COMPRAS')], limit=1)
        tax_imp.write({
            'tax_exigibility': 'on_payment',
            'cash_basis_account_id': tax_16.cash_basis_account_id.id,
            'cash_basis_base_account_id': tax_16.cash_basis_base_account_id.id,
        })
        custom = self.create_customs()
        custom.write({
            'invoice_ids': [(4, invoice.id)],
            'rate': 19.12360,
            'iva': 16.0,
        })
        custom.approve_custom()
        move = self.env['account.move'].search([
            ('journal_id', '=', self.company.tax_cash_basis_journal_id.id)])
        self.assertEquals(len(move.line_ids), 8, '8 lines must be generated.')

    def create_customs(self):
        partner = self.env.ref('base.res_partner_12')
        account_dta = self.env.ref('l10n_mx_edi_customs_diot.account_account_dta')
        bank_journal = self.env['account.journal'].create({
            'name': 'My bank',
            'code': 'MB',
            'type': 'bank',
            'update_posted': True,
        })
        return self.customs.create({
            'name': '19 24 34 9000104',
            'date': self.env['l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date(),  # noqa
            'operation': 'IMP',
            'key_custom': 'A1',
            'regime': 'IMD',
            'sat_partner_id': partner.id,
            'partner_id': self.env.ref('base.res_partner_18').id,
            'dta': 4287.00,
            'account_dta_id': account_dta.id,
            'journal_payment_id': bank_journal.id,
            'journal_invoice_id': self.journal.id,
        })

    def generate_invoice(self):
        date = self.env['l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date()  # noqa
        prod = self.env.ref('product.product_product_8')
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'date_invoice': date,
            'account_id': self.partner.property_account_payable_id.id,
            'journal_id': self.journal.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': prod.id,
            'account_id': (prod.product_tmpl_id.get_product_accounts().get(
                'income').id),
            'quantity': 1,
            'price_unit': 100,
            'name': 'Product Test',
            'invoice_id': invoice.id,
        })
        return invoice
