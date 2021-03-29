# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from odoo import http
from odoo.http import request


class SaleOrderAttachments(http.Controller):

    @http.route(
        ['/purchase/order_attachments/<int:order_id>'],
        type='http', auth="user", methods=['POST'], website=True)
    def attach_files(self, order_id, **post):
        purchase_obj = request.env['purchase.order']
        att_obj = request.env['ir.attachment']
        xml = post.get('xml')
        errors, filename = att_obj.parse_xml(xml)
        if errors.get('wrongfiles'):
            return json.dumps({'error_messages': errors})
        att_ids = purchase_obj.insert_attachment(
            'purchase.order', order_id, post, filename)
        return json.dumps({'id': att_ids.ids})
