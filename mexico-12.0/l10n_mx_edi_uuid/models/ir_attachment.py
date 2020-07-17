# -*- coding: utf-8 -*-
# Copyright 2019 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from lxml import etree, objectify

from odoo import api, fields, models

FIELDS = ['store_fname', 'res_model', 'res_id', 'name', 'datas']


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    l10n_mx_edi_cfdi_uuid = fields.Char(
        string="Fiscal Folio", index=True,
        prefetch=False, readonly=True)

    @api.multi
    def update_uuid(self):
        if not self.ids or not self.exists():
            return
        uuid_attachments = self.search([
            ('id', 'in', self.ids), ('res_id', '!=', 0),
            ('res_model', 'in', ['account.invoice', 'account.payment']),
            '|', ('name', '=ilike', '%.xml'), ('name', 'not like', '.')
        ])
        attachments_skipped = self.browse()
        for attach in uuid_attachments:
            if not attach.datas:
                attachments_skipped |= attach
                continue
            cfdi = base64.decodestring(attach.datas).replace(
                b'xmlns:schemaLocation', b'xsi:schemaLocation')
            model = self.env[attach.res_model].browse(attach.res_id)
            try:
                tree = objectify.fromstring(cfdi)
            except etree.XMLSyntaxError:
                # it is a invalid xml
                attachments_skipped |= attach
                continue

            tfd_node = model.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is None:
                # It is not a signed xml
                attachments_skipped |= attach
                continue
            # used _write to avoid loop when calling method from write
            attach._write({'l10n_mx_edi_cfdi_uuid': tfd_node.get('UUID')})
            if not model.l10n_mx_edi_cfdi_name:
                model.l10n_mx_edi_cfdi_name = attach.name
        (self - uuid_attachments + attachments_skipped)._write({
            'l10n_mx_edi_cfdi_uuid': False})
        invoice_ids = (uuid_attachments - attachments_skipped).filtered(
            lambda r: r.res_model == 'account.invoice').mapped('res_id')
        invoices = self.env['account.invoice'].browse(invoice_ids).exists()
        if invoices:
            invoices.sudo()._check_uuid_duplicated()
        return True

    @api.multi
    def write(self, vals):
        vals.pop('l10n_mx_edi_cfdi_uuid', None)
        with self.env.cr.savepoint():
            # Secure way if someone catch the exception to skip a rollback
            res = super(IrAttachment, self).write(vals)
            if set(vals.keys()) & set(FIELDS):
                self.update_uuid()
        return res

    @api.model
    def create(self, vals):
        vals.pop('l10n_mx_edi_cfdi_uuid', None)
        with self.env.cr.savepoint():
            # Secure way if someone catch the exception and skip a rollback
            records = super(IrAttachment, self).create(vals)
            if set(vals.keys()) & set(FIELDS):
                records.update_uuid()
        return records
