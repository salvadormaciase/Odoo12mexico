from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceInterCompany(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiInvoiceInterCompany, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search([('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.company2 = self.company.create({
            'name': 'MX TEST',
            'rule_type': 'invoice_and_refund',
            'country_id': self.env.ref('base.mx').id,
            'parent_id': self.company.id
        })
        self.env.user.company_ids = [(4, self.company2.id)]
        self.env.user.company_id = self.company2
        self.env.ref('l10n_mx.mx_coa').load_for_current_company(16, 16)
        self.env.user.company_id = self.company

    def test_edi_intercompany_invoices(self):
        """Case with invoice_and_refund"""
        invoice = self.create_invoice()
        invoice.partner_id = self.company2.partner_id
        invoice.sudo().action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed", invoice.message_ids.mapped('body'))
        related = invoice.sudo().search([('auto_invoice_id', '=', invoice.id)])
        self.assertTrue(related)
        self.assertEqual(invoice.l10n_mx_edi_cfdi_uuid, related.l10n_mx_edi_cfdi_uuid, 'UUID not assigned correctly.')

    def test_edi_intercompany_sales(self):
        """Case with so_and_po"""
        self.company2.write({
            'rule_type': 'so_and_po',
            'applicable_on': 'sale',
            'auto_validation': 'validated',
            'warehouse_id': self.env['stock.warehouse'].search([('company_id', '=', self.company2.id)]).id,
        })
        self.product.invoice_policy = 'order'
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.company2.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
            })]
        })
        sale_order.action_confirm()
        self.env['sale.advance.payment.inv'].with_context(
            active_ids=[sale_order.id]).create({
                'advance_payment_method': 'delivered'}).create_invoices()
        invoice = sale_order.invoice_ids
        invoice.sudo().action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed", invoice.message_ids.mapped('body'))
        related = self.env['purchase.order'].sudo().search([('auto_sale_order_id', '=', sale_order.id)])
        self.assertTrue(related, 'PO not generated')
        self.assertTrue(self.env['ir.attachment'].search([('res_model', '=', related._name),
                                                          ('res_id', '=', related.id)]), 'Document not attached')
        sale_order = sale_order.copy({})
        sale_order.action_confirm()
        purchase = self.env['purchase.order'].sudo().search([('auto_sale_order_id', '=', sale_order.id)])
        purchase.button_confirm()
        picking = purchase.picking_ids
        picking.sudo().button_validate()
        bill = self.env[invoice._name].create({
            'type': 'in_invoice',
            'purchase_id': purchase.id,
        })
        bill.purchase_order_change()
        self.env['sale.advance.payment.inv'].with_context(
            active_ids=[sale_order.id]).create({
                'advance_payment_method': 'delivered'}).create_invoices()
        invoice = sale_order.invoice_ids
        invoice.sudo().action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed", invoice.message_ids.mapped('body'))
        self.assertEqual(invoice.l10n_mx_edi_cfdi_uuid, purchase.invoice_ids.l10n_mx_edi_cfdi_uuid,
                         'UUID not assigned correctly.')
