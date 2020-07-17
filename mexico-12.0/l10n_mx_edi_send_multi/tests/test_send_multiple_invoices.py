from odoo.exceptions import Warning as UserError
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestSendMulti(InvoiceTransactionCase):

    def test_send_multiple_invoices(self):
        """Send Multiple Invoices from single and Multiple partners"""
        invoices = self.env['account.invoice']
        # Agrolait invoices
        invoice1 = self.create_invoice()
        partner_email = invoice1.partner_id.email
        invoice1.sudo().partner_id.email = False
        invoices += self.create_invoice()
        invoices += self.create_invoice()
        invoices += invoice1
        ctx = {'active_model': 'account.invoice', 'active_ids': invoices.ids}
        wizard = self.env['wizard.mass.invoice.sending'].with_context(
            ctx).create({})
        # Assert, Must Fail because partner does not have a valid email
        with self.assertRaises(UserError):
            wizard.send_email()

        invoice1.sudo().partner_id.email = partner_email
        wizard = self.env['wizard.mass.invoice.sending'].with_context(
            ctx).create({})
        # Assert: Must success living a messages on partner
        messages = len(invoice1.partner_id.message_ids)
        wizard.send_email()
        self.assertEqual(
            messages + 1, len(invoice1.partner_id.message_ids))

        # Send including a different partner
        invoice4 = self.create_invoice()
        invoice4.partner_id = self.env.ref("base.res_partner_12")
        invoices += invoice4
        ctx['active_ids'] = invoices.ids
        with self.assertRaises(UserError):
            wizard = self.env['wizard.mass.invoice.sending'].with_context(
                ctx).create({})
