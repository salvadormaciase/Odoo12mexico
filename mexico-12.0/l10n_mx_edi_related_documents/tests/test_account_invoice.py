# Copyright 2020 Vauxoo
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


@tagged('edi_related_documents')
class TestL10nMxEdiRelatedDocuments(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiRelatedDocuments, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search([
            ('name', '=', 'ISR')
        ])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })

    def test_01_get_related_documents(self):
        """Testing that when creating an invoice and it refund, and checking that the invoice id is on the field
        l10n_mx_edi_related_document_ids' of the refund, and the refund id is on the field
        'l10n_mx_edi_related_document_ids_inverse' of the invoice.
        """
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))

        refund = self.env['account.invoice.refund'].with_context(
            active_ids=invoice.ids).create({
                'filter_refund': 'refund',
                'description': 'Testing',
                'date': invoice.date_invoice,
            })
        result = refund.invoice_refund()
        refund_id = result.get('domain')[1][2]
        refund = self.env['account.invoice'].browse(refund_id)
        refund.action_invoice_open()
        refund.l10n_mx_edi_get_related_documents()

        self.assertIn(invoice.id, refund.l10n_mx_edi_related_document_ids.ids)
        self.assertIn(refund.id, invoice.l10n_mx_edi_related_document_ids_inverse.ids)

    def test_02_get_related_documents_error(self):
        """Testing that when a record has on it field 'l10n_mx_edi_origin' a CDFI with a wrong pattern it will raise
        an error.
        """
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        invoice.refresh()
        self.assertEqual(invoice.state, "open")
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        invoice.write({
            'l10n_mx_edi_origin': 'WRONG VALUE',
        })

        invoice.l10n_mx_edi_get_related_documents()
        message = ("The field 'CFDI Origin' of the record %s has a wrong value") % (invoice.name)
        self.assertIn(message, invoice.message_ids[0].body)

        invoice.write({
            'l10n_mx_edi_origin': '01|Testing',
        })
        invoice.l10n_mx_edi_get_related_documents()
        message = ("The number: Testing doesn't match the pattern of a CFDI we are unable to look for this related "
                   "document.")
        self.assertIn(message, invoice.message_ids[0].body)
