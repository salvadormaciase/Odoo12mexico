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

from odoo import models, api
from odoo.exceptions import ValidationError


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def write(self, vals):
        # self.ensure_one()
        res = super(StockMove, self).write(vals)

        if self._context.get('flag_wizard'):
            for move in self:
                flag_error = False
                for line in move.move_line_ids:
                    if line.product_id.tracking != 'none':
                        if move.picking_id.picking_type_id.use_existing_lots:
                            if move.product_id.tracking == 'serial' and not line.lot_id:
                                flag_error = True
                                break
                        elif move.product_id.tracking == 'lot' and not line.lot_name:
                            flag_error = True
                            break

                if flag_error:
                    raise ValidationError('Please fill Lot/Serial Numbers for the products')

        return res


# class StockMoveLine(models.Model):

#     _inherit = 'stock.move.line'

#     @api.multi
#     def write(self, vals):
#         # self.ensure_one()
#         for line in self:
#             if vals.get('lot_id'):
#                 lines = self.env['stock.move.line'].search([('state', '=', 'done'), ('id', '!=', line.id), ('lot_id', '=', vals.get('lot_id'))], limit=1)
#                 if lines:
#                     raise ValidationError('You can not use lot/serial number which are already used earlier!')
#         return super(StockMoveLine, self).write(vals)
