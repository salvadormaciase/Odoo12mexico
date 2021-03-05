# Copyright 2020 Vauxoo
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    l10n_mx_edi_related_document_ids = fields.Many2many(
        "account.invoice", "rel_l10n_mx_edi_related_document_ids", "invoice_id", "related_invoice_id", "CFDI Origins",
        help="Related documents that are on the field 'CFDI Origin'")
    l10n_mx_edi_related_document_ids_inverse = fields.Many2many(
        "account.invoice", "rel_l10n_mx_edi_related_document_ids", "related_invoice_id", "invoice_id",
        "CFDI Destinations", help="Related documents where this record is on their field 'CFDI Origin'")
    count_related_documents = fields.Integer(compute="_compute_count_related_documents")
    count_related_documents_inverse = fields.Integer(compute="_compute_count_related_documents")

    @api.multi
    def l10n_mx_edi_get_related_documents(self):
        """Method to obtain all the related documents of a record that are on the field "CFDI Origin" of the record
        """
        for record in self:
            l10n_mx_edi_origin = record.l10n_mx_edi_origin.split("|")
            if not len(l10n_mx_edi_origin) == 2 or l10n_mx_edi_origin[0] not in ['01', '02', '03', '04',
                                                                                 '05', '06', '07']:
                message = _("The field 'CFDI Origin' of the record %s has a wrong value.") % (record.name)
                record.message_post(body=message)
                continue

            cfdi_origin_documents = record.l10n_mx_edi_origin.split("|")[1].split(',')
            pattern = r'[a-f0-9A-F]{8}-[a-f0-9A-F]{4}-[a-f0-9A-F]{4}-[a-f0-9A-F]{4}-[a-f0-9A-F]{12}'
            for cfdi_origin in cfdi_origin_documents:
                if not len(cfdi_origin) == 36 or not re.match(pattern, cfdi_origin):
                    message = _("The number: %s doesn't match the pattern of a CFDI we are unable to look "
                                "for this related document.") % (cfdi_origin)
                    record.message_post(body=message)

            domain = [('l10n_mx_edi_cfdi_uuid', 'in', cfdi_origin_documents)]
            documents = record.search(domain)
            record.l10n_mx_edi_related_document_ids = [(6, 0, documents.ids)]

    def _compute_count_related_documents(self):
        """Method to get how many related documents has a record.
        """
        for record in self:
            record.count_related_documents = len(record.l10n_mx_edi_related_document_ids)
            record.count_related_documents_inverse = len(record.l10n_mx_edi_related_document_ids_inverse)

    def action_get_related_documents(self):
        """Action that gets all the CFDI Origins a record.
        """
        action = self.env.ref("account.action_invoice_tree1").read()[0]
        action.update({
            'name': _('Related Documents Origins'),
            'domain': [('id', "in", self.l10n_mx_edi_related_document_ids.ids)],
        })
        return action

    def action_get_related_documents_inverse(self):
        """Action that gets all the records where this record is found on their "CFDI Origin" field.
        """
        action = self.env.ref("account.action_invoice_tree1").read()[0]
        action.update({
            'name': _('Related Documents Destinations'),
            'domain': [('id', "in", self.l10n_mx_edi_related_document_ids_inverse.ids)],
        })
        return action
