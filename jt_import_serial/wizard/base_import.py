# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import psycopg2
from odoo.tools import pycompat
from odoo import models, api
_logger = logging.getLogger(__name__)


class BaseImport(models.TransientModel):

    _inherit = "base_import.import"

    @api.multi
    def do(self, fields, columns, options, dryrun=False):
        picking = False
        operation_type = False
        use_exist_lot = False
        if self._context.get('picking_id') and self.res_model == 'stock.production.lot':
            picking = self.env['stock.picking'].browse(
                int(self._context.get('picking_id')))
            operation_type = picking and picking.picking_type_id or False
            use_exist_lot = operation_type and operation_type.use_existing_lots

        self.ensure_one()
        self._cr.execute('SAVEPOINT import')

        final_data = []
        flag_has_lot_product = False
        final_product_dict = {}
        product_index = 0
        lot_index = 0
        try:
            data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            data = self._parse_import_data(data, import_fields, options)

            if picking and operation_type:
                if 'product_id' in import_fields and 'name' in import_fields:
                    flag_has_lot_product = True

                    # Set index of product and lot
                    product_index = import_fields.index('product_id')
                    lot_index = import_fields.index('name')

                    for lst in data:
                        product = self.env['product.product'].search([('name', '=', lst[product_index])], limit=1)
                        if product:
                            has_lot = self.env['stock.production.lot'].sudo().search([('product_id', '=', product.id), ('name', '=', lst[lot_index])], limit=1)
                            if has_lot:
                                tmp_list = []
                                if product.id in final_product_dict:
                                    tmp_list = final_product_dict.get(product.id)
                                tmp_list.append(has_lot)
                                final_product_dict.update({product.id: tmp_list})
                            else:
                                final_data.append(lst)
                        else:
                            final_data.append(lst)
            else:
                final_data = data

        except ValueError as error:
            return {
                'messages': [{
                    'type': 'error',
                    'message': pycompat.text_type(error),
                    'record': False,
                }]
            }

        _logger.info('importing %d rows...', len(final_data))

        name_create_enabled_fields = options.pop(
            'name_create_enabled_fields', {})
        model = self.env[self.res_model].with_context(
            import_file=True, name_create_enabled_fields=name_create_enabled_fields)

        if picking and operation_type and not use_exist_lot and flag_has_lot_product:
            import_result = {'messages': [], 'ids': []}
        else:
            import_result = model.load(import_fields, final_data)

        # Main function code to add serial/lot number to products
        if picking and operation_type and flag_has_lot_product:
            lots = {}
            lot_records = []

            if not use_exist_lot:
                for lst in final_data:
                    product = self.env['product.product'].search([('name', '=', lst[product_index])])
                    if product:
                        tmp_list = []
                        if product.id in lots:
                            tmp_list = lots.get(product.id)
                        tmp_list.append(lst[lot_index])
                        lots.update({product.id: tmp_list})
                for key, value in final_product_dict.items():
                    lst = []
                    for val in value:
                        lst.append(val.name)
                    tmp_list = []
                    if key in lots:
                        tmp_list = lots.get(product.id)
                    tmp_list.extend(lst)
                    lots.update({key: tmp_list})

            else:
                new_ids = []
                for key, value in final_product_dict.items():
                    for lot in value:
                        new_ids.append(lot.id)
                new_ids.extend(import_result.get('ids'))
                lot_records = self.env['stock.production.lot'].browse(new_ids)

            for move in picking.move_ids_without_package:
                used_lot_ids = []
                lots_to_fill = []
                filled_lot = []

                if use_exist_lot:
                    for lot in lot_records:
                        if lot.id not in used_lot_ids and lot.product_id.id == move.product_id.id:
                            lots_to_fill.append(lot)

                if move.product_id.tracking != 'none':
                    for line in move.move_line_ids:
                        if not use_exist_lot:
                            if line.product_id.id in lots:
                                for lot in lots.get(line.product_id.id):
                                    if lot not in filled_lot:
                                        line.lot_name = lot
                                        line.qty_done = line.product_uom_qty
                                        filled_lot.append(lot)
                                        break
                        else:
                            for lot in lots_to_fill:
                                if lot.id not in used_lot_ids:
                                    if line.product_id.tracking == 'serial':
                                        quants = self.env['stock.quant'].sudo().search([
                                            ('product_id', '=', line.product_id.id),
                                            ('location_id', '=', picking.location_id.id),
                                            ('lot_id', '=', lot.id),
                                            # ('quantity', '>=', line.product_uom_qty)
                                        ])
                                        if not quants:
                                            self.env['stock.quant'].with_context(default_flag_import_quant=True, default_picking_id=picking.id)._update_available_quantity(move.product_id, picking.location_id, line.product_uom_qty, lot_id=lot, package_id=None, owner_id=None, in_date=None)
                                    else:
                                        self.env['stock.quant'].with_context(default_flag_import_quant=True, default_picking_id=picking.id)._update_available_quantity(move.product_id, picking.location_id, line.product_uom_qty, lot_id=lot, package_id=None, owner_id=None, in_date=None)

                                    if operation_type.use_existing_lots:
                                        line.lot_id = lot.id
                                    line.qty_done = line.product_uom_qty
                                    used_lot_ids.append(lot.id)
                                    break

        _logger.info('done')

        try:
            if dryrun:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.clear_caches()
                self.pool.reset_changes()
            else:
                self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        if import_result['ids'] and options.get('headers'):
            BaseImportMapping = self.env['base_import.mapping']
            for index, column_name in enumerate(columns):
                if column_name:
                    # Update to latest selected field
                    exist_records = BaseImportMapping.search(
                        [('res_model', '=', self.res_model), ('column_name', '=', column_name)])
                    if exist_records:
                        exist_records.write({'field_name': fields[index]})
                    else:
                        BaseImportMapping.create({
                            'res_model': self.res_model,
                            'column_name': column_name,
                            'field_name': fields[index]
                        })
        return import_result
