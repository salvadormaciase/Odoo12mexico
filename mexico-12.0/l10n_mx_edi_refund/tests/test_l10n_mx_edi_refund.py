from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiRefund(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiRefund, self).setUp()
        self.refund_model = self.env['account.invoice.refund']
        self.payment_inmediate = self.env.ref(
            'account.account_payment_term_immediate')
        self.payment_method = self.env.ref(
            'l10n_mx_edi.payment_method_transferencia')
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })

    def test_l10n_mx_edi_invoice_refund(self):
        # -----------------------
        # Testing invoice refund to verify value selected from wizard of
        # credit note
        # -----------------------
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        refund = self.refund_model.with_context(
            active_ids=invoice.ids).create({
                'filter_refund': 'refund',
                'description': 'Refund Modify Test',
                'date': invoice.date_invoice,
                'l10n_mx_edi_payment_method_id': self.payment_method.id,
                'l10n_mx_edi_usage': 'G02',
                'l10n_mx_edi_origin_type': '03',
            })
        result = refund.invoice_refund()
        refund_id = result.get('domain')[1][2]
        refund = self.invoice_model.browse(refund_id)
        refund_type = refund.get_cfdi_related()['type']
        self.assertEquals(self.payment_inmediate,
                          refund.payment_term_id,
                          'Payment Term in refund is different to selected '
                          'from the wizard of credit note')
        self.assertEquals(self.payment_method,
                          refund.l10n_mx_edi_payment_method_id,
                          'Payment Method in refund is different to selected '
                          'from the wizard of credit note')
        self.assertEquals('G02', refund.l10n_mx_edi_usage,
                          'Use in refund is different to selected '
                          'from the wizard of credit note')
        self.assertEquals('03', refund_type,
                          'Invoice origin type is different to selected '
                          'from the wizard of credit note')
