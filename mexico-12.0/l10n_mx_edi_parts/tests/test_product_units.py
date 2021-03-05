# Copyright 2019 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestProductUnits(InvoiceTransactionCase):

    def setUp(self):
        super(TestProductUnits, self).setUp()
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.product.tracking = 'serial'

    def test_product_units(self):
        purchase = self.create_purchase()
        purchase.button_confirm()
        picking = purchase.picking_ids
        line = picking.move_ids_without_package.move_line_ids
        self.set_serial_number(line, 1.0, lot_name='123456')
        picking.sudo().button_validate()
        sale_order = self.create_sale_order()
        sale_order.action_confirm()
        lot = line.lot_id
        picking = sale_order.picking_ids
        picking.move_ids_without_package.quantity_done = 1.0
        line = picking.move_ids_without_package.move_line_ids
        self.set_serial_number(line, 1.0, lot_id=lot.id)
        picking.button_validate()
        self.env['sale.advance.payment.inv'].with_context(
            active_ids=[sale_order.id]).create({
                'advance_payment_method': 'delivered'}).create_invoices()
        invoice = sale_order.invoice_ids
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertEqual(xml.Conceptos.Concepto.Parte.attrib[
            'NoIdentificacion'], '123456',
            "The product lot/serial was not added")

    def test_product_units_lot(self):
        self.product.tracking = 'lot'
        purchase = self.create_purchase()
        purchase.order_line.product_qty = 2.0
        purchase.button_confirm()
        picking = purchase.picking_ids
        line = picking.move_ids_without_package.move_line_ids
        self.set_serial_number(line, 2.0, lot_name='123456')
        picking.sudo().button_validate()
        sale_order = self.create_sale_order()
        sale_order.order_line.product_uom_qty = 2.0
        sale_order.action_confirm()
        lot = line.lot_id
        picking = sale_order.picking_ids
        picking.move_ids_without_package.quantity_done = 2.0
        line = picking.move_ids_without_package.move_line_ids
        self.set_serial_number(line, 2.0, lot_id=lot.id)
        picking.button_validate()
        self.env['sale.advance.payment.inv'].with_context(
            active_ids=[sale_order.id]).create({
                'advance_payment_method': 'delivered'}).create_invoices()
        invoice = sale_order.invoice_ids
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        self.assertEqual(xml.Conceptos.Concepto.Parte.attrib[
            'NoIdentificacion'], '123456',
            "The product lot/serial was not added")

    def set_serial_number(self, move_line, qty, lot_id=None, lot_name=None):
        move_line.sudo().write({
            'qty_done': qty,
            'lot_id': lot_id,
            'lot_name': lot_name,
        })
        return move_line

    def create_purchase(self):
        purchase = self.env['purchase.order'].sudo().create({
            'partner_id': self.partner_agrolait.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_qty': 1.0,
                'price_unit': 100.0,
                'date_planned': datetime.today(),
                'product_uom': self.product.uom_id.id,
            })]
        })
        return purchase

    def create_sale_order(self):
        sale = self.env['sale.order'].sudo().create({
            'partner_id': self.ref('base.res_partner_2'),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
            })]
        })
        return sale
