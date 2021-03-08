# Copyright 2018 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestMXInvoiceDelivery(InvoiceTransactionCase):

    def test_invoice_free_delivery(self):
        """Ensure that CFDI with free delivery is generated correctly."""
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        invoice = self.create_invoice()
        invoice.invoice_line_ids.invoice_line_tax_ids = False
        invoice.invoice_line_ids.copy({
            'product_id': self.env['delivery.carrier'].sudo().search(
                [('fixed_price', '=', 0)]).mapped('product_id').id,
            'price_unit': 0,
        })
        invoice.compute_taxes()
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
