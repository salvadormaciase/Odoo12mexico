# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def insert_attachment(self, model, id_record, files, filename):
        attachment_obj = self.env['ir.attachment'].sudo()
        # if asuffix is required add to this dict the input name and
        # the suffix to add to the file name
        suffixes = {
            'purchase_order': 'PO',
            'receipt': 'AC',
        }
        for fname, xml_file in files.items():
            if not xml_file:
                continue
            suffix = suffixes.get(fname, '')
            new_name = filename if not suffix else '%s_%s' % (filename, suffix)
            attachment_value = {
                'name': '%s.%s' % (new_name, xml_file.mimetype.split('/')[1]),
                'datas': base64.b64encode(xml_file.read()),
                'datas_fname': xml_file.filename,
                'res_model': model,
                'res_id': id_record,
            }
            attachment_obj += attachment_obj.create(attachment_value)
        return attachment_obj
